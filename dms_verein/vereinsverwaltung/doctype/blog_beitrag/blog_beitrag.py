import re
import frappe
from frappe.model.document import Document


class BlogBeitrag(Document):
    def before_insert(self):
        if not self.slug:
            self.slug = self._generate_slug(self.titel)
        if not self.autor:
            self.autor = frappe.session.user
        if self.status == "Veröffentlicht" and not self.veroeffentlicht_am:
            self.veroeffentlicht_am = frappe.utils.today()

    def _generate_slug(self, titel):
        s = titel.lower()
        s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:80]
