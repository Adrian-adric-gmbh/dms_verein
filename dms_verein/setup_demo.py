"""
Demo-Daten für dms_verein.

Aufruf über die Kommandozeile:
    bench --site <site> execute dms_verein.setup_demo.run
    bench --site <site> execute dms_verein.setup_demo.remove

Aus der Oberfläche heraus laufen dieselben Funktionen über
dms_verein.api.demo (Tab "Demo-Daten" in der Vereinskonfiguration).

Jeder angelegte Datensatz wird in der Vereins Konfiguration mitgeschrieben
(Feld demo_daten_index). Nur was dort steht, wird beim Entfernen gelöscht --
bereits vorhandene Datensätze fasst der Seeder nicht an und trägt sie auch
nicht ein. Damit kann das Entfernen keine echten Vereinsdaten treffen.
"""

import json

import frappe
from frappe.utils import add_days, add_months, now_datetime, today

KONFIG = "Vereins Konfiguration"

# Felder, die die Demo in der (einzelnen) Vereins Konfiguration setzt.
# Beim Entfernen werden genau diese wieder geleert.
DEMO_KONFIG_FELDER = [
    "vereinsname", "rechtsform", "gruendungsjahr", "vereinszweck",
    "strasse", "hausnummer", "plz", "ort", "bundesland",
    "telefon", "email", "website",
    "registernummer", "amtsgericht", "steuernummer", "gemeinnuetzig",
    "vertretung_vorstand",
    "bankname", "konto_inhaber", "iban", "bic",
    "sepa_glaeubiger_id", "sepa_mandatsreferenz_prefix",
    "primaerfarbe", "sekundaerfarbe", "vereinsmotto", "willkommenstext",
    "datenschutzbeauftragter", "datenschutz_email",
    "beitrag_faelligkeit", "beitrag_intervall",
]


# ─── Index: welche Datensätze gehören zur Demo? ─────────────────────────────

def _index_laden():
    roh = frappe.db.get_single_value(KONFIG, "demo_daten_index")
    if not roh:
        return []
    try:
        return json.loads(roh)
    except (ValueError, TypeError):
        return []


def _index_speichern(index):
    frappe.db.set_single_value(KONFIG, "demo_daten_index", json.dumps(index, ensure_ascii=False))
    frappe.db.set_single_value(KONFIG, "demo_daten_aktiv", 1 if index else 0)
    frappe.db.set_single_value(KONFIG, "demo_daten_erstellt", now_datetime() if index else None)


def status():
    """Kurzübersicht für die Oberfläche."""
    index = _index_laden()
    nach_doctype = {}
    for eintrag in index:
        if eintrag.get("single"):
            continue
        nach_doctype[eintrag["doctype"]] = nach_doctype.get(eintrag["doctype"], 0) + 1
    return {
        "aktiv": bool(index),
        "anzahl": sum(nach_doctype.values()),
        "nach_doctype": nach_doctype,
        # Ohne Demo-Daten kein Datum -- ein geleertes Datetime-Single liefert
        # sonst das Nulldatum zurück.
        "erstellt_am": frappe.db.get_single_value(KONFIG, "demo_daten_erstellt") if index else None,
        "konfiguration_von_demo": any(e.get("single") for e in index),
    }


def _neu(index, doctype, werte, schluessel=None):
    """Legt einen Datensatz an, sofern er noch nicht existiert.

    Nur wirklich neu angelegte Datensätze landen im Index -- fremde
    gleichnamige Daten bleiben dadurch beim Entfernen unangetastet.
    Gibt den Namen des Datensatzes zurück (auch wenn er schon existierte).
    """
    vorhanden = frappe.db.exists(doctype, schluessel) if schluessel else None
    if vorhanden:
        return vorhanden if isinstance(vorhanden, str) else vorhanden[0][0]
    doc = frappe.new_doc(doctype)
    doc.update(werte)
    doc.insert(ignore_permissions=True)
    index.append({"doctype": doctype, "name": doc.name})
    return doc.name


# ─── Anlegen ──────────────────────────────────────────────────────────────────

def demo_daten_anlegen():
    """Legt den kompletten Demo-Datenbestand an."""
    if _index_laden():
        frappe.throw("Es sind bereits Demo-Daten vorhanden. Bitte zuerst entfernen.")

    index = []
    _vereinsconfig(index)
    _mitgliedstypen(index)
    _vorstandspositionen(index)
    _sparten(index)
    mitglieder = _mitglieder(index)
    _spartenmitglieder(index, mitglieder)
    _vorstand(index, mitglieder)
    _sparten_termine(index)
    _veranstaltungen(index)
    _fotoalben(index)
    _antraege(index)

    _index_speichern(index)
    frappe.db.commit()
    return status()


def _vereinsconfig(index):
    if frappe.db.get_single_value(KONFIG, "vereinsname"):
        return
    doc = frappe.get_doc(KONFIG)
    doc.vereinsname = "TSV Musterstadt"
    doc.rechtsform = "e.V."
    doc.gruendungsjahr = 1952
    doc.vereinszweck = "Förderung des Sports und der körperlichen Ertüchtigung im Sinne des Breitensports."
    doc.strasse = "Sportplatzweg"
    doc.hausnummer = "12"
    doc.plz = "86150"
    doc.ort = "Augsburg"
    doc.bundesland = "Bayern"
    doc.telefon = "0821 123456"
    doc.email = "info@tsv-musterstadt.de"
    doc.website = "www.tsv-musterstadt.de"
    doc.registernummer = "VR 12345"
    doc.amtsgericht = "Amtsgericht Augsburg"
    doc.steuernummer = "108/123/45678"
    doc.gemeinnuetzig = 1
    doc.vertretung_vorstand = "Hans Müller (1. Vorsitzender), Maria Schmidt (2. Vorsitzende)"
    doc.bankname = "Sparkasse Augsburg"
    doc.konto_inhaber = "TSV Musterstadt e.V."
    doc.iban = "DE89370400440532013000"
    doc.bic = "COBADEFFXXX"
    doc.sepa_glaeubiger_id = "DE98ZZZ09999999999"
    doc.sepa_mandatsreferenz_prefix = "TSV-"
    doc.primaerfarbe = "#2563eb"
    doc.sekundaerfarbe = "#0f172a"
    doc.vereinsmotto = "Gemeinsam stark — seit 1952"
    doc.willkommenstext = (
        "Herzlich willkommen beim TSV Musterstadt! Wir freuen uns über Ihr Interesse an "
        "unserem Verein. Ob Sport, Gemeinschaft oder Engagement — bei uns ist jeder willkommen."
    )
    doc.datenschutzbeauftragter = "Dr. Klaus Weber"
    doc.datenschutz_email = "datenschutz@tsv-musterstadt.de"
    doc.beitrag_faelligkeit = "01.01."
    doc.beitrag_intervall = "Jährlich"
    doc.save(ignore_permissions=True)
    index.append({"doctype": KONFIG, "single": 1, "felder": DEMO_KONFIG_FELDER})


def _mitgliedstypen(index):
    typen = [
        {"bezeichnung": "Aktiv Erwachsene", "beitragsbetrag": 120, "zahlungsintervall": "Jährlich",
         "beschreibung": "Vollmitgliedschaft ab 18 Jahren mit Stimmrecht", "stimmberechtigt": 1, "farbe": "#2563eb"},
        {"bezeichnung": "Aktiv Jugend", "beitragsbetrag": 60, "zahlungsintervall": "Jährlich",
         "beschreibung": "Jugendmitgliedschaft bis 17 Jahre", "max_alter": 17, "stimmberechtigt": 0, "farbe": "#16a34a"},
        {"bezeichnung": "Passiv", "beitragsbetrag": 48, "zahlungsintervall": "Jährlich",
         "beschreibung": "Fördermitgliedschaft ohne aktive Sportteilnahme", "stimmberechtigt": 1, "farbe": "#9333ea"},
        {"bezeichnung": "Ehrenmitglied", "beitragsbetrag": 0, "zahlungsintervall": "Beitragsfrei",
         "beschreibung": "Ehrenmitgliedschaft für besondere Verdienste um den Verein", "stimmberechtigt": 1, "farbe": "#f59e0b"},
        {"bezeichnung": "Familie", "beitragsbetrag": 180, "zahlungsintervall": "Jährlich",
         "beschreibung": "Familienmitgliedschaft (Eltern + Kinder)", "stimmberechtigt": 1, "farbe": "#ef4444"},
    ]
    for t in typen:
        _neu(index, "Mitgliedstyp", dict(t, aktiv=1), t["bezeichnung"])


def _vorstandspositionen(index):
    positionen = [
        {"bezeichnung": "1. Vorsitzender/Vorsitzende", "rang": 1, "pflichtposition": 1},
        {"bezeichnung": "2. Vorsitzender/Vorsitzende", "rang": 2, "pflichtposition": 1},
        {"bezeichnung": "Kassenwart/Kassenwartin", "rang": 3, "pflichtposition": 1},
        {"bezeichnung": "Schriftführer/Schriftführerin", "rang": 4, "pflichtposition": 0},
        {"bezeichnung": "Jugendwart/Jugendwartin", "rang": 5, "pflichtposition": 0},
        {"bezeichnung": "Sportwart/Sportwartin", "rang": 6, "pflichtposition": 0},
    ]
    for p in positionen:
        _neu(index, "Vorstandsposition", dict(p, aktiv=1), p["bezeichnung"])


# Sparten mit Beitrag, Trainingszeiten und späterer Mitgliederzuordnung.
SPARTEN = [
    {"name_sparte": "Fußball", "icon": "⚽", "farbe": "#16a34a", "gruendungsjahr": 1952,
     "treffpunkt": "Hauptspielfeld, Sportplatzweg 12", "beitrag": 60, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Von der Bambini-Mannschaft bis zur Ü40 — Fußball ist die größte Sparte im Verein.</p>",
     "termine": [("Training Herren", "18:30:00", "20:00:00", "Wöchentlich", "Dienstag"),
                 ("Training Jugend", "17:00:00", "18:30:00", "Wöchentlich", "Donnerstag")]},
    {"name_sparte": "Tennis", "icon": "🎾", "farbe": "#eab308", "gruendungsjahr": 1975,
     "treffpunkt": "Tennisanlage, Am Sportpark 3", "beitrag": 90, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Sechs Sandplätze, Punktspielbetrieb und ein aktives Vereinsleben.</p>",
     "termine": [("Freies Spiel", "16:00:00", "20:00:00", "Wöchentlich", "Mittwoch")]},
    {"name_sparte": "Schwimmen", "icon": "🏊", "farbe": "#0ea5e9", "gruendungsjahr": 1968,
     "treffpunkt": "Hallenbad Musterstadt", "beitrag": 72, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Schwimmkurse für Kinder, Technik-Training und Aquafitness.</p>",
     "termine": [("Anfängerschwimmen", "15:00:00", "16:00:00", "Wöchentlich", "Montag"),
                 ("Aquafitness", "19:00:00", "20:00:00", "Wöchentlich", "Montag")]},
    {"name_sparte": "Leichtathletik", "icon": "🏃", "farbe": "#f97316", "gruendungsjahr": 1960,
     "treffpunkt": "Tartanbahn, Sportplatzweg 12", "beitrag": 54, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Lauf, Sprung, Wurf — Training für alle Altersklassen.</p>",
     "termine": [("Lauftreff", "18:00:00", "19:30:00", "Wöchentlich", "Freitag")]},
    {"name_sparte": "Turnen", "icon": "🤸", "farbe": "#a855f7", "gruendungsjahr": 1955,
     "treffpunkt": "Gymnastikhalle, Sportplatzweg 12", "beitrag": 48, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Eltern-Kind-Turnen, Gerätturnen und Seniorengymnastik.</p>",
     "termine": [("Eltern-Kind-Turnen", "16:00:00", "17:00:00", "Wöchentlich", "Samstag")]},
    {"name_sparte": "Volleyball", "icon": "🏐", "farbe": "#ec4899", "gruendungsjahr": 1985,
     "treffpunkt": "Sporthalle Nord", "beitrag": 60, "beitrag_intervall": "Jährlich",
     "beschreibung": "<p>Hobby- und Ligamannschaft, gemischtes Training.</p>",
     "termine": [("Mixed-Training", "20:00:00", "22:00:00", "Wöchentlich", "Mittwoch")]},
]


def _sparten(index):
    for s in SPARTEN:
        werte = {k: v for k, v in s.items() if k != "termine"}
        _neu(index, "Sparte", dict(werte, aktiv=1), s["name_sparte"])


MITGLIEDER = [
    {"vorname": "Hans", "nachname": "Müller", "anrede": "Herr", "geburtsdatum": "1970-03-15",
     "strasse": "Hauptstraße 42", "plz": "86150", "ort": "Augsburg",
     "email": "hans.mueller@email.de", "telefon": "0821 112233", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "1990-01-01", "status": "Aktiv"},
    {"vorname": "Maria", "nachname": "Schmidt", "anrede": "Frau", "geburtsdatum": "1975-07-22",
     "strasse": "Blumenweg 8", "plz": "86153", "ort": "Augsburg",
     "email": "maria.schmidt@email.de", "telefon": "0821 445566", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "1998-03-15", "status": "Aktiv"},
    {"vorname": "Peter", "nachname": "Weber", "anrede": "Herr", "geburtsdatum": "1985-11-08",
     "strasse": "Ringstraße 15", "plz": "86156", "ort": "Augsburg",
     "email": "p.weber@email.de", "telefon": "0821 778899", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "2005-06-01", "status": "Aktiv"},
    {"vorname": "Anna", "nachname": "Fischer", "anrede": "Frau", "geburtsdatum": "2008-04-30",
     "strasse": "Lindenallee 3", "plz": "86150", "ort": "Augsburg",
     "email": "anna.fischer@email.de", "mitgliedstyp": "Aktiv Jugend",
     "eintrittsdatum": "2018-09-01", "status": "Aktiv"},
    {"vorname": "Karl", "nachname": "Bauer", "anrede": "Herr", "geburtsdatum": "1945-12-01",
     "strasse": "Alte Straße 77", "plz": "86159", "ort": "Augsburg",
     "email": "k.bauer@email.de", "mitgliedstyp": "Ehrenmitglied",
     "eintrittsdatum": "1965-01-01", "status": "Aktiv"},
    {"vorname": "Lisa", "nachname": "Hoffmann", "anrede": "Frau", "geburtsdatum": "1992-06-18",
     "strasse": "Neugasse 5", "plz": "86152", "ort": "Augsburg",
     "email": "l.hoffmann@email.de", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "2015-04-01", "status": "Aktiv"},
    {"vorname": "Thomas", "nachname": "Braun", "anrede": "Herr", "geburtsdatum": "1988-09-25",
     "strasse": "Parkweg 21", "plz": "86154", "ort": "Augsburg",
     "email": "t.braun@email.de", "mitgliedstyp": "Passiv",
     "eintrittsdatum": "2010-01-15", "status": "Aktiv"},
    {"vorname": "Sophie", "nachname": "Klein", "anrede": "Frau", "geburtsdatum": "2005-02-14",
     "strasse": "Gartenstraße 9", "plz": "86157", "ort": "Augsburg",
     "email": "sophie.klein@email.de", "mitgliedstyp": "Aktiv Jugend",
     "eintrittsdatum": "2019-09-01", "status": "Aktiv"},
    {"vorname": "Michael", "nachname": "Schäfer", "anrede": "Herr", "geburtsdatum": "1968-05-03",
     "strasse": "Bergstraße 44", "plz": "86161", "ort": "Augsburg",
     "email": "m.schaefer@email.de", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "1988-07-01", "status": "Aktiv"},
    {"vorname": "Julia", "nachname": "Wolf", "anrede": "Frau", "geburtsdatum": "1995-10-11",
     "strasse": "Sonnenweg 2", "plz": "86150", "ort": "Augsburg",
     "email": "j.wolf@email.de", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "2020-02-01", "status": "Aktiv"},
    {"vorname": "Daniel", "nachname": "Krause", "anrede": "Herr", "geburtsdatum": "1982-01-27",
     "strasse": "Feldweg 18", "plz": "86158", "ort": "Augsburg",
     "email": "d.krause@email.de", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "2008-05-01", "status": "Aktiv"},
    {"vorname": "Nina", "nachname": "Berger", "anrede": "Frau", "geburtsdatum": "1999-08-09",
     "strasse": "Am Anger 6", "plz": "86151", "ort": "Augsburg",
     "email": "n.berger@email.de", "mitgliedstyp": "Aktiv Erwachsene",
     "eintrittsdatum": "2021-09-01", "status": "Aktiv"},
]


def _mitglieder(index):
    """Legt die Mitglieder an und liefert {email: name} zurück."""
    namen = {}
    for m in MITGLIEDER:
        name = _neu(index, "Mitglied", dict(m, land="Deutschland"), {"email": m["email"]})
        namen[m["email"]] = name
    return namen


# Wer turnt wo mit? (Sparte -> Liste aus E-Mail + Funktion)
# Mehrfachmitgliedschaften sind Absicht: so sieht man in der Demo, dass ein
# Mitglied in mehreren Sparten aktiv sein kann.
SPARTEN_ZUORDNUNG = {
    "Fußball": [("hans.mueller@email.de", "Spartenleiter"), ("p.weber@email.de", "Stellvertreter"),
                ("m.schaefer@email.de", "Trainer Herren"), ("d.krause@email.de", ""),
                ("sophie.klein@email.de", ""), ("anna.fischer@email.de", "")],
    "Tennis": [("maria.schmidt@email.de", "Spartenleiterin"), ("l.hoffmann@email.de", "Stellvertreterin"),
               ("j.wolf@email.de", ""), ("t.braun@email.de", "")],
    "Schwimmen": [("l.hoffmann@email.de", "Spartenleiterin"), ("anna.fischer@email.de", ""),
                  ("n.berger@email.de", "Übungsleiterin")],
    "Leichtathletik": [("m.schaefer@email.de", "Spartenleiter"), ("sophie.klein@email.de", ""),
                       ("j.wolf@email.de", "")],
    "Turnen": [("j.wolf@email.de", "Spartenleiterin"), ("n.berger@email.de", ""),
               ("k.bauer@email.de", "Ehrenmitglied")],
    "Volleyball": [("d.krause@email.de", "Spartenleiter"), ("n.berger@email.de", "Stellvertreterin"),
                   ("p.weber@email.de", "")],
}

# Wer leitet die Sparte? (Sparte -> (Leitung, Stellvertretung) als E-Mail)
SPARTEN_LEITUNG = {
    "Fußball": ("hans.mueller@email.de", "p.weber@email.de"),
    "Tennis": ("maria.schmidt@email.de", "l.hoffmann@email.de"),
    "Schwimmen": ("l.hoffmann@email.de", "n.berger@email.de"),
    "Leichtathletik": ("m.schaefer@email.de", "sophie.klein@email.de"),
    "Turnen": ("j.wolf@email.de", "n.berger@email.de"),
    "Volleyball": ("d.krause@email.de", "n.berger@email.de"),
}


def _spartenmitglieder(index, mitglieder):
    """Ordnet Mitglieder den Sparten zu und setzt die Spartenleitung.

    Spartenmitglied ist eine Kindtabelle der Sparte -- die Zeilen verschwinden
    also automatisch mit der Sparte und brauchen keinen eigenen Index-Eintrag.
    """
    angelegte_sparten = {e["name"] for e in index if e.get("doctype") == "Sparte"}
    eintritt = add_months(today(), -18)
    for sparte_name, zuordnung in SPARTEN_ZUORDNUNG.items():
        if sparte_name not in angelegte_sparten:
            continue  # fremde Sparte gleichen Namens nicht anfassen
        doc = frappe.get_doc("Sparte", sparte_name)
        for email, funktion in zuordnung:
            if email not in mitglieder:
                continue
            doc.append("mitglieder", {
                "mitglied": mitglieder[email],
                "funktion": funktion,
                "von": eintritt,
                "aktiv": 1,
            })
        leitung, stellvertretung = SPARTEN_LEITUNG.get(sparte_name, (None, None))
        if leitung in mitglieder:
            doc.spartenleiter = mitglieder[leitung]
        if stellvertretung in mitglieder:
            doc.stellvertreter = mitglieder[stellvertretung]
        doc.save(ignore_permissions=True)


VORSTAND = [
    ("hans.mueller@email.de", "1. Vorsitzender/Vorsitzende", "vorsitz@tsv-musterstadt.de"),
    ("maria.schmidt@email.de", "2. Vorsitzender/Vorsitzende", "vorstand@tsv-musterstadt.de"),
    ("t.braun@email.de", "Kassenwart/Kassenwartin", "kasse@tsv-musterstadt.de"),
    ("l.hoffmann@email.de", "Schriftführer/Schriftführerin", "schriftfuehrung@tsv-musterstadt.de"),
    ("j.wolf@email.de", "Jugendwart/Jugendwartin", "jugend@tsv-musterstadt.de"),
    ("m.schaefer@email.de", "Sportwart/Sportwartin", "sport@tsv-musterstadt.de"),
]


def _vorstand(index, mitglieder):
    von = add_months(today(), -12)
    bis = add_months(today(), 12)
    for email, position, dienst_email in VORSTAND:
        if email not in mitglieder or not frappe.db.exists("Vorstandsposition", position):
            continue
        if frappe.db.exists("Vorstandsmitglied", {"mitglied": mitglieder[email], "position": position}):
            continue
        _neu(index, "Vorstandsmitglied", {
            "mitglied": mitglieder[email],
            "position": position,
            "amtsperiode_von": von,
            "amtsperiode_bis": bis,
            "aktiv": 1,
            "email_dienstlich": dienst_email,
        })


def _sparten_termine(index):
    """Wiederkehrende Trainingstermine je Sparte."""
    angelegte_sparten = {e["name"] for e in index if e.get("doctype") == "Sparte"}
    start = add_days(today(), 3)
    ende = add_months(today(), 6)
    for s in SPARTEN:
        if s["name_sparte"] not in angelegte_sparten:
            continue
        for titel, von, bis, wiederholung, wochentag in s["termine"]:
            _neu(index, "Sparten Termin", {
                "sparte": s["name_sparte"],
                "titel": titel,
                "datum": start,
                "uhrzeit_von": von,
                "uhrzeit_bis": bis,
                "treffpunkt": s["treffpunkt"],
                "wiederholung": wiederholung,
                "wiederholung_wochentag": wochentag,
                "wiederholung_bis": ende,
                "aktiv": 1,
            })


def _veranstaltungen(index):
    t = today()
    events = [
        {"titel": "Jahreshauptversammlung 2026", "kategorie": "Hauptversammlung",
         "datum_von": add_days(t, 14), "uhrzeit_von": "19:00:00",
         "veranstaltungsort": "Vereinsheim TSV Musterstadt", "status": "Bestätigt", "öffentlich": 1,
         "beschreibung": "<p>Jährliche Mitgliederversammlung mit Wahlen und Jahresrückblick.</p><p>Tagesordnung: 1. Begrüßung 2. Jahresbericht 3. Kassenbericht 4. Wahlen 5. Verschiedenes</p>"},
        {"titel": "Fußball-Turnier Sommer 2026", "kategorie": "Turnier",
         "datum_von": add_days(t, 21), "uhrzeit_von": "10:00:00",
         "veranstaltungsort": "Hauptspielfeld Sportplatzweg", "status": "Geplant", "öffentlich": 1,
         "anmeldung_erforderlich": 1, "max_teilnehmer": 80,
         "beschreibung": "<p>Das große Sommerturnier unserer Fußballsparte — alle Teams willkommen!</p>"},
        {"titel": "Vereinsfest 2026", "kategorie": "Fest",
         "datum_von": add_days(t, 35), "uhrzeit_von": "14:00:00",
         "datum_bis": add_days(t, 35), "uhrzeit_bis": "22:00:00",
         "veranstaltungsort": "Vereinsgelände", "status": "Geplant", "öffentlich": 1,
         "beschreibung": "<p>Unser jährliches Sommerfest mit Musik, Essen und Spaß für die ganze Familie!</p>"},
        {"titel": "Tennis-Anfängerkurs", "kategorie": "Training",
         "datum_von": add_days(t, 7), "uhrzeit_von": "16:00:00",
         "veranstaltungsort": "Tennisanlage Am Sportpark", "status": "Bestätigt", "öffentlich": 1,
         "max_teilnehmer": 12, "anmeldung_erforderlich": 1,
         "kosten_mitglieder": 25, "kosten_gaeste": 45,
         "beschreibung": "<p>6-wöchiger Anfängerkurs für Erwachsene. Material wird gestellt.</p>"},
        {"titel": "Schwimmabzeichen für Kinder", "kategorie": "Sonstige",
         "datum_von": add_days(t, 10), "uhrzeit_von": "09:00:00",
         "veranstaltungsort": "Hallenbad Musterstadt", "status": "Bestätigt", "öffentlich": 1,
         "beschreibung": "<p>Abnahme von Seepferdchen, Bronze, Silber und Gold.</p>"},
        {"titel": "Volleyball-Hobbyturnier", "kategorie": "Turnier",
         "datum_von": add_days(t, 28), "uhrzeit_von": "13:00:00",
         "veranstaltungsort": "Sporthalle Nord", "status": "Geplant", "öffentlich": 1,
         "anmeldung_erforderlich": 1, "max_teilnehmer": 48,
         "beschreibung": "<p>Mixed-Turnier für Hobbyteams — Anmeldung als Sechserteam.</p>"},
    ]
    for e in events:
        _neu(index, "Veranstaltung", e, {"titel": e["titel"]})


def _fotoalben(index):
    alben = [
        {"titel": "Vereinsfest 2025", "datum": "2025-07-20", "öffentlich": 1,
         "beschreibung": "Rückblick auf unser Sommerfest 2025"},
        {"titel": "Fußball-Meisterschaft 2025", "datum": "2025-05-15", "öffentlich": 1,
         "beschreibung": "Bilder von unserer erfolgreichen Saison"},
        {"titel": "Hauptversammlung 2025", "datum": "2025-03-10", "öffentlich": 0,
         "beschreibung": "Fotos von der Jahreshauptversammlung"},
        {"titel": "Tennis-Turnier Herbst 2025", "datum": "2025-09-28", "öffentlich": 1,
         "beschreibung": "Herbst-Turnier der Tennisabteilung"},
    ]
    for a in alben:
        _neu(index, "Fotoalbum", a, {"titel": a["titel"]})


def _antraege(index):
    antraege = [
        {"vorname": "Max", "nachname": "Mustermann", "anrede": "Herr",
         "geburtsdatum": "1990-06-15", "strasse": "Musterstr. 1", "plz": "86150", "ort": "Augsburg",
         "email": "max.mustermann@email.de", "telefon": "0821 999888",
         "gewuenschter_mitgliedstyp": "Aktiv Erwachsene", "sparte_wunsch": "Fußball",
         "datenschutz_akzeptiert": 1, "satzung_akzeptiert": 1, "beitragsordnung_akzeptiert": 1,
         "status": "Neu"},
        {"vorname": "Erika", "nachname": "Musterfrau", "anrede": "Frau",
         "geburtsdatum": "1998-11-30", "strasse": "Beispielweg 7", "plz": "86153", "ort": "Augsburg",
         "email": "erika.musterfrau@email.de",
         "gewuenschter_mitgliedstyp": "Aktiv Erwachsene", "sparte_wunsch": "Tennis",
         "sepa_gewuenscht": 1, "kontoinhaber": "Erika Musterfrau",
         "iban": "DE12500105170648489890",
         "datenschutz_akzeptiert": 1, "satzung_akzeptiert": 1, "beitragsordnung_akzeptiert": 1,
         "status": "In Prüfung"},
        {"vorname": "Jonas", "nachname": "Beispiel", "anrede": "Herr",
         "geburtsdatum": "2012-03-08", "strasse": "Schulweg 22", "plz": "86157", "ort": "Augsburg",
         "email": "jonas.beispiel@email.de",
         "gewuenschter_mitgliedstyp": "Aktiv Jugend", "sparte_wunsch": "Schwimmen",
         "datenschutz_akzeptiert": 1, "satzung_akzeptiert": 1, "beitragsordnung_akzeptiert": 1,
         "status": "Neu"},
    ]
    for a in antraege:
        _neu(index, "Mitgliedsantrag", a, {"email": a["email"]})


# ─── Entfernen ────────────────────────────────────────────────────────────────

def demo_daten_entfernen():
    """Entfernt genau die Datensätze, die die Demo angelegt hat."""
    index = _index_laden()
    if not index:
        frappe.throw("Es sind keine Demo-Daten hinterlegt.")

    einzeln = [e for e in index if e.get("single")]
    datensaetze = [e for e in index if not e.get("single")]

    geloescht = 0
    # Rückwärts durch den Index, damit abhängige Datensätze zuerst drankommen.
    # Das reicht aber nicht: eine Sparte entsteht vor den Mitgliedern, verweist
    # aber über Spartenleitung und Kindtabelle auf sie. Darum wird so lange
    # wiederholt, wie ein Durchlauf noch etwas löschen konnte.
    offen = list(reversed(datensaetze))
    zaehler = 0
    while offen:
        rest = []
        for eintrag in offen:
            doctype, name = eintrag["doctype"], eintrag["name"]
            if not frappe.db.exists(doctype, name):
                geloescht += 1
                continue
            # Savepoint, damit eine fehlgeschlagene Löschung die laufende
            # Transaktion nicht unbrauchbar macht.
            zaehler += 1
            sp = f"demo_del_{zaehler}"
            frappe.db.savepoint(sp)
            try:
                frappe.delete_doc(
                    doctype, name,
                    ignore_permissions=True,
                    delete_permanently=True,
                    ignore_missing=True,
                )
                geloescht += 1
            except Exception:
                frappe.db.rollback(save_point=sp)
                rest.append(eintrag)
        if len(rest) == len(offen):
            break  # kein Fortschritt mehr -- der Rest hängt an echten Daten
        offen = rest

    # Vereinskonfiguration ist ein Single und wird nicht geloescht, sondern
    # genau in den Feldern geleert, die die Demo gefüllt hat. vereinsname und
    # ort sind Pflichtfelder -- beim Leeren wird die Prüfung übergangen,
    # damit wieder ein leeres Formular zum Ausfüllen dasteht.
    for eintrag in einzeln:
        doc = frappe.get_doc(KONFIG)
        for feld in eintrag.get("felder", []):
            if hasattr(doc, feld):
                setattr(doc, feld, None)
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)

    # Die fehlgeschlagenen Löschversuche haben Frappe-Meldungen erzeugt.
    # Was wirklich übrig blieb, meldet diese Funktion selbst zurück.
    frappe.clear_messages()

    _index_speichern(offen)
    frappe.db.commit()

    return {
        "geloescht": geloescht,
        "verblieben": [f'{e["doctype"]} {e["name"]}' for e in offen],
        "status": status(),
    }


# ─── Einstiegspunkte für die Kommandozeile ───────────────────────────────────

def run():
    frappe.set_user("Administrator")
    ergebnis = demo_daten_anlegen()
    print(f"✅ Demo-Daten angelegt: {ergebnis['anzahl']} Datensätze")
    for doctype, anzahl in sorted(ergebnis["nach_doctype"].items()):
        print(f"   {anzahl:>3} × {doctype}")


def remove():
    frappe.set_user("Administrator")
    ergebnis = demo_daten_entfernen()
    print(f"🧹 {ergebnis['geloescht']} Demo-Datensätze entfernt")
    if ergebnis["verblieben"]:
        print("Nicht entfernbar (noch verknüpft):")
        for eintrag in ergebnis["verblieben"]:
            print(f"   {eintrag}")
