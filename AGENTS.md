# WordPress-Template: Projektanweisungen

Diese Kopie ist ein lokales Testprojekt. Die Vorlage darf begründet verbessert
werden. Ziel ist eine einfache Docker-Umgebung mit vollständig lokal bearbeitbarem
WordPress-Root einschließlich wp-config.php und .htaccess.

- Kommuniziere auf Deutsch. Lies README.md und den relevanten Code vor Änderungen.
- Erhalte den vollständigen Bind-Mount nach wordpress_data/. Core-Dateien dürfen
  für lokale Untersuchungen bearbeitet werden; reguläre Projektfunktionen gehören
  nach Möglichkeit in eigene Themes oder Plugins.
- Nutze vorhandene Standards und kleine, nachvollziehbare Änderungen. Begründe
  neue Abhängigkeiten und Architekturentscheidungen. Keine beiläufigen Refactorings.
- Lokale Änderungen und Checks sind erlaubt. Globale Einstellungen und andere
  Projekte bleiben unberührt. Respektiere vorhandene Änderungen.
- Keine produktiven Credentials, Kundendaten oder echten Integrationen verwenden.
  Externe Seiteneffekte und Datenübertragung erfordern ausdrückliche Freigabe.
  Deployment übernimmt Alex. Tool-Verfügbarkeit ist keine Freigabe.
- Prüfe vor Start/Import Compose-Projekt, Mounts, Volumes und Integrationen.
  Im Lab immer beide Compose-Dateien und den vereinbarten Projektnamen verwenden.
  Keine globalen Docker-Aufräumaktionen und kein Löschen wertvoller Daten.
- .env und wordpress_data/ bleiben unversioniert. Keine Secrets in Dokumentation,
  Logs oder Abschlussberichten. Für Beispiele ausschließlich Platzhalter verwenden.
- Validiere Eingaben, prüfe Berechtigungen und Ausgabekontexte, behandle Fehler
  nachvollziehbar und entferne temporäre Debug-Ausgaben.
- Delegiere nach Änderungen an Security-/Isolationsregeln einen lesenden
  Security-Review an einen Subagent, sofern verfügbar. Findings brauchen Auslöser,
  Auswirkung und Datei/Zeile. Der Hauptagent bewertet und korrigiert sie.
- Vor Abschluss: Compose-Konfiguration validieren, bei Laufzeitänderungen die
  betroffenen Funktionen testen, finalen Diff und Status prüfen und relevante
  Dokumentation aktualisieren. Trenne vorbestehende Fehler von neuen Problemen.
- Nenne tatsächlich ausgeführte Checks und verbleibende Einschränkungen.
  Nicht ausgeführte Pflichtchecks gelten nicht als bestanden.

Check-Befehle und Grenzen des Offline-Modus stehen in README.md.
