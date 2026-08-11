"""Endpunkte für die Demo-Daten-Verwaltung in der Vereinskonfiguration."""

import frappe

from dms_verein import setup_demo
from dms_verein.api.verein import ADMIN_ROLLEN, _notify


@frappe.whitelist()
def demo_status():
    """Liegen Demo-Daten vor? Steuert die Buttons in der Oberfläche."""
    frappe.only_for(ADMIN_ROLLEN)
    return setup_demo.status()


@frappe.whitelist()
def demo_anlegen():
    """Legt den Demo-Datenbestand an (Sparten, Mitglieder, Vorstand, Termine ...)."""
    frappe.only_for(ADMIN_ROLLEN)
    ergebnis = setup_demo.demo_daten_anlegen()
    _notify("Demo", "insert")
    return ergebnis


@frappe.whitelist()
def demo_entfernen():
    """Entfernt ausschließlich die Datensätze, die die Demo angelegt hat."""
    frappe.only_for(ADMIN_ROLLEN)
    ergebnis = setup_demo.demo_daten_entfernen()
    _notify("Demo", "delete")
    return ergebnis
