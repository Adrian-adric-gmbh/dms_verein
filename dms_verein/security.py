import base64
import binascii
import hmac
import os

import frappe


HEALTH_PATH = "/api/method/dms_verein.api.health.check"


def enforce_internal_access():
	"""Optional second access barrier for dynamic Frappe requests.

	A reverse proxy must remain the primary barrier because static assets may be
	served without reaching Frappe. Outgoing mail and background jobs do not pass
	through this request hook.
	"""
	password = os.environ.get("DMS_INTERNAL_ACCESS_PASSWORD", "")
	if not password:
		return

	request = frappe.local.request
	if request.path == HEALTH_PATH or request.method == "OPTIONS":
		return

	username = os.environ.get("DMS_INTERNAL_ACCESS_USER", "verein")
	authorization = request.headers.get("Authorization", "")
	provided_user = ""
	provided_password = ""
	if authorization.startswith("Basic "):
		try:
			decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
			provided_user, provided_password = decoded.split(":", 1)
		except (binascii.Error, UnicodeDecodeError, ValueError):
			pass

	valid = hmac.compare_digest(provided_user, username) and hmac.compare_digest(provided_password, password)
	if valid:
		return

	frappe.local.response["http_status_code"] = 401
	frappe.local.response["headers"] = {"WWW-Authenticate": 'Basic realm="Vereinsverwaltung"'}
	raise frappe.AuthenticationError("Interner Zugang erforderlich.")