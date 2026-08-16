FROM frappe/erpnext:v16

USER root

RUN apt-get update \
	&& apt-get install --no-install-recommends -y redis-tools gosu \
	&& rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/dms_verein
COPY --chown=frappe:frappe deploy/railway-start.sh /usr/local/bin/dms-railway-start

RUN chmod 755 /usr/local/bin/dms-railway-start \
	&& /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/dms_verein

# Bleibt root: Railway mountet Volumes root-eigentümerisch, railway-start.sh
# korrigiert die Rechte und wechselt selbst zu frappe.
USER root
WORKDIR /home/frappe/frappe-bench

CMD ["dms-railway-start"]