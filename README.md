# TTF Laudenbach – Vereinswebsite

Statische Vereinswebsite auf GitHub Pages.

## Grundprinzip

Die Seite bleibt bewusst einfach aufgebaut:

- **HTML (`index.html`, `pages/**/*.html`)** – Seiteninhalt und semantische Struktur
- **`components/header.html`** – gemeinsamer Header und Hauptnavigation
- **`components/footer.html`** – gemeinsamer Footer
- **`assets/css/main.css`** – zentraler CSS-Einstiegspunkt; lädt die CSS-Module direkt per `@import`
- **`assets/js/main.js`** – zentraler JavaScript-Einstiegspunkt; lädt nur benötigte Features
- **`assets/data/`** – dynamisch erzeugte JSON-Daten
- **`assets/python/`** – Scraper, Datenvalidierung und Galerie-Generator

Es gibt keinen CSS-Build und kein `site.bundle.css` mehr.

## Header und Footer

Die HTML-Seiten enthalten nur noch die beiden Platzhalter:

```html
<div id="header-container"></div>
...
<div id="footer-container"></div>
```

`assets/js/core/site-components.js` lädt anschließend:

- `/components/header.html`
- `/components/footer.html`

Damit sind Header und Footer echte **Single Sources of Truth**. Änderungen an Navigation oder Footer werden nur noch in den beiden Dateien unter `components/` vorgenommen.

## CSS

Die Seiten laden direkt:

```html
<link href="/assets/css/main.css" rel="stylesheet"/>
```

`main.css` importiert die getrennten Base-, Layout-, Komponenten- und Responsive-Dateien. Es ist kein Build-Schritt notwendig.

## JavaScript

`assets/js/main.js` initialisiert zuerst Header und Footer und lädt danach nur die Features, die auf der jeweiligen Seite gebraucht werden, zum Beispiel Tabellen, Galerie, Kontaktformular, News-Slider oder Spielerlisten.

## Automatische Daten

### Mannschaften, Spielpläne und Tabellen

Der Workflow **Auto-Update Daten** startet täglich und kann zusätzlich manuell ausgeführt werden.

- Scraper: `assets/python/scraper.py`
- Konfiguration: `assets/python/config.py`
- Prüfung vor Übernahme: `assets/python/validate_scraper_data.py`

Bei einem ungewöhnlich großen Datenrückgang bricht die Prüfung ab. Für einen beabsichtigten Saisonwechsel kann der manuelle Workflow mit `allow_large_data_drop` ausgeführt werden.

### Galerie

Der Workflow **Generate Gallery JSON** läuft bei Änderungen unter `assets/images/` und erzeugt:

```text
assets/data/gallerie.json
```

Die eigentliche Logik liegt in:

```text
assets/python/generate_gallery.py
```

Der GitHub-Workflow enthält dadurch nur noch die Ablaufsteuerung.

## Typische Änderungen

| Änderung | Datei / Bereich |
|---|---|
| Navigation | `components/header.html` |
| Footer | `components/footer.html` |
| Seiteninhalt | jeweilige HTML-Datei |
| Gestaltung | `assets/css/` |
| Frontend-Funktion | `assets/js/` |
| Mannschafts-/Ligaquellen | `assets/python/config.py` und ggf. `assets/js/config/` |
| Scraper | `assets/python/scraper.py` |
| Galerie-Erzeugung | `assets/python/generate_gallery.py` |

## Wartungsregel

Neue Abstraktionen oder Build-Schritte nur einführen, wenn sie ein konkretes Wartungsproblem lösen. Für diese Vereinswebsite gilt bewusst: **wenige Ebenen, eindeutige Zuständigkeiten und möglichst wenig duplizierter Code.**
