import frappe


def get_notification_config():
	"""Leerer Desk-Notification-Hook.

	Verhindert einen Frappe-Core-Bug: frappe.desk.notifications.get_notification_config
	iteriert "for notification_config in hooks.notification_config" ohne Pruefung auf None.
	Definiert KEINE App diesen Hook, ist hooks.notification_config None -> TypeError,
	was "bench migrate" bei jedem Start abbrechen liess.
	"""
	return frappe._dict()
