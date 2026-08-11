import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class Mitgliedsantrag(Document):
    def before_insert(self):
        self.eingangsdatum = now_datetime()
        self.vollstaendiger_name = f"{self.vorname} {self.nachname}"

    def annehmen(self):
        """Antrag annehmen und Mitglied erstellen."""
        if self.status == "Angenommen":
            frappe.throw("Antrag wurde bereits angenommen.")

        mitglied = frappe.new_doc("Mitglied")
        mitglied.vorname = self.vorname
        mitglied.nachname = self.nachname
        mitglied.anrede = self.anrede
        mitglied.geburtsdatum = self.geburtsdatum
        mitglied.geschlecht = self.geschlecht
        mitglied.strasse = self.strasse
        mitglied.plz = self.plz
        mitglied.ort = self.ort
        mitglied.email = self.email
        mitglied.telefon = self.telefon
        mitglied.mobil = self.mobil
        mitglied.mitgliedstyp = self.gewuenschter_mitgliedstyp
        mitglied.eintrittsdatum = frappe.utils.today()
        mitglied.status = "Aktiv"

        if self.iban:
            mitglied.iban = self.iban
            mitglied.bic = self.bic
            mitglied.bank_name = ""

        mitglied.insert(ignore_permissions=True)

        if self.sparte_wunsch:
            sparte = frappe.get_doc("Sparte", self.sparte_wunsch)
            sparte.append("mitglieder", {
                "mitglied": mitglied.name,
                "von": frappe.utils.today(),
                "aktiv": 1,
            })
            sparte.save(ignore_permissions=True)

        self.status = "Angenommen"
        self.mitglied_erstellt = mitglied.name
        self.bearbeitungsdatum = now_datetime()
        self.bearbeitet_von = frappe.session.user
        self.save(ignore_permissions=True)

        # Willkommens-E-Mail senden
        if self.email:
            try:
                verein_name = frappe.db.get_single_value("Vereins Konfiguration", "vereinsname") or "Ihrem Verein"
                frappe.sendmail(
                    recipients=[self.email],
                    subject=f"Willkommen bei {verein_name}!",
                    message=f"""
<p>Liebe/r {self.vorname} {self.nachname},</p>
<p>wir freuen uns, Sie als neues Mitglied bei <strong>{verein_name}</strong> begrüßen zu dürfen!</p>
<p>Ihr Mitgliedsantrag wurde geprüft und angenommen. Ihre Mitgliedsnummer lautet: <strong>{mitglied.name}</strong></p>
<p>Falls Sie noch kein Konto im Mitgliederportal haben, wenden Sie sich bitte an den Vereinsvorstand.</p>
<p>Mit freundlichen Grüßen<br>Der Vereinsvorstand</p>
""",
                    delayed=False,
                )
            except Exception:
                pass  # E-Mail-Fehler darf Antrag-Annahme nicht blockieren

        return mitglied.name

    def ablehnen(self, grund=""):
        self.status = "Abgelehnt"
        self.bearbeitungsdatum = now_datetime()
        self.bearbeitet_von = frappe.session.user
        if grund:
            self.bearbeitungsnotiz = grund
        self.save(ignore_permissions=True)

        # Ablehnungs-E-Mail senden
        if self.email:
            try:
                verein_name = frappe.db.get_single_value("Vereins Konfiguration", "vereinsname") or "unserem Verein"
                grund_text = f"<p><strong>Begründung:</strong> {grund}</p>" if grund else ""
                frappe.sendmail(
                    recipients=[self.email],
                    subject=f"Ihr Mitgliedsantrag bei {verein_name}",
                    message=f"""
<p>Liebe/r {self.vorname} {self.nachname},</p>
<p>vielen Dank für Ihr Interesse an einer Mitgliedschaft bei <strong>{verein_name}</strong>.</p>
<p>Nach Prüfung Ihres Antrags müssen wir Ihnen leider mitteilen, dass wir Ihren Antrag zum aktuellen Zeitpunkt nicht annehmen können.</p>
{grund_text}
<p>Bei Fragen wenden Sie sich gerne direkt an den Vereinsvorstand.</p>
<p>Mit freundlichen Grüßen<br>Der Vereinsvorstand</p>
""",
                    delayed=False,
                )
            except Exception:
                pass
