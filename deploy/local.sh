#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/compose.local.yaml"
ENV_FILE="$ROOT_DIR/deploy/.env.local"
ACTION="${1:-setup}"

compose() {
	docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

require_docker() {
	if ! command -v docker >/dev/null 2>&1; then
		echo "Docker fehlt. Installation: https://docs.docker.com/engine/install/" >&2
		exit 1
	fi
	if ! docker compose version >/dev/null 2>&1; then
		echo "Das Docker-Compose-Plugin fehlt." >&2
		exit 1
	fi
	if ! docker info >/dev/null 2>&1; then
		echo "Docker läuft nicht oder der aktuelle Benutzer hat keinen Zugriff." >&2
		exit 1
	fi
}

create_environment() {
	if [[ -f "$ENV_FILE" ]]; then
		return
	fi
	if ! command -v openssl >/dev/null 2>&1; then
		echo "openssl wird zum Erzeugen lokaler Kennwörter benötigt." >&2
		exit 1
	fi

	umask 077
	local admin_password database_password
	admin_password="$(openssl rand -hex 16)"
	database_password="$(openssl rand -hex 32)"
	cat >"$ENV_FILE" <<EOF
LOCAL_PORT=8080
LOCAL_ADMIN_PASSWORD=$admin_password
LOCAL_DB_ROOT_PASSWORD=$database_password
EOF
	chmod 600 "$ENV_FILE"
	echo "Lokale Zugangsdaten wurden in deploy/.env.local erzeugt."
}

port_is_listening() {
	local port="$1"
	if command -v ss >/dev/null 2>&1; then
		ss -H -ltn "sport = :$port" 2>/dev/null | grep -q .
		return
	fi
	return 1
}

ensure_available_port() {
	require_environment
	if compose ps --status running --services 2>/dev/null | grep -qx frappe; then
		return
	fi

	local current_port selected_port
	current_port="$(sed -n 's/^LOCAL_PORT=//p' "$ENV_FILE")"
	current_port="${current_port:-8080}"
	if ! port_is_listening "$current_port"; then
		return
	fi

	selected_port=""
	for candidate in $(seq 8080 8099); do
		if ! port_is_listening "$candidate"; then
			selected_port="$candidate"
			break
		fi
	done
	if [[ -z "$selected_port" ]]; then
		echo "Zwischen 8080 und 8099 wurde kein freier lokaler Port gefunden." >&2
		exit 1
	fi

	sed -i "s/^LOCAL_PORT=.*/LOCAL_PORT=$selected_port/" "$ENV_FILE"
	echo "Port $current_port ist belegt; verwende stattdessen Port $selected_port."
}

require_environment() {
	if [[ ! -f "$ENV_FILE" ]]; then
		echo "Lokale Konfiguration fehlt. Zuerst ausführen: ./deploy/local.sh setup" >&2
		exit 1
	fi
}

show_credentials() {
	require_environment
	local admin_password port
	admin_password="$(sed -n 's/^LOCAL_ADMIN_PASSWORD=//p' "$ENV_FILE")"
	port="$(sed -n 's/^LOCAL_PORT=//p' "$ENV_FILE")"
	echo "URL:      http://localhost:${port:-8080}/verein"
	echo "Desk:     http://localhost:${port:-8080}/app"
	echo "Benutzer: Administrator"
	echo "Kennwort: $admin_password"
}

case "$ACTION" in
	setup)
		require_docker
		create_environment
		ensure_available_port
		echo "Baue und starte Frappe, MariaDB und Redis. Der erste Start kann mehrere Minuten dauern ..."
		compose up --detach --build --wait --wait-timeout 900
		echo
		echo "Lokale Vereinsverwaltung ist bereit."
		show_credentials
		;;
	start)
		require_docker
		require_environment
		compose up --detach --wait --wait-timeout 900
		show_credentials
		;;
	stop)
		require_docker
		require_environment
		compose stop
		;;
	restart)
		require_docker
		require_environment
		compose restart
		compose up --detach --wait --wait-timeout 900
		show_credentials
		;;
	logs)
		require_docker
		require_environment
		compose logs --follow --tail 200 "${2:-frappe}"
		;;
	status)
		require_docker
		require_environment
		compose ps
		;;
	credentials)
		show_credentials
		;;
	reset)
		require_docker
		require_environment
		echo "ACHTUNG: Dadurch werden die lokale Datenbank und alle lokalen Dateien gelöscht."
		read -r -p "Zum Fortfahren RESET eingeben: " confirmation
		if [[ "$confirmation" != "RESET" ]]; then
			echo "Abgebrochen."
			exit 0
		fi
		compose down --volumes --remove-orphans
		rm -f "$ENV_FILE"
		echo "Lokale Daten wurden entfernt."
		;;
	*)
		echo "Verwendung: ./deploy/local.sh {setup|start|stop|restart|logs [service]|status|credentials|reset}" >&2
		exit 2
		;;
esac