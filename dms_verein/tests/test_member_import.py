import unittest

from dms_verein.member_import import MemberImportError, parse_member_csv


HEADER = "externe_id;mitgliedsnummer;vorname;nachname;strasse;plz;ort;mitgliedstyp;eintrittsdatum;email;abteilungen;iban\n"


class MemberImportParserTest(unittest.TestCase):
	def test_normalizes_dates_email_and_iban(self):
		rows, errors = parse_member_csv(
			HEADER
			+ "ALT-1;;Ada;Lovelace;Testweg 1;12345;Berlin;Aktiv;01.02.2020;ADA@EXAMPLE.ORG;Tennis|Turnen;DE89 3704 0044 0532 0130 00\n"
		)

		self.assertEqual(errors, [])
		self.assertEqual(rows[0]["eintrittsdatum"], "2020-02-01")
		self.assertEqual(rows[0]["email"], "ada@example.org")
		self.assertEqual(rows[0]["iban"], "DE89370400440532013000")
		self.assertEqual(rows[0]["abteilungen"], ["Tennis", "Turnen"])

	def test_uses_member_number_as_external_id(self):
		rows, errors = parse_member_csv(
			HEADER + ";4711;Ada;Lovelace;Testweg 1;12345;Berlin;Aktiv;2020-01-01;;;\n"
		)

		self.assertEqual(errors, [])
		self.assertEqual(rows[0]["externe_id"], "4711")

	def test_accepts_family_stem_header(self):
		header = HEADER.replace("abteilungen", "familienstaemme")
		rows, errors = parse_member_csv(
			header + "ALT-4;;Ada;Lovelace;Testweg 1;12345;Berlin;Aktiv;2020-01-01;;Nord|Süd;\n"
		)

		self.assertEqual(errors, [])
		self.assertEqual(rows[0]["abteilungen"], ["Nord", "Süd"])

	def test_generates_deterministic_external_id(self):
		line = ";;Ada;Lovelace;Testweg 1;12345;Berlin;Aktiv;2020-01-01;ada@example.org;;\n"
		first, _ = parse_member_csv(HEADER + line)
		second, _ = parse_member_csv(HEADER + line)

		self.assertRegex(first[0]["externe_id"], r"^IMPORT-[A-F0-9]{16}$")
		self.assertEqual(first[0]["externe_id"], second[0]["externe_id"])

	def test_reports_invalid_row_without_losing_line_number(self):
		rows, errors = parse_member_csv(
			HEADER + "ALT-2;;Grace;Hopper;Testweg 2;12345;Berlin;Aktiv;31.02.2020;;;\n"
		)

		self.assertEqual(rows, [])
		self.assertEqual(errors[0]["zeile"], 2)
		self.assertIn("Ungültiges Datum", errors[0]["meldung"])

	def test_rejects_missing_required_header(self):
		with self.assertRaisesRegex(MemberImportError, "Pflichtspalten fehlen"):
			parse_member_csv("vorname;nachname\nAda;Lovelace\n")

	def test_rejects_invalid_iban_checksum(self):
		rows, errors = parse_member_csv(
			HEADER + "ALT-3;;Katherine;Johnson;Testweg 3;12345;Berlin;Aktiv;2020-01-01;;;DE00370400440532013000\n"
		)

		self.assertEqual(rows, [])
		self.assertIn("IBAN-Prüfsumme", errors[0]["meldung"])


if __name__ == "__main__":
	unittest.main()