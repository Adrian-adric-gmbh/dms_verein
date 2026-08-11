import frappe
import json

no_cache = 1


def get_context(context):
    user = frappe.session.user
    if user == "Guest":
        context.rollen_json = "[]"
    else:
        rollen = frappe.get_roles(user)
        context.rollen_json = json.dumps(rollen)

    base_url = frappe.utils.get_url()
    path = frappe.request.path if frappe.request else ""

    if path.rstrip("/") == "/verein/produkt":
        context.og_title = "DMS Verein – Die digitale Vereinsplattform"
        context.og_description = (
            "Mitgliederverwaltung, interner Chat (E2E-verschlüsselt), Finanzen, "
            "SEPA-Lastschrift und ein mobiles Mitgliederportal – alles in einer Plattform. "
            "Für Vereine, Feuerwehren und mehr."
        )
        context.og_image = f"{base_url}/assets/dms_verein/screenshots/og_preview.jpg"
        context.og_url = f"{base_url}/verein/produkt"
        context.is_produkt_page = True
    else:
        context.is_produkt_page = False

    return context
