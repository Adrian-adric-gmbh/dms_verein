### Vereinsverwaltung

Vereins- und Mitgliederverwaltung

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app dms_verein
```

### Produktion und Railway

Die App benötigt den vollständigen Frappe-Stack einschließlich Queue-Workern und Scheduler. Hinweise zum
internen Passwortschutz, Railway-Aufbau, SMTP, Backups und Mitgliederimport stehen in
[docs/production-railway.md](docs/production-railway.md).

Geführtes Railway-Deployment:

```bash
./deploy/deploy-railway.sh
```

### Lokal mit Docker

Voraussetzung ist Docker mit dem Compose-Plugin. Der vollständige lokale Stack aus Frappe, MariaDB und
Redis wird mit einem Befehl eingerichtet:

```bash
./deploy/local.sh setup
```

Das Script erzeugt lokale Zugangsdaten, persistente Docker-Volumes und wartet auf den Healthcheck. Danach
ist die App unter `http://localhost:8080/verein` erreichbar. Weitere Befehle:

```bash
./deploy/local.sh status
./deploy/local.sh logs
./deploy/local.sh credentials
./deploy/local.sh stop
./deploy/local.sh start
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/dms_verein
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
