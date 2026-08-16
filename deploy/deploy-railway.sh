#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ -n "$(git status --porcelain)" ]]; then
	echo "Das Arbeitsverzeichnis enthält noch nicht committete Änderungen." >&2
	echo "Bitte diese Deployment-Dateien zuerst committen und nach GitHub pushen." >&2
	exit 1
fi
if git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1 \
	&& [[ "$(git rev-list --count '@{upstream}'..HEAD)" != "0" ]]; then
	echo "Der aktuelle Commit wurde noch nicht nach GitHub gepusht." >&2
	exit 1
fi

if ! command -v node >/dev/null 2>&1; then
	echo "Node.js wird für die Railway CLI benötigt." >&2
	exit 1
fi

if [[ ! -d node_modules/railway ]]; then
	echo "Installiere die Railway-TypeScript-SDK für 'railway config plan/apply' ..."
	npm install --no-audit --no-fund
fi

railway() {
	npx --yes @railway/cli@latest "$@"
}

echo "Railway-Anmeldung prüfen ..."
if ! railway whoami >/dev/null 2>&1; then
	railway login
fi

if ! railway status >/dev/null 2>&1; then
	echo "Noch kein Railway-Projekt verknüpft. Bitte im folgenden Dialog ein neues Projekt anlegen oder auswählen."
	railway init
fi

read -r -s -p "Frappe-Administrator-Kennwort: " admin_password
echo

if [[ ${#admin_password} -lt 16 ]]; then
	echo "Das Kennwort muss mindestens 16 Zeichen lang sein." >&2
	exit 1
fi

# MariaDB uebernimmt MARIADB_ROOT_PASSWORD nur beim allerersten Start eines leeren
# Volumes; bei jedem Aufruf ein neues Passwort zu generieren wuerde es vom echten,
# im Volume eingefrorenen Root-Passwort abdriften lassen. Deshalb einmalig erzeugen
# und lokal (git-ignoriert) persistieren.
db_password_file="deploy/.env.railway-db-password"
if [[ ! -f "$db_password_file" ]]; then
	umask 077
	openssl rand -hex 32 > "$db_password_file"
fi
database_password="$(cat "$db_password_file")"

export DMS_RAILWAY_ADMIN_PASSWORD="$admin_password"
export DMS_RAILWAY_DB_ROOT_PASSWORD="$database_password"

echo
echo "Railway-Änderungsplan:"
railway config plan

echo
read -r -p "Diesen Stack jetzt erstellen/aktualisieren? [j/N]: " confirmation
if [[ ! "$confirmation" =~ ^[jJyY]$ ]]; then
	echo "Abgebrochen; es wurden keine Änderungen angewendet."
	exit 0
fi

railway config apply --yes

echo
echo "Erzeuge eine öffentliche Domain für den Frappe-Dienst ..."
railway domain --service frappe || true
railway variable set 'PUBLIC_HOST=${{frappe.RAILWAY_PUBLIC_DOMAIN}}' --service frappe

echo
echo "Deployment angestoßen. Status und Logs:"
echo "  npx @railway/cli status"
echo "  npx @railway/cli logs --service frappe"
echo
echo "Hinweis: Der Passwort-Gateway ist derzeit deaktiviert; Frappe ist direkt"
echo "über die oben erzeugte Domain erreichbar (Zugriff nur über Frappe-Login)."