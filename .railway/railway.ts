import {
  defineRailway,
  github,
  group,
  image,
  preserve,
  project,
  redis,
  service,
  volume,
} from "railway/iac";

const GITHUB_REPO = "Adrian-adric-gmbh/dms_verein";

function requiredEnvironment(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} fehlt. Bitte deploy/deploy-railway.sh verwenden.`);
  }
  return value;
}

export default defineRailway(() => {
  const cache = redis("redis");
  const region = "europe-west4-drams3a"; // EU West Metal (Amsterdam)
  const sites = volume("frappe-sites", { region, sizeMB: 5000 });
  const databaseData = volume("mariadb-data", { region, sizeMB: 5000 });
  const database = service("mariadb", {
    source: image("mariadb:10.11", {
      autoUpdates: { type: "patch" },
    }),
    regions: { [region]: 1 },
    volumeMounts: {
      "/var/lib/mysql": databaseData,
    },
    env: {
      MARIADB_ROOT_PASSWORD: requiredEnvironment("DMS_RAILWAY_DB_ROOT_PASSWORD"),
      MARIADB_AUTO_UPGRADE: "1",
    },
  });

  const app = service("frappe", {
    source: github(GITHUB_REPO, { branch: "main" }),
    start: "dms-railway-start",
    healthcheck: "/api/method/dms_verein.api.health.check",
    // Grosszuegig: "bench new-site" (einmaliger Erstboot mit leerem Volume) migriert
    // frappe+erpnext+dms_verein Doctypes und kann deutlich laenger als 5 Minuten dauern.
    healthcheckTimeout: 1800,
    regions: { [region]: 1 },
    volumeMounts: {
      "/home/frappe/frappe-bench/sites": sites,
    },
    env: {
      RAILWAY_DOCKERFILE_PATH: "deploy/railway-app.Dockerfile",
      SITE_NAME: "dms.internal",
      DB_HOST: database.env.RAILWAY_PRIVATE_DOMAIN,
      DB_PORT: "3306",
      DB_ROOT_USER: "root",
      DB_ROOT_PASSWORD: requiredEnvironment("DMS_RAILWAY_DB_ROOT_PASSWORD"),
      REDIS_URL: cache.env.REDIS_URL,
      ADMIN_PASSWORD: requiredEnvironment("DMS_RAILWAY_ADMIN_PASSWORD"),
      PORT: "8080",
      GUNICORN_WORKERS: "2",
      GUNICORN_THREADS: "4",
      GUNICORN_TIMEOUT: "120",
      // Wird erst nach dem Apply per "railway variable set" gesetzt (siehe deploy-railway.sh)
      PUBLIC_HOST: preserve(),
    },
  });

  const gateway = service("gateway", {
    source: github(GITHUB_REPO, { branch: "main" }),
    healthcheck: "/health",
    healthcheckTimeout: 30,
    regions: { [region]: 1 },
    env: {
      RAILWAY_DOCKERFILE_PATH: "deploy/railway-gateway.Dockerfile",
      FRAPPE_UPSTREAM: app.env.RAILWAY_PRIVATE_DOMAIN,
      INTERNAL_ACCESS_USER: requiredEnvironment("DMS_RAILWAY_ACCESS_USER"),
      INTERNAL_ACCESS_PASSWORD_HASH: requiredEnvironment("DMS_RAILWAY_ACCESS_PASSWORD_HASH"),
    },
  });

  return project("dms-verein", {
    resources: [
      group("Anwendung", [app, gateway, sites]),
      group("Daten", [database, databaseData, cache]),
    ],
  });
});