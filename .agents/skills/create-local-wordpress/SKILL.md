---
name: create-local-wordpress
description: Erstellt und installiert ein neues lokales WordPress-Projekt aus diesem Docker-Template. Verwenden für neue lokale Projektkopien mit bearbeitbarem Core; nicht für Deployment oder Import bestehender Kundenseiten.
---

# Neues lokales WordPress-Projekt

Lies die README.md und scripts/lab.py der Template-Wurzel (drei Verzeichnisse
oberhalb dieses Skill-Ordners). Nutze den dort beschriebenen Offline-Lab-Ablauf.

Kläre Zielordner und Projektname aus dem Auftrag. Wähle freie, getrennte
localhost-Ports und einen eindeutigen Compose-Projektnamen. Routinemäßige lokale
Entscheidungen dürfen selbstständig getroffen werden. Titel und Adminname sind
konfigurierbar; Standard ist local-admin mit zufälligem Passwort.

Erstelle eine frische Kopie des vereinbarten Template-Branches in einem neuen
Zielordner. Nutze git clone, wenn ein Repository gewünscht ist, oder exportiere
einen definierten Commit für eine Kopie ohne Template-Git-Historie. Kopiere keine
.env, .local, wordpress_data, Datenbankvolumes oder Zugangsdaten aus einem anderen
Projekt. Liegen uncommittete Template-Änderungen vor, kläre vor dem Export, ob
sie Bestandteil der neuen Vorlage sein sollen; verliere sie nicht stillschweigend.

Führe in der neuen Kopie aus:

```bash
python3 scripts/lab.py --project <eindeutiger-name> --wp-port <port> --adminer-port <port> --title "<titel>"
```

Der Installer erzeugt lokale Credentials, startet die Offline-Umgebung und
installiert WordPress ohne Mailversand. Zugangsdaten stehen in der ignorierten
.local/wordpress-admin.json außerhalb des Webroots. Gib im Abschluss den Pfad
und den Adminnamen an, aber keine Passwörter. Die Offline-Installation verwendet
Englisch und Europe/Berlin. Andere Sprache/Zeitzone nur bei Bedarf ergänzen;
Sprachpakete benötigen einen separat geprüften öffentlichen Download.

Bei vorhandener Installation erhält der Ablauf Daten und Einstellungen. Bei
Projektkollisionen oder fremden/teilweise gefüllten Datenbanken abbrechen und
die Ursache prüfen. Keine Volumes löschen, um eine Kollision zu umgehen.
Nach Teilfehlern nur die eigene angefangene Installation fortsetzen.

Prüfe nach Installation: Frontend und Login per HTTP, Admin-Authentifizierung
ohne Passwortausgabe, Datenbankzugriff, tatsächlichen Bind-Mount und .htaccess,
PHP-Mail-Sperre und Offline-Verbindungstest. Nutze für Checks dieselben zwei
Compose-Dateien und denselben Projektnamen. Temporäre Prüfdateien entfernen.

Berichte URLs, Zielordner, gespeicherten Zugangsdatenpfad, tatsächliche Checks
und Einschränkungen. Kundendatenimport, echte Integrationen, Push und Deployment
sind keine impliziten Bestandteile dieses Skills.
