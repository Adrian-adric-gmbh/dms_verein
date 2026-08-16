# Railway Infrastructure as Code

Die Datei `railway.ts` verwaltet den vollständigen Railway-Stack. Nicht direkt mit
`railway config apply` starten, sondern aus dem Repository-Root:

```bash
./deploy/deploy-railway.sh
```

Das Script setzt die nur während des Plans benötigten Secrets als lokale
Umgebungsvariablen. Railway zeigt Variablenwerte im Plan standardmäßig redigiert an.