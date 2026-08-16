app_name = "dms_verein"
app_title = "Vereinsverwaltung"
app_publisher = "Sascha Böhm"
app_description = "Vereins- und Mitgliederverwaltung"
app_email = "service@industrie-4-0.org"
app_license = "mit"

# TEMP-DEBUG: Diagnose fuer "Module {} not found" beim Request-Bootstrap.
# Wird entfernt, sobald die Ursache gefunden ist.
def _install_temp_debug_patch():
	import sys

	if getattr(sys.modules[__name__], "_debug_patch_installed", False):
		return
	import frappe.modules.utils as _mod_utils

	_orig_get_module_app = _mod_utils.get_module_app

	def _debug_get_module_app(module):
		try:
			return _orig_get_module_app(module)
		except Exception:
			print(f"=== TEMP-DEBUG get_module_app FAILED for module={module!r} ===", flush=True)
			import traceback
			traceback.print_stack()
			raise

	_mod_utils.get_module_app = _debug_get_module_app
	sys.modules[__name__]._debug_patch_installed = True


try:
	_install_temp_debug_patch()
except Exception as _e:
	print(f"=== TEMP-DEBUG patch install failed: {_e!r} ===", flush=True)

fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Vereins Admin", "Kassenwart", "Spartenleiter", "Vorstand", "Mitglied", "Blogger"
    ]]]},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dms_verein/css/dms_verein.css"
# app_include_js = "/assets/dms_verein/js/dms_verein.js"

# include js, css files in header of web template
# web_include_css = "/assets/dms_verein/css/dms_verein.css"
# web_include_js = "/assets/dms_verein/js/dms_verein.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dms_verein/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "dms_verein/public/icons.svg"

# Website Routing
# ---------------

# Das Mitgliederportal ist eine Vue-SPA mit History-Mode und der Basis "/verein"
# (siehe frontend/src/router/index.js). Ohne diese Regel liefert Frappe nur
# "/verein" aus; jeder Reload, Bookmark oder geteilte Link auf eine Unterroute
# wie /verein/portal, /verein/admin oder /verein/produkt landet im 404.
# Die Regel leitet alles unterhalb von /verein auf die Seite www/verein.html,
# das Routing uebernimmt danach der Vue-Router im Browser.
website_route_rules = [
    {"from_route": "/verein/<path:app_path>", "to_route": "verein"},
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# Mitglieder, die sich ueber Frappes eigene Login-Seite anmelden, landen sonst
# im Desk, mit dem sie nichts anfangen koennen. Ueber die SPA-Anmeldung unter
# /verein/login greift diese Regel nicht -- dort routet LoginView.vue selbst.
role_home_page = {
    "Mitglied": "verein/portal",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "dms_verein.utils.jinja_methods",
# 	"filters": "dms_verein.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "dms_verein.install.before_install"
# after_install = "dms_verein.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "dms_verein.uninstall.before_uninstall"
# after_uninstall = "dms_verein.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "dms_verein.utils.before_app_install"
# after_app_install = "dms_verein.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "dms_verein.utils.before_app_uninstall"
# after_app_uninstall = "dms_verein.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "dms_verein.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config
# Muss definiert bleiben (auch leer): fehlt dieser Hook in ALLEN installierten
# Apps, ist "hooks.notification_config" None und frappe.desk.notifications
# bricht mit TypeError ab (Frappe-Core-Bug, siehe notifications.py).
notification_config = "dms_verein.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"dms_verein.tasks.all"
# 	],
# 	"daily": [
# 		"dms_verein.tasks.daily"
# 	],
# 	"hourly": [
# 		"dms_verein.tasks.hourly"
# 	],
# 	"weekly": [
# 		"dms_verein.tasks.weekly"
# 	],
# 	"monthly": [
# 		"dms_verein.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "dms_verein.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "dms_verein.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dms_verein.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dms_verein.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["dms_verein.security.enforce_internal_access"]
# after_request = ["dms_verein.utils.after_request"]

# Job Events
# ----------
# before_job = ["dms_verein.utils.before_job"]
# after_job = ["dms_verein.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"dms_verein.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

