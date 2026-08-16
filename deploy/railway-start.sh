#!/usr/bin/env bash
set -Eeuo pipefail

: "${SITE_NAME:=dms.internal}"
: "${DB_HOST:?DB_HOST fehlt}"
: "${DB_PORT:=3306}"
: "${DB_ROOT_USER:=root}"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD fehlt}"
: "${REDIS_URL:?REDIS_URL fehlt}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD fehlt}"
: "${PUBLIC_SCHEME:=https}"

cd /home/frappe/frappe-bench

mkdir -p sites
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
	echo "Erstelle Frappe-Site $SITE_NAME ..."
	bench new-site "$SITE_NAME" \
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