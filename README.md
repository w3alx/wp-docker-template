# WordPress Docker Template

Lokale WordPress-Entwicklungsumgebung mit Docker Compose, MariaDB, WordPress und Adminer.

---

## Features

- WordPress mit PHP 8.3
- MariaDB 11
- Adminer für Datenbankzugriff
- Persistente Datenbank
- Persistente WordPress-Core-Dateien
- Lokaler Zugriff auf `wp-content`
- Einfacher Start neuer Projekte

---

## Enthaltene Services

| Service   | Image                     |
| --------- | ------------------------- |
| WordPress | `wordpress:php8.3-apache` |
| MariaDB   | `mariadb:11`              |
| Adminer   | `adminer`                 |

---

## Projektstruktur

```text
.
├── docker-compose.yml
├── .env.example
├── .env
├── wp-content/
└── README.md
```

## Einrichtung

### 1. Repository klonen

```bash
git clone <repo-url> <projektname>
cd <projektname>
```

### 2. Umgebungsdatei erstellen

```bash
cp .env.example .env
```

Beispiel:

```env
DB_NAME=wordpress
DB_USER=wordpress
DB_PASSWORD=wordpress
DB_ROOT_PASSWORD=root

WP_PORT=8080
ADMINER_PORT=8081
```

### 3. Container starten

```bash
docker compose up -d
```

---

## Zugriff

### WordPress

<http://localhost:8080>

### Adminer

<http://localhost:8081>

---

## Adminer Login

| Feld      | Wert        |
| --------- | ----------- |
| System    | MariaDB     |
| Server    | db          |
| Benutzer  | DB_USER     |
| Passwort  | DB_PASSWORD |
| Datenbank | DB_NAME     |

---

## Datenhaltung

### Datenbank

```yaml
db_data:/var/lib/mysql
```

Speichert die MariaDB-Daten persistent.

### WordPress Core

```yaml
wordpress_data:/var/www/html
```

Speichert den kompletten WordPress-Root inklusive:

```text
wp-config.php
wp-admin/
wp-includes/
```

### wp-content

```yaml
./wp-content:/var/www/html/wp-content
```

Themes, Plugins und Uploads können direkt lokal bearbeitet werden.

---

## Git-Empfehlungen

### Ins Repository

- docker-compose.yml
- .env.example
- README.md
- Eigene Themes
- Eigene Plugins
- ACF JSON

### Nicht ins Repository

```gitignore
.env

wp-content/uploads/
wp-content/cache/
wp-content/upgrade/
```

---

## Nützliche Docker Befehle

### Starten

```bash
docker compose up -d
```

### Stoppen

```bash
docker compose stop
```

### Neustarten

```bash
docker compose start
```

### Entfernen

```bash
docker compose down
```

### Alles löschen (inkl. Volumes)

```bash
docker compose down -v
```

---

## Shell-Zugriff

### WordPress

```bash
docker compose exec wordpress bash
```

### Datenbank

```bash
docker compose exec db bash
```

---

## Logs

Alle Logs:

```bash
docker compose logs -f
```

Nur WordPress:

```bash
docker compose logs -f wordpress
```

Nur Datenbank:

```bash
docker compose logs -f db
```

---

## Status

```bash
docker compose ps
```

---

## Ziel

Neues Projekt starten:

```bash
cp .env.example .env
docker compose up -d
```

Nach wenigen Minuten steht eine vollständige lokale WordPress-Installation inklusive Datenbank und Adminer zur Verfügung.
