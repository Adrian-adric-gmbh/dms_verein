import frappe


@frappe.whitelist(allow_guest=True)
def check():
	return {"status": "ok"}