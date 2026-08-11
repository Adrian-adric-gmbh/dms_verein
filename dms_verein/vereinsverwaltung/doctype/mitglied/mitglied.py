import frappe
from frappe.model.document import Document


class Mitglied(Document):
    def before_save(self):
        self.vollstaendiger_name = f"{self.vorname} {self.nachname}"

    def after_insert(self):
        self._add_mitgliedschaft_eintrag()

    def _add_mitgliedschaft_eintrag(self):
        if not self.mitgliedschaften:
            self.append("mitgliedschaften", {
                "mitgliedstyp": self.mitgliedstyp,
                "von": self.eintrittsdatum,
                "status": "Aktiv",
            })
            self.save(ignore_permissions=True)
