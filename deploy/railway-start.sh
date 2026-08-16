#!/usr/bin/env bash
set -Eeuo pipefail

# Railway mountet persistente Volumes root-eigentuemerisch; einmalig korrigieren
# und danach als frappe weiterlaufen (bench darf nicht als root ausgefuehrt werden).
if [[ "$(id -u)" == "0" ]]; then
	mkdir -p /home/frappe/frappe-bench/sites
	chown -R frappe:frappe /home/frappe/frappe-bench/sites
	# Docker legt stdout/stderr root-eigentuemerisch an, wenn der Container als root
	# startet; ohne diesen chown kann nginx seine auf /dev/stdout bzw. /dev/stderr
	# verlinkten Logdateien als frappe nicht mehr oeffnen.
	chown frappe /proc/self/fd/1 /proc/self/fd/2
	exec gosu frappe "$0"
fi

: "${SITE_NAME:=dms.internal}"
: "${SITE_DB_NAME:=dms_verein}"
: "${DB_HOST:?DB_HOST fehlt}"
: "${DB_PORT:=3306}"
: "${DB_ROOT_USER:=root}"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD fehlt}"
: "${REDIS_URL:?REDIS_URL fehlt}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD fehlt}"
: "${PUBLIC_SCHEME:=https}"

cd /home/frappe/frappe-bench

mkdir -p sites
# Diagnose: zeigt, ob das Railway-Volume wirklich unter sites/ gemountet ist.
echo "=== VOLUME-DIAGNOSE ==="
df -h /home/frappe/frappe-bench/sites 2>&1 || true
echo "--- mount ---"
mount 2>/dev/null | grep -E "frappe-bench/sites" || echo "(kein eigener Mount auf sites/ gefunden)"
echo "--- Inhalt sites/ ---"
ls -la sites/ 2>&1 | head -20
echo "--- site_config vorhanden? ---"
ls -la "sites/$SITE_NAME/site_config.json" 2>&1 || echo "(fehlt)"
echo "=== ENDE DIAGNOSE ==="
# Railways Volume ist wirklich leer -- anders als ein Docker-Named-Volume kopiert
# es den gebackenen Image-Inhalt nicht vor (kein "copy-up"); ohne diese Datei
# schlaegt "bench set-config -g" mit FileNotFoundError fehl.
if [[ ! -f sites/common_site_config.json ]]; then
	echo '{}' > sites/common_site_config.json
fi
ls -1 apps > sites/apps.txt

bench set-config -g db_host "$DB_HOST"
bench set-config -gp db_port "$DB_PORT"
bench set-config -g redis_cache "$REDIS_URL"
bench set-config -g redis_queue "$REDIS_URL"
bench set-config -g redis_socketio "$REDIS_URL"
bench set-config -gp socketio_port 9000
bench set-config -g chromium_path /usr/bin/chromium-headless-shell

echo "Warte auf MariaDB und Redis ..."
for attempt in $(seq 1 60); do
	if mysqladmin ping --silent --host="$DB_HOST" --port="$DB_PORT" --user="$DB_ROOT_USER" --password="$DB_ROOT_PASSWORD" \
		&& redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; then
		break
	fi
	if [[ "$attempt" == "60" ]]; then
		echo "MariaDB oder Redis ist nach 120 Sekunden nicht erreichbar." >&2
		exit 1
	fi
	sleep 2
done

if [[ ! -f "sites/$SITE_NAME/site_config.json" ]]; then
	# Schutz vor Datenverlust: Wenn die Datenbank bereits Daten enthaelt, aber die
	# site_config.json fehlt (z. B. Volume nicht gemountet), NICHT stillschweigend
	# eine leere Site anlegen -- lieber laut abbrechen, damit die Volume-Anbindung
	# geprueft wird.
	table_count="$(mysql --host="$DB_HOST" --port="$DB_PORT" --user="$DB_ROOT_USER" \
		--password="$DB_ROOT_PASSWORD" --batch --skip-column-names \
		-e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$SITE_DB_NAME'" 2>/dev/null || echo 0)"
	if [[ "${table_count:-0}" -gt 0 ]]; then
		echo "ABBRUCH: Datenbank '$SITE_DB_NAME' enthaelt bereits $table_count Tabellen," >&2
		echo "aber sites/$SITE_NAME/site_config.json fehlt. Es wird KEINE neue Site" >&2
		echo "angelegt, um vorhandene Daten nicht zu verlieren. Bitte die Anbindung des" >&2
		echo "Volumes 'frappe-sites' pruefen (railway volume list / config apply)." >&2
		exit 1
	fi
	echo "Erstelle Frappe-Site $SITE_NAME ..."
	bench new-site "$SITE_NAME" \
		--db-name "$SITE_DB_NAME" \
		--db-host "$DB_HOST" \
		--db-port "$DB_PORT" \
		--db-root-username "$DB_ROOT_USER" \
		--db-root-password "$DB_ROOT_PASSWORD" \
		--admin-password "$ADMIN_PASSWORD" \
		--install-app dms_verein \
		--no-mariadb-socket
else
	if ! bench --site "$SITE_NAME" list-apps --format text | grep -qx dms_verein; then
		bench --site "$SITE_NAME" install-app dms_verein
	fi
	bench --site "$SITE_NAME" migrate
fi

# nginx liefert /assets aus sites/assets aus. bench verlinkt dort frappe/erpnext,
# aber nicht dms_verein (dessen Vue-SPA ist vorgebaut, kein "bench build" im
# Runtime-Image). Daher den Symlink hier explizit auf dem Volume anlegen.
mkdir -p sites/assets
ln -sfn /home/frappe/frappe-bench/apps/dms_verein/dms_verein/public sites/assets/dms_verein

bench use "$SITE_NAME"
bench --site "$SITE_NAME" set-config host_name "${PUBLIC_SCHEME}://${PUBLIC_HOST:-$SITE_NAME}"
bench --site "$SITE_NAME" enable-scheduler
bench --site "$SITE_NAME" clear-cache

export BACKEND=127.0.0.1:8000
export SOCKETIO=127.0.0.1:9000
export FRAPPE_SITE_NAME_HEADER="$SITE_NAME"
export CLIENT_MAX_BODY_SIZE="${CLIENT_MAX_BODY_SIZE:-50m}"

pids=()
stop_processes() {
	trap - TERM INT EXIT
	if ((${#pids[@]})); then
		kill "${pids[@]}" 2>/dev/null || true
		wait "${pids[@]}" 2>/dev/null || true
	fi
}
trap stop_processes TERM INT EXIT

start.sh & pids+=("$!")
node apps/frappe/socketio.js & pids+=("$!")
bench worker --queue short,default & pids+=("$!")
bench worker --queue long,default,short & pids+=("$!")
bench schedule & pids+=("$!")
nginx-entrypoint.sh & pids+=("$!")

wait -n "${pids[@]}"
echo "Ein Frappe-Prozess wurde unerwartet beendet." >&2
exit 1