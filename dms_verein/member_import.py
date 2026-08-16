import csv
import hashlib
import io
import re
from datetime import datetime


MAX_IMPORT_ROWS = 5000
VALID_STATUSES = {"Aktiv", "Passiv", "Gesperrt", "Ausgetreten", "Verstorben"}
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")

ALIASES = {
	"externe_id": "externe_id",
	"externe id": "externe_id",
	"mitgliedsnummer": "mitgliedsnummer",
	"anrede": "anrede",
	"vorname": "vorname",
	"nachname": "nachname",
	"geburtsdatum": "geburtsdatum",
	"geschlecht": "geschlecht",
	"strasse": "strasse",
	"strasse hausnummer": "strasse",
	"hausnummer": "hausnummer",
	"plz": "plz",
	"ort": "ort",
	"land": "land",
	"email": "email",
	"e mail": "email",
	"telefon": "telefon",
	"mobil": "mobil",
	"mitgliedstyp": "mitgliedstyp",
	"eintrittsdatum": "eintrittsdatum",
	"status": "status",
	"iban": "iban",
	"bic": "bic",
	"bank_name": "bank_name",
	"bank": "bank_name",
	"abteilung": "abteilungen",
	"abteilungen": "abteilungen",
	"abteilungszugehoerigkeit": "abteilungen",
	"sparte": "abteilungen",
	"sparten": "abteilungen",
	"familienstamm": "abteilungen",
	"familienstaemme": "abteilungen",
	"stamm": "abteilungen",
	"staemme": "abteilungen",
}

IMPORT_FIELDS = {
	"externe_id", "mitgliedsnummer", "anrede", "vorname", "nachname",
	"geburtsdatum", "geschlecht", "strasse", "hausnummer", "plz", "ort",
	"land", "email", "telefon", "mobil", "mitgliedstyp", "eintrittsdatum",
	"status", "iban", "bic", "bank_name",
}
REQUIRED_FIELDS = {
	"vorname", "nachname", "strasse", "plz", "ort",
	"mitgliedstyp", "eintrittsdatum",
}


class MemberImportError(ValueError):
	pass


def _normalize_header(value):
	value = (value or "").strip().lower()
	value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
	return re.sub(r"[^a-z0-9_]+", " ", value).strip()


def _normalize_date(value):
	if not value:
		return ""
	for date_format in DATE_FORMATS:
		try:
			return datetime.strptime(value, date_format).date().isoformat()
		except ValueError:
			continue
	raise MemberImportError(f"Ungültiges Datum: {value}")


def _normalize_email(value):
	value = value.strip().lower()
	if value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
		raise MemberImportError(f"Ungültige E-Mail-Adresse: {value}")
	return value


def _normalize_iban(value):
	iban = re.sub(r"\s+", "", value).upper()
	if not iban:
		return ""
	if not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}", iban):
		raise MemberImportError("IBAN hat ein ungültiges Format.")
	rearranged = iban[4:] + iban[:4]
	numeric = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
	if int(numeric) % 97 != 1:
		raise MemberImportError("IBAN-Prüfsumme ist ungültig.")
	return iban


def _generate_external_id(row):
	if row.get("externe_id"):
		return row["externe_id"]
	if row.get("mitgliedsnummer"):
		return row["mitgliedsnummer"]
	identity = "|".join(
		(row.get(field) or "").strip().lower()
		for field in ("vorname", "nachname", "geburtsdatum", "email")
	)
	return f"IMPORT-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16].upper()}"


def _normalize_departments(value):
	departments = []
	for department in re.split(r"[|,]", value or ""):
		department = department.strip()
		if department and department not in departments:
			departments.append(department)
	return departments


def parse_member_csv(content):
	if not isinstance(content, str) or not content.strip():
		raise MemberImportError("Die CSV-Datei ist leer.")

	sample = content[:4096]
	try:
		dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
		delimiter = None
	except csv.Error:
		dialect = csv.excel
		delimiter = ";"

	reader_options = {"delimiter": delimiter} if delimiter else {}
	reader = csv.DictReader(io.StringIO(content), dialect=dialect, **reader_options)
	if not reader.fieldnames:
		raise MemberImportError("Die CSV-Datei enthält keine Kopfzeile.")

	field_map = {}
	for source_name in reader.fieldnames:
		normalized = _normalize_header(source_name)
		canonical = ALIASES.get(normalized)
		if canonical:
			field_map[source_name] = canonical

	missing_headers = REQUIRED_FIELDS - set(field_map.values())
	if missing_headers:
		raise MemberImportError(f"Pflichtspalten fehlen: {', '.join(sorted(missing_headers))}")

	rows = []
	errors = []
	for line_number, source_row in enumerate(reader, start=2):
		if not any((value or "").strip() for value in source_row.values()):
			continue
		if line_number - 1 > MAX_IMPORT_ROWS:
			raise MemberImportError(f"Maximal {MAX_IMPORT_ROWS} Datensätze pro Import sind erlaubt.")
		row = {target: (source_row.get(source) or "").strip() for source, target in field_map.items()}
		row["_zeile"] = line_number
		try:
			missing_values = [field for field in REQUIRED_FIELDS if not row.get(field)]
			if missing_values:
				raise MemberImportError(f"Pflichtwerte fehlen: {', '.join(sorted(missing_values))}")
			row["geburtsdatum"] = _normalize_date(row.get("geburtsdatum", ""))
			row["eintrittsdatum"] = _normalize_date(row["eintrittsdatum"])
			row["email"] = _normalize_email(row.get("email", ""))
			row["externe_id"] = _generate_external_id(row)
			row["abteilungen"] = _normalize_departments(row.get("abteilungen", ""))
			row["iban"] = _normalize_iban(row.get("iban", ""))
			row["bic"] = row.get("bic", "").replace(" ", "").upper()
			if row["bic"] and not re.fullmatch(r"[A-Z0-9]{8}([A-Z0-9]{3})?", row["bic"]):
				raise MemberImportError("BIC hat ein ungültiges Format.")
			row["status"] = row.get("status") or "Aktiv"
			if row["status"] not in VALID_STATUSES:
				raise MemberImportError(f"Ungültiger Status: {row['status']}")
			row["land"] = row.get("land") or "Deutschland"
			rows.append(row)
		except MemberImportError as error:
			errors.append({"zeile": line_number, "externe_id": row.get("externe_id", ""), "meldung": str(error)})

	if not rows and not errors:
		raise MemberImportError("Die CSV-Datei enthält keine Datensätze.")
	return rows, errors