/**
 * Anbieter der Software (nicht des Vereins!).
 *
 * Der Verein ist Betreiber seiner eigenen Seite und stellt sein Impressum
 * über die Vereins-Konfiguration ein. Diese Daten hier beschreiben den
 * Anbieter der Plattform "DMS Verein" und werden für die
 * Anbieterkennzeichnung nach § 5 DDG (früher TMG) auf der Produktseite
 * sowie für den Herstellerhinweis im Vereins-Footer verwendet.
 *
 * Quelle: https://website.industrie-4-0.org/impressum/
 */
export const ANBIETER = {
  firma: 'Sascha Böhm Software & App',
  inhaber: 'Sascha Böhm',
  strasse: 'Hohenschwärz 66',
  plz: '91322',
  ort: 'Gräfenberg',
  land: 'Deutschland',
  telefon: '+49 151 155 20 344',
  email: 'service@industrie-4-0.org',
  kontaktEmail: 'kontakt@industrie-4-0.org',
  website: 'https://website.industrie-4-0.org/',
  impressumUrl: 'https://website.industrie-4-0.org/impressum/',
  ustIdNr: 'DE337811439',
  produkt: 'DMS Verein',
}

/** "Hohenschwärz 66, 91322 Gräfenberg, Deutschland" */
export const ANBIETER_ANSCHRIFT = `${ANBIETER.strasse}, ${ANBIETER.plz} ${ANBIETER.ort}, ${ANBIETER.land}`

/** Telefonnummer ohne Leerzeichen, für tel:-Links */
export const ANBIETER_TEL_HREF = `tel:${ANBIETER.telefon.replace(/\s+/g, '')}`
