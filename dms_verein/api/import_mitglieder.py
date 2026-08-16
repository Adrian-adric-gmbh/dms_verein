import hashlib
import json

import frappe
from frappe.utils import cint, now_datetime

from dms_verein.member_import import IMPORT_FIELDS, MemberImportError, parse_member_csv


ADMIN_ROLLEN = ["Vereins Admin", "System Manager"]
MAX_FILE_SIZE = 2 * 1024 * 1024


def _require_admin():
	frappe.only_for(ADMIN_ROLLEN)


def _load_private_file(file_url):
	files = frappe.get_all(
		"File",
		filters={"file_url": file_url, "is_private": 1},
		fields=["name", "file_name", "file_url", "file_size"],
		limit_page_length=1,
	)
	if not files:
		frappe.throw("Die Importdatei wurde nicht als private Datei gefunden.")
	file_info = files[0]
	if cint(file_info.file_size) > MAX_FILE_SIZE:
		frappe.throw("Die Importdatei darf maximal 2 MB groß sein.")
	content = frappe.get_doc("File", file_info.name).get_content()
	if isinstance(content, bytes):
		try:
			content = content.decode("utf-8-sig")
		except UnicodeDecodeError:
			frappe.throw("Die CSV-Datei muss UTF-8-kodiert sein.")
	return file_info, content


def _analyse(rows, parser_errors, create_portal_users=False):
	errors = list(parser_errors)
	seen_external_ids = set()
	member_types = set(frappe.get_all("Mitgliedstyp", pluck="name"))
	departments = set(frappe.get_all("Sparte", pluck="name"))
	external_ids = [row["externe_id"] for row in rows]
	existing_members = {
		row.externe_id: row
		for row in frappe.get_all(
			"Mitglied",
			filters={"externe_id": ["in", external_ids]},
			fields=["name", "externe_id", "mitgliedsnummer", "email"],
			limit_page_length=5000,
		)
	} if external_ids else {}
	member_numbers = [row.get("mitgliedsnummer") for row in rows if row.get("mitgliedsnummer")]
	existing_numbers = {
		row.mitgliedsnummer: row.name
		for row in frappe.get_all(
			"Mitglied",
			filters={"mitgliedsnummer": ["in", member_numbers]},
			fields=["name", "mitgliedsnummer"],
			limit_page_length=5000,
		)
	} if member_numbers else {}
	portal_links = {}
	if create_portal_users:
		emails = [row.get("email") for row in rows if row.get("email")]
		portal_links = {
			row.portal_benutzer: row.name
			for row in frappe.get_all(
				"Mitglied",
				filters={"portal_benutzer": ["in", emails]},
				fields=["name", "portal_benutzer"],
				limit_page_length=5000,
			)
		} if emails else {}

	valid_rows = []
	for row in rows:
		row_errors = []
		external_id = row["externe_id"]
		if external_id in seen_external_ids:
			row_errors.append("Externe ID kommt in der Datei mehrfach vor.")
		seen_external_ids.add(external_id)
		if row["mitgliedstyp"] not in member_types:
			row_errors.append(f"Mitgliedstyp existiert nicht: {row['mitgliedstyp']}")
		unknown_departments = [department for department in row["abteilungen"] if department not in departments]
		if unknown_departments:
			structure_name = frappe.db.get_single_value("Vereins Konfiguration", "struktur_singular") or "Sparte"
			row_errors.append(f"{structure_name} existiert nicht: {', '.join(unknown_departments)}")
		member_number = row.get("mitgliedsnummer")
		if member_number and member_number in existing_numbers and external_id not in existing_members:
			row_errors.append(f"Mitgliedsnummer ist bereits vergeben: {member_number}")
		if create_portal_users and not row.get("email"):
			row_errors.append("Für einen Portal-Benutzer ist eine E-Mail-Adresse erforderlich.")
		if create_portal_users and row.get("email") in portal_links and external_id not in existing_members:
			row_errors.append(f"E-Mail ist bereits mit einem Mitglied verknüpft: {row['email']}")
		for message in row_errors:
			errors.append({"zeile": row["_zeile"], "externe_id": external_id, "meldung": message})
		if not row_errors:
			valid_rows.append(row)

	return {
		"gesamt": len(rows) + len(parser_errors),
		"gueltig": len(valid_rows),
		"vorhanden": sum(1 for row in valid_rows if row["externe_id"] in existing_members),
		"neu": sum(1 for row in valid_rows if row["externe_id"] not in existing_members),
		"fehleranzahl": len(errors),
		"fehler": errors[:200],
		"vorschau": valid_rows[:25],
		"rows": valid_rows,
		"existing_members": existing_members,
	}


@frappe.whitelist()
def validate_import(file_url, portal_benutzer_anlegen=0, willkommensmail_senden=0):
	_require_admin()
	file_info, content = _load_private_file(file_url)
	try:
		rows, parser_errors = parse_member_csv(content)
	except MemberImportError as error:
		frappe.throw(str(error))
	analysis = _analyse(rows, parser_errors, cint(portal_benutzer_anlegen))
	report = {key: value for key, value in analysis.items() if key not in {"rows", "existing_members"}}

	batch = frappe.new_doc("Mitgliederimport")
	batch.status = "Validiert" if not report["fehleranzahl"] else "Validierung fehlgeschlagen"
	batch.datei = file_info.file_url
	batch.dateiname = file_info.file_name
	batch.datei_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
	batch.gesamt = report["gesamt"]
	batch.gueltig = report["gueltig"]
	batch.vorhanden = report["vorhanden"]
	batch.fehleranzahl = report["fehleranzahl"]
	batch.portal_benutzer_anlegen = cint(portal_benutzer_anlegen)
	batch.willkommensmail_senden = cint(willkommensmail_senden) if cint(portal_benutzer_anlegen) else 0
	batch.bericht = json.dumps(report, ensure_ascii=False, default=str)
	batch.gestartet_von = frappe.session.user
	batch.insert(ignore_permissions=True)
	return {"batch": batch.name, "status": batch.status, **report}


@frappe.whitelist()
def start_import(batch_name):
	_require_admin()
	batch = frappe.get_doc("Mitgliederimport", batch_name)
	if batch.status != "Validiert" or batch.fehleranzahl:
		frappe.throw("Nur ein fehlerfrei validierter Import kann gestartet werden.")
	batch.status = "Eingeplant"
	batch.gestartet_am = now_datetime()
	batch.save(ignore_permissions=True)
	frappe.enqueue(
		"dms_verein.api.import_mitglieder.run_import",
		queue="long",
		enqueue_after_commit=True,
		batch_name=batch.name,
	)
	return {"batch": batch.name, "status": batch.status}


@frappe.whitelist()
def get_import_status(batch_name):
	_require_admin()
	batch = frappe.get_doc("Mitgliederimport", batch_name)
	report = json.loads(batch.bericht or "{}")
	return {
		"batch": batch.name,
		"status": batch.status,
		"gesamt": batch.gesamt,
		"importiert": batch.importiert,
		"vorhanden": batch.vorhanden,
		"fehleranzahl": batch.fehleranzahl,
		"bericht": report,
	}


def _create_portal_user(member, send_welcome):
	if not member.email:
		return
	if frappe.db.exists("User", member.email):
		user = frappe.get_doc("User", member.email)
	else:
		user = frappe.new_doc("User")
		user.email = member.email
		user.first_name = member.vorname or ""
		user.last_name = member.nachname or ""
		user.enabled = 1
		user.user_type = "Website User"
		user.send_welcome_email = cint(send_welcome)
	if "Mitglied" not in {role.role for role in user.roles}:
		user.append("roles", {"role": "Mitglied"})
	if user.is_new():
		user.insert(ignore_permissions=True)
	else:
		user.save(ignore_permissions=True)
	member.portal_benutzer = member.email
	member.portal_aktiv = 1
	member.save(ignore_permissions=True)


def _assign_departments(member, departments, since):
	for department_name in departments:
		department = frappe.get_doc("Sparte", department_name)
		if any(row.mitglied == member.name and row.aktiv for row in department.mitglieder):
			continue
		department.append("mitglieder", {
			"mitglied": member.name,
			"von": since,
			"aktiv": 1,
		})
		department.save(ignore_permissions=True)


def run_import(batch_name):
	try:
		_run_import(batch_name)
	except Exception as error:
		frappe.db.rollback()
		batch = frappe.get_doc("Mitgliederimport", batch_name)
		batch.status = "Fehlgeschlagen"
		batch.fehleranzahl = max(cint(batch.fehleranzahl), 1)
		batch.bericht = json.dumps({"fehler": [{"meldung": str(error)}]}, ensure_ascii=False)
		batch.abgeschlossen_am = now_datetime()
		batch.save(ignore_permissions=True)
		frappe.db.commit()
		frappe.log_error(title=f"Mitgliederimport {batch_name} fehlgeschlagen", message=frappe.get_traceback())


def _run_import(batch_name):
	batch = frappe.get_doc("Mitgliederimport", batch_name)
	batch.status = "Wird importiert"
	batch.save(ignore_permissions=True)
	frappe.db.commit()

	_file_info, content = _load_private_file(batch.datei)
	if hashlib.sha256(content.encode("utf-8")).hexdigest() != batch.datei_hash:
		batch.status = "Fehlgeschlagen"
		batch.bericht = json.dumps({"fehler": [{"meldung": "Die Importdatei wurde nach der Validierung verändert."}]})
		batch.save(ignore_permissions=True)
		frappe.db.commit()
		return

	rows, parser_errors = parse_member_csv(content)
	analysis = _analyse(rows, parser_errors, batch.portal_benutzer_anlegen)
	if analysis["fehleranzahl"]:
		batch.status = "Fehlgeschlagen"
		batch.fehleranzahl = analysis["fehleranzahl"]
		batch.bericht = json.dumps({"fehler": analysis["fehler"]}, ensure_ascii=False)
		batch.save(ignore_permissions=True)
		frappe.db.commit()
		return

	imported = 0
	errors = []
	for index, row in enumerate(analysis["rows"], start=1):
		if row["externe_id"] in analysis["existing_members"]:
			continue
		save_point = f"mitglied_import_{index}"
		frappe.db.savepoint(save_point)
		try:
			member = frappe.new_doc("Mitglied")
			for field in IMPORT_FIELDS - {"_zeile"}:
				if field in row and row[field] != "":
					member.set(field, row[field])
			if not member.mitgliedsnummer:
				member.mitgliedsnummer = member.externe_id
			member.insert(ignore_permissions=True)
			if row["abteilungen"]:
				_assign_departments(member, row["abteilungen"], member.eintrittsdatum)
			if batch.portal_benutzer_anlegen:
				_create_portal_user(member, batch.willkommensmail_senden)
			imported += 1
		except Exception as error:
			frappe.db.rollback(save_point=save_point)
			errors.append({"zeile": row["_zeile"], "externe_id": row["externe_id"], "meldung": str(error)})
		if index % 100 == 0:
			frappe.db.commit()

	batch.importiert = imported
	batch.fehleranzahl = len(errors)
	batch.status = "Abgeschlossen" if not errors else "Abgeschlossen mit Fehlern"
	batch.abgeschlossen_am = now_datetime()
	batch.bericht = json.dumps(
		{"importiert": imported, "vorhanden": analysis["vorhanden"], "fehler": errors[:200]},
		ensure_ascii=False,
	)
	batch.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.publish_realtime("dms_update", {"doctype": "Mitglied", "action": "bulk_import"}, room="all")