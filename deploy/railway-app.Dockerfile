FROM frappe/erpnext:v16

USER root

RUN apt-get update \
	&& apt-get install --no-install-recommends -y redis-tools \
	&& rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/dms_verein
COPY --chown=frappe:frappe deploy/railway-start.sh /usr/local/bin/dms-railway-start

RUN chmod 755 /usr/local/bin/dms-railway-start \
	&& /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/dms_verein \
	# Same linking bench build would perform, without requiring node in this runtime image
	&& ln -sfn /home/frappe/frappe-bench/apps/dms_verein/dms_verein/public /home/frappe/frappe-bench/assets/dms_verein \
	&& chown -h frappe:frappe /home/frappe/frappe-bench/assets/dms_verein

USER frappe
WORKDIR /home/frappe/frappe-bench

CMD ["dms-railway-start"]