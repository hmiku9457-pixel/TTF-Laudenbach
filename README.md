# TTF Laudenbach – Vereinswebsite

Statische Vereinswebsite auf GitHub Pages.

## Die einfache Regel

Bearbeitet werden nur die **Quelldateien**:

- Seiteninhalte: `index.html` und `pages/**/*.html`
- gemeinsamer Header und Footer: `components/`
- Gestaltung: `assets/css/`
- Funktionen: `assets/js/`
- dynamische Inhalte: `assets/data/`

Nicht direkt bearbeiten:

- `assets/css/site.bundle.css`
- die markierten Header-/Footer-Blöcke in den HTML-Dateien
- `sitemap.xml`

Diese Dateien werden aus den Quellen erzeugt.

## Nach einer Änderung

### Normale Inhalte, JavaScript oder Daten

Änderung committen. Der Workflow **„Website bauen und prüfen“** startet automatisch.

### Header, Footer, CSS oder Seitenstruktur

Unter **Actions → Website bauen und prüfen → Run workflow** die Option

**„Header, Footer, CSS-Bundle und Sitemap aktualisieren“**

aktivieren. Der Workflow baut, prüft und committet die erzeugten Dateien.

## Dauerhafte Workflows

- **Website bauen und prüfen** – Build, Qualitätsprüfung und Browsertests
- **Generate Gallery JSON** – aktualisiert die Galerie-Daten
- **Auto-Update Daten** – aktualisiert Mannschafts- und Spieldaten

Einmalige Design-, Patch- und Migrationsworkflows gehören nicht mehr zum
dauerhaften Aufbau.

## Werkzeuge

```text
tools/site/build.py   # Header, Footer, CSS-Bundle und Sitemap
tools/site/check.py   # HTML, Links, JSON, Imports und Repository-Hygiene
tests/e2e/            # Browser- und Layouttests
```
