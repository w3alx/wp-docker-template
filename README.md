# Lokales WordPress mit vollständig bearbeitbarem Root

Diese Testkopie basiert auf w3alx/wp-docker-template, Ausgangscommit `9ae8748`.
Die Vorlage darf vereinfacht und verbessert werden. Sie ist kein festgelegter
WordPress-Stack für alle zukünftigen Projekte.

## Aufbau

- WordPress mit Apache, standardmäßig PHP 8.5.
- MariaDB 11 mit projektbezogenem Datenvolume und Healthcheck.
- Adminer 5 für lokalen Datenbankzugriff.
- Im Offline-Lab zusätzlich ein kleiner Nginx-Gateway für localhost-Zugriff.
- `./wordpress_data:/var/www/html` bindet die gesamte Installation lokal ein.
  Dazu gehören Core, `wp-content`, `wp-config.php` und `.htaccess`.
- WordPress und Adminer sind nur an `127.0.0.1` veröffentlicht. Die Datenbank
  hat keinen veröffentlichten Host-Port.

Die Image-Tags sind über `.env` konfigurierbar. Sie sind beweglich und noch
nicht auf Digests fixiert. Für bestehende Projekte wird die Laufzeit passend
zur Zielumgebung gewählt; PHP 8.5 ist keine allgemeine Legacy-Vorgabe.

## Einrichtung

Kopiere `.env.sample` nach `.env` und setze zwei unterschiedliche, zufällige,
rein lokale Datenbankpasswörter. Leere Passwörter verhindern den Compose-Start.
`.env` wird nicht versioniert. Die Datenbankwerte initialisieren ein neues
Volume; spätere Änderungen in `.env` ändern keine vorhandenen DB-Benutzer.

In dieser Lab-Kopie wurde `.env` bereits mit generierten Testpasswörtern und
separaten Testports vorgesehen: WordPress `18080`, Adminer `18088`.

Alle folgenden Befehle im Verzeichnis dieser Testkopie ausführen:

```bash
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml config --quiet
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml up -d --wait
```

Danach WordPress unter <http://127.0.0.1:18080> und Adminer unter
<http://127.0.0.1:18088> öffnen. Die WordPress-Erstinstallation erfolgt separat.
Adminer verwendet Server `db` und die lokalen DB-Zugangsdaten aus `.env`.

Für weitere Projekte einen eigenen Compose-Projektnamen und eigene freie Ports
verwenden. Keine festen Container-, Netzwerk- oder Volumenamen hinzufügen.

## Sicherer Testbetrieb

`compose.lab.yml` ergänzt ein internes Docker-Netzwerk ohne regulären externen
Netzwerkzugriff von WordPress, Adminer und Datenbank. Ein Nginx-Gateway verbindet
dieses Netzwerk mit einem separaten Eingangsnetzwerk und veröffentlicht ausschließlich
die beiden localhost-Ports. Er hat keine WordPress-Dateien oder DB-Zugangsdaten
eingebunden und leitet nur an die zwei festen lokalen Dienste weiter.

Diese Trennung ist nötig, weil interne Netzwerke in der getesteten Docker-Umgebung
keine direkt erreichbaren Host-Port-Mappings liefern. Das Overlay nutzt `!reset` für Ports und
benötigt eine Compose-Version mit Unterstützung für `!reset` (hier 5.5.1). Die einfache Basis bleibt bei
drei Diensten; der vierte Dienst gehört ausschließlich zum Offline-Lab. Das Gateway
selbst hat externen Netzwerkzugriff. Downloads von Images erfolgen durch Docker selbst;
WordPress-interne Plugin-/Theme-Downloads, Updates und externe APIs funktionieren
im Offline-Modus nicht. Externen Zugriff erst für einen konkreten, geprüften
Vorgang freigeben. Die Basisdatei allein bietet diesen Offline-Schutz nicht.

Die eingebundene `docker/php/lab.ini` lässt PHP-Mailversand über `/bin/false`
fehlschlagen. E-Mails werden momentan nicht in einem lokalen Postfach gesammelt.
Ein lokaler Mailfänger kann später ergänzt werden, falls Formular-Tests ihn brauchen.

Diese Maßnahmen ersetzen keine Prüfung importierter Plugins und Daten.
Ein internes Docker-Netzwerk ist keine vollständige Sicherheitsgrenze zum Host.
JavaScript im Browser kann weiterhin externe Dienste erreichen. Vor echten
Projektimporten müssen Credentials, SMTP, Webhooks, Tracking und Kundendaten
bereinigt bzw. deaktiviert werden.

## Daten und Bearbeitung

Nach dem ersten Start liegt der komplette WordPress-Root in `wordpress_data/`.
Der Ordner bleibt nach Container-Neustarts erhalten und ist unversioniert.
Das offizielle Image befüllt einen leeren Root beim Start.

`.htaccess` liegt direkt in diesem Root. Eine vorhandene oder selbst angelegte
Datei bleibt bearbeitbar. Für reguläre Projektentwicklung bevorzugen wir eigene
Themes und Plugins; Änderungen am Core sind lokal möglich, aber updateanfällig.

Eigene Themes/Plugins werden noch nicht separat versioniert. Das legen wir bei
der ersten tatsächlichen Implementierungsaufgabe fest. DB-Dumps, Zugangsdaten,
Uploads und die gesamte generierte Installation gehören nicht in dieses Template-Repo.

## Betrieb und Checks

```bash
# Status
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml ps
# Logs (können nach einem Import sensible Inhalte enthalten)
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml logs --tail=50
# PHP-Laufzeit und Apache-Konfiguration
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml exec -T wordpress php -v
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml exec -T wordpress apache2ctl -t
# Stoppen, Daten behalten
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml stop
# Container/Netzwerk entfernen, Daten behalten
docker compose -p codex-lab-wp-template -f docker-compose.yml -f compose.lab.yml down
```

`down -v` löscht die Datenbank dieses Compose-Projekts. Das ist kein normaler
Stop-Befehl. Es löscht den Bind-Mount `wordpress_data/` nicht und ist hier
bewusst nicht als Routine vorgesehen.

Vor Abschluss von Änderungen Compose validieren, betroffene Laufzeitfunktionen
prüfen und `git diff --check` sowie den finalen Diff und Status prüfen.
Es gibt noch keine Theme-/Plugin-Lints, Unit-Tests oder CI, da noch kein eigener
Anwendungscode enthalten ist.

## Quellen

- [Docker: interne Netzwerke](https://docs.docker.com/reference/compose-file/networks/)
- [Offizieller WordPress-Entrypoint](https://github.com/docker-library/wordpress/blob/master/docker-entrypoint.sh)
- [MariaDB: Healthcheck](https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/using-healthcheck-sh)
