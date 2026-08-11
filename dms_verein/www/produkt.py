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
    context.og_url = f"{base_url}/produkt"
    context.og_image = f"{base_url}/assets/dms_verein/screenshots/og_preview.jpg"
    return context
