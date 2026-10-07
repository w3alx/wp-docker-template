# Validierung des Lab-Installers

Stand: 7. Oktober 2026. Branch: lab/codex-local-wordpress.

## Geprüft

- Hauptinstanz: WordPress installiert, Frontend HTTP 200, Admin-Login mit
  authentifiziertem Dashboard erfolgreich.
- Frische separate Projektkopie: erster Installer-Lauf erfolgreich mit
  WordPress-Healthcheck, eigenen Ports und eigenem Datenvolume.
- Falsches geerbtes WP_PORT überschreibt die eigene .env nicht.
- Wiederholung erhält bestehende Inhalte, Benutzer und Titel.
- Kopierte .local-Projektidentität wird abgewiesen; fremde Compose-Ressourcen
  werden nicht übernommen. Widersprüchliche Docker-Zielvariablen werden abgewiesen.
- .env und Admin-Credentials sind ignoriert; Passwortdatei hat Rechte 0600 und
  liegt außerhalb des Webroots. Passwortübergabe über STDIN; Promptausgabe abgefangen.
- Bind-Mount, .htaccess, PHP-Mail-Sperre und blockierter externer TCP-Test
  praktisch bestätigt. Apache/Nginx- und Compose-Konfiguration valide.
- Separater statischer Review abgeschlossen; Findings korrigiert.
- Projektlokaler Skill mit offiziellem Skill-Validator validiert und unabhängig
  praktisch getestet; Python-Syntaxprüfung und git diff --check bestanden.

## Demonstrierte Korrekturen

Ohne echten WordPress-Healthcheck konnte WP-CLI vor dem Kopieren des Core starten.
Der aktuelle Healthcheck prüft Core/config-Dateien und Apache-Port.

Projektidentität berücksichtigt Checkout-Pfad und Docker-Daemon. Compose arbeitet
mit kontrollierter Umgebung und expliziter .env. Ein privates Abschlussflag
ermöglicht das Fortsetzen eigener Nacharbeiten nach erfolgreichem core install.

WP-CLI kann gepromptete Passwörter ausgeben. Deshalb wird die Ausgabe solcher
Befehle vollständig abgefangen. Ein betroffenes lokales Testpasswort wurde rotiert.

## Grenzen

Getestet auf macOS/Apple Silicon mit Docker Desktop 29.8.0 und Compose 5.5.1.
Windows und andere Hostumgebungen sind nicht praktisch verifiziert. Die frische
Offline-Installation verwendet Englisch; es werden keine Sprachpakete heruntergeladen.
Es gibt keine echten Kundenimporte und keine Tests eigener Themes/Plugins.
Netzwerkisolation ist kein vollständiger Schutz gegenüber Host oder Browser.
Image-Tags bleiben beweglich. Kein Deployment und keine Änderung am Default-Branch.
