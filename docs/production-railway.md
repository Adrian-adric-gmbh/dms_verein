# Produktionsbetrieb auf Railway

## Lokaler Docker-Betrieb

Für lokale Tests ist keine native Bench-, MariaDB- oder Redis-Installation nötig. Mit installiertem Docker
und Compose-Plugin genügt im Repository-Root:

```bash
./deploy/local.sh setup
```

Beim ersten Lauf werden `deploy/.env.local` mit zufälligen Kennwörtern sowie persistente Volumes für Site,
Datenbank und Redis erzeugt. Die Datei wird von Git ignoriert und erhält Dateirechte `600`. Nach dem
erfolgreichen Healthcheck zeigt das Script URL und Administrator-Kennwort an.

```bash
./deploy/local.sh credentials       # URL und Administrator-Kennwort
./deploy/local.sh status            # Containerstatus
./deploy/local.sh logs              # Frappe-Logs verfolgen
./deploy/local.sh logs mariadb      # Datenbanklogs verfolgen
./deploy/local.sh stop              # Container anhalten, Daten behalten
./deploy/local.sh start             # Vorhandenen Stack starten
./deploy/local.sh restart           # Dienste neu starten
./deploy/local.sh reset             # Alle lokalen Daten nach Bestätigung löschen
```

Die Anwendung ist an `127.0.0.1` gebunden und daher standardmäßig nur auf dem lokalen Rechner erreichbar:

```text
Portal: http://localhost:8080/verein
Desk:   http://localhost:8080/app
```

Diese App ist eine Frappe-App und kein eigenständiger Webserver. Für den Betrieb werden ein gepinntes
Frappe/Bench-Image, MariaDB, Redis, Web-, Socket.IO-, Scheduler- und Worker-Prozesse benötigt. Nutze für
das Anwendungsimage den offiziellen `frappe_docker`-Custom-App-Workflow und pinne Image und Frappe-Version
auf einen getesteten Release beziehungsweise Digest.

## Schnellstart

Voraussetzungen sind Docker, Node.js und ein Railway-Konto. Danach aus dem Repository-Root:

```bash
./deploy/deploy-railway.sh
```

Railway baut aus dem GitHub-Repository. Deshalb müssen alle Änderungen vor dem Aufruf committed und nach
`main` gepusht sein. Bei einem privaten Repository muss Railway in den GitHub-Integrationen Zugriff auf
`saschafo/dms_verein` erhalten.

Das Script meldet sich bei Railway an, verknüpft beziehungsweise erstellt ein Projekt, fragt das interne
Zugangskennwort und das Frappe-Administrator-Kennwort ab, zeigt den Infrastrukturplan und legt nach
Bestätigung den Stack an. Kennwörter werden nicht in Dateien geschrieben. Der erste Build kann wegen des
Frappe-Basisimages mehrere Minuten dauern.

Die Infrastruktur ist in [.railway/railway.ts](../.railway/railway.ts) definiert. Railway Infrastructure
as Code ist derzeit experimentell; vor jedem `apply` deshalb den angezeigten Plan prüfen.

## Railway-Architektur

Nur der Service `gateway` erhält eine öffentliche Railway-Domain:

```text
Internet -> Caddy Basic Auth -> Frappe (privates Railway-Netz)
                                             |- nginx + gunicorn
                                             |- socket.io
                                             |- short/long worker
                                              `- scheduler

Frappe ---- Redis ---- MariaDB
    `------ persistentes sites-Volume
```

Webserver, Worker und Scheduler laufen absichtlich in einem Railway-Service. Railway-Volumes können nur
an einen Service gebunden werden, Frappe benötigt aber für Site-Konfiguration und Dateien ein gemeinsames
`sites`-Verzeichnis. Für den vorgesehenen internen Vereinsbetrieb ist diese Architektur einfacher und
zuverlässiger als getrennte Prozesse. Bei größerer Last sollte auf eine Plattform mit Shared Storage oder
S3 und ein separates, gepinntes Custom-App-Image gewechselt werden.

Der Startprozess erstellt beim ersten Lauf die Site und installiert die App. Bei späteren Deployments führt
er vor dem Start automatisch `bench --site dms.internal migrate` aus. Der neue Massenimport läuft im
Long-Queue-Worker desselben Containers.

Nach dem ersten Deploy in Railway kontrollieren:

1. Nur `gateway` besitzt eine öffentliche Domain.
2. `frappe`, `mariadb` und `redis` sind ausschließlich über Private Networking erreichbar.
3. Das Volume `frappe-sites` ist unter `/home/frappe/frappe-bench/sites` gemountet.
4. Das Volume `mariadb-data` ist unter `/var/lib/mysql` gemountet.
5. Gateway und Frappe zeigen einen erfolgreichen Healthcheck.

## Interner Passwortschutz

Das Deploy-Script erzeugt den Passwort-Hash automatisch. Für eine manuelle Änderung:

```bash
docker run --rm caddy:2.10-alpine caddy hash-password --plaintext 'EIN-LANGES-ZUFAELLIGES-PASSWORT'
```

Die zugehörigen Gateway-Variablen sind:

```text
INTERNAL_ACCESS_USER=verein
INTERNAL_ACCESS_PASSWORD_HASH=<Ausgabe von caddy hash-password>
FRAPPE_UPSTREAM=http://<frappe-service>.railway.internal:<port>
```

Der Pfad `/health` bleibt für
Railways Healthcheck erreichbar und liefert keine Anwendungsdaten. Alle anderen Pfade, einschließlich
Assets und öffentlicher Frappe-APIs, verlangen HTTP Basic Auth.

Optional kann zusätzlich am Frappe-Service ein zweiter Schutz aktiviert werden:

```text
DMS_INTERNAL_ACCESS_USER=verein
DMS_INTERNAL_ACCESS_PASSWORD=<gleiches Klartextpasswort als Railway Secret>
```

Dieser Hook schützt dynamische Frappe-Anfragen. Er ersetzt den Gateway nicht, weil ein vorgeschalteter
Webserver statische Assets gegebenenfalls direkt ausliefert.

## E-Mail

HTTP Basic Auth betrifft nur eingehende HTTP-Anfragen. Ausgehende SMTP-Verbindungen und Queue-Worker
funktionieren weiterhin. In Frappe unter **Email Account** ein Konto eines Transaktionsmail-Anbieters
konfigurieren und dabei Port 587 mit STARTTLS oder Port 465 mit TLS verwenden. Port 25 sollte nicht
verwendet werden.

Vor dem Produktivstart:

- Absenderdomain mit SPF, DKIM und DMARC konfigurieren.
- Standard-Absender und Antwortadresse festlegen.
- Testmail aus der Vereinskonfiguration versenden.
- Worker- und Email-Queue überwachen und Fehlversuche alarmieren.
- Willkommensmails beim ersten Import deaktiviert lassen und erst nach Stichproben separat aktivieren.

## Persistenz und Secrets

- `encryption_key`, `secret_key`, Datenbank- und SMTP-Passwörter ausschließlich als Railway Secrets halten.
- Private Dateien und Backups auf persistentem Volume oder S3-kompatiblem Object Storage speichern.
- Vor jedem Deploy automatisches Datenbank- und Dateibackup erstellen und Restore regelmäßig testen.
- Den Frappe-Service nicht zusätzlich öffentlich veröffentlichen; sonst lässt sich der Gateway umgehen.
- Railway-Logs an eine externe Aufbewahrung/Alarmierung anbinden.

## Release-Ablauf

1. CI muss erfolgreich sein.
2. Backup von Datenbank sowie privaten und öffentlichen Dateien erstellen.
3. Änderung nach `main` pushen; Railway baut beide betroffenen Images neu.
4. Der Frappe-Startprozess führt die Migration vor dem Prozessstart aus.
5. Gateway- und Frappe-Healthcheck kontrollieren.
6. Healthcheck, Login, Testmail und einen Import-Dry-Run prüfen.
7. Bei Fehlern vorheriges Image ausrollen; bei nicht rückwärtskompatibler Migration Backup wiederherstellen.

## Mitgliederimport

### Familienverband und Familienstämme

Unter **Konfiguration -> Darstellung -> Organisationsstruktur** lassen sich die sichtbaren Begriffe der
internen Gruppen ändern. Die Schaltfläche **Familienverband** setzt:

```text
Singular: Familienstamm
Plural: Familienstämme
Leitung: Stammesleitung
```

Intern bleiben DocType, API-Pfade und Berechtigungsrolle als `Sparte` beziehungsweise `Spartenleiter`
gespeichert. Dadurch ist keine riskante Umbenennung vorhandener Daten nötig. In Navigation, öffentlicher
Seite, Portal, Anträgen, Kalender, Abstimmungen, Mailing, Verwaltung und Import werden dagegen die
konfigurierten Bezeichnungen angezeigt. Anschließend können unter **Familienstämme** zum Beispiel die
Stämme `Nord`, `Süd` oder historische Familienlinien angelegt und Mitglieder zugeordnet werden.

Der Import akzeptiert für diese Zuordnung sowohl ältere Spaltennamen (`abteilungen`, `sparten`) als auch
`familienstamm`, `familienstaemme`, `stamm` und `staemme`. Mehrere Werte werden mit `|` oder Komma getrennt:

```text
familienstaemme
Stamm Nord|Stamm Süd
```

Nach der Migration steht unter **Mitglieder -> Import** die CSV-Oberfläche bereit. Pflichtspalten sind:

```text
vorname;nachname;strasse;plz;ort;mitgliedstyp;eintrittsdatum
```

`externe_id` ist optional. Wenn sie fehlt, verwendet der Import die `mitgliedsnummer`; fehlt auch diese,
wird aus Name, Geburtsdatum und E-Mail eine deterministische Import-ID erzeugt. Eine echte, unveränderliche
Altsystem-ID bleibt für langfristig wiederholbare Importe vorzuziehen. Ein erneuter Import überspringt bereits
vorhandene IDs. Optional akzeptiert `abteilungen` mehrere vorhandene Sparten, getrennt mit `|` oder Komma,
zum Beispiel `Tennis|Turnen`. Die Oberfläche akzeptiert UTF-8-CSV mit Komma, Semikolon oder Tab, maximal 2 MB und 5.000
Datensätzen. Erst ein fehlerfreier Dry-Run kann gestartet werden. Portal-Konten und Willkommensmails sind
bewusst optionale, vor der Validierung festgelegte Schritte.

Vor dem ersten echten Lauf den Import auf einer Staging-Kopie testen und anschließend Anzahl, Status,
Mitgliedstypen, Eintrittsdaten sowie eine Stichprobe der Bankdaten mit dem Altsystem abgleichen.