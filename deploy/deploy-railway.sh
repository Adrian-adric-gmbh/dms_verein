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

if ! command -v docker >/dev/null 2>&1; then
	echo "Docker wird benötigt, um den Caddy-Passwort-Hash zu erzeugen." >&2
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

read -r -p "Interner Benutzername [verein]: " access_user
access_user="${access_user:-verein}"
read -r -s -p "Internes Zugangskennwort: " access_password
echo
read -r -s -p "Frappe-Administrator-Kennwort: " admin_password
echo

if [[ ${#access_password} -lt 16 || ${#admin_password} -lt 16 ]]; then
	echo "Beide Kennwörter müssen mindestens 16 Zeichen lang sein." >&2
	exit 1
fi

password_hash="$(docker run --rm caddy:2.10-alpine caddy hash-password --plaintext "$access_password")"
database_password="$(openssl rand -hex 32)"
unset access_password

export DMS_RAILWAY_ACCESS_USER="$access_user"
export DMS_RAILWAY_ACCESS_PASSWORD_HASH="$password_hash"
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
echo "Erzeuge eine öffentliche Domain ausschließlich für den Passwort-Gateway ..."
railway domain --service gateway || true
railway variable set 'PUBLIC_HOST=${{gateway.RAILWAY_PUBLIC_DOMAIN}}' --service frappe

echo
echo "Deployment angestoßen. Status und Logs:"
echo "  npx @railway/cli status"
echo "  npx @railway/cli logs --service frappe"
echo "  npx @railway/cli logs --service gateway"
echo
echo "Wichtig: Gib dem Service 'frappe' keine öffentliche Domain."