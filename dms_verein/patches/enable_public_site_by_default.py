import frappe


def execute():
	"""Neues Feld 'oeffentliche_seite_aktiv' auf bestehenden Installationen aktiv setzen.

	Frappe wendet den Schema-Default eines neuen Felds bei einem bereits vorhandenen
	Single-DocType nicht rückwirkend an -- ohne diesen Patch waere die oeffentliche
	Vereinsseite fuer alle bestehenden Installationen nach dem Update ungewollt aus.
	"""
	already_set = frappe.db.sql(
		"""SELECT 1 FROM `tabSingles` WHERE doctype=%s AND field=%s""",
		("Vereins Konfiguration", "oeffentliche_seite_aktiv"),
	)
	if not already_set:
		frappe.db.set_single_value("Vereins Konfiguration", "oeffentliche_seite_aktiv", 1)
