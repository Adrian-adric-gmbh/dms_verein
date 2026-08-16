import frappe
from frappe.model.document import Document


class Mitglied(Document):
    def before_save(self):
        self.vollstaendiger_name = f"{self.vorname} {self.nachname}"
        if not self.mitgliedsnummer and self.name and not self.name.startswith("new-"):
            self.mitgliedsnummer = self.name

    def validate(self):
        if not self.portal_benutzer:
            return
        existing = frappe.db.exists(
            "Mitglied",
            {"portal_benutzer": self.portal_benutzer, "name": ["!=", self.name]},
        )
        if existing:
            frappe.throw("Der Portal-Benutzer ist bereits mit einem anderen Mitglied verknüpft.")

    def after_insert(self):
        if not self.mitgliedsnummer:
            self.mitgliedsnummer = self.name
        self._add_mitgliedschaft_eintrag()

    def _add_mitgliedschaft_eintrag(self):
        if not self.mitgliedschaften:
            self.append("mitgliedschaften", {
                "mitgliedstyp": self.mitgliedstyp,
                "von": self.eintrittsdatum,
                "status": "Aktiv",
            })
            self.save(ignore_permissions=True)
