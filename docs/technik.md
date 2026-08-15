---
title: "Technikdokumentation – TTF Laudenbach"
---

# Technikdokumentation – TTF Laudenbach

Diese Dokumentation beschreibt Aufbau, Betrieb und Wartung der Vereinswebseite der **Tischtennis-Freunde Laudenbach**. Sie richtet sich an Personen, die die technische Betreuung der Webseite übernehmen oder bei Problemen nachvollziehen müssen, wo eine Änderung vorgenommen wird.

Die Webseite ist bewusst als **einfache statische Vereinswebseite** aufgebaut. Ziel ist nicht maximale technische Abstraktion, sondern eine Struktur, die auch nach längerer Zeit noch nachvollziehbar und mit überschaubarem Aufwand wartbar bleibt.

## 1. Technischer Überblick

Die Webseite besteht im Kern aus:

- statischen HTML-Seiten,
- modularen CSS-Dateien,
- JavaScript-Modulen für dynamische Funktionen,
- automatisch erzeugten JSON-Daten,
- Python-Skripten für Scraping und Generatoren,
- GitHub Actions für Automatisierung und Deployment,
- Pages CMS für die redaktionelle News-Pflege,
- GitHub Pages als Hosting.

Es gibt bewusst **keinen CSS- oder JavaScript-Buildprozess** und kein Framework. Die Dateien werden vom Browser direkt geladen.

Die zentrale öffentliche Domain ist:

`https://www.ttf-laudenbach.de`

Die Domain wird über die Datei `CNAME` mit GitHub Pages verbunden.

## 2. Grundprinzip der Wartung

Für Änderungen gilt grundsätzlich:

> Die jeweilige Quelle ändern – nicht das daraus automatisch erzeugte Ergebnis.

Beispiele:

- News-Inhalt: `content/news/*.md` bzw. Pages CMS bearbeiten.
- Generierte News-Seiten: **nicht** manuell bearbeiten.
- Spielbetriebsdaten: Quelle bzw. Scraper-Konfiguration bearbeiten.
- Generierte JSON-Dateien: **nicht** dauerhaft manuell korrigieren.
- Navigation: `components/header.html` bearbeiten.
- Footer: `components/footer.html` bearbeiten.
- Styling: das zuständige CSS-Modul bearbeiten.

Diese Trennung verhindert, dass manuelle Änderungen beim nächsten Workflow-Lauf wieder überschrieben werden.

## 3. Repository-Struktur

Die wichtigsten Bereiche des Repositories sind:

```text
/
├── .github/workflows/       GitHub-Actions-Workflows
├── assets/
│   ├── css/                 Gestaltung
│   ├── data/                automatisch erzeugte JSON-Daten
│   ├── images/              Bilder der Webseite
│   ├── js/                  JavaScript-Module
│   └── python/              Scraper und Generatoren
├── components/              gemeinsamer Header und Footer
├── content/news/            redaktionelle News-Quelldateien
├── docs/                    technische und redaktionelle Dokumentation
├── pages/                   Inhaltsseiten der Webseite
├── templates/               Vorlagen für generierte News-Seiten
├── .pages.yml               Pages-CMS-Konfiguration
├── 404.html                 Fehlerseite
├── CNAME                    Custom Domain für GitHub Pages
├── index.html               Startseite
├── robots.txt               Suchmaschinensteuerung
└── sitemap.xml              Sitemap
```

## 4. HTML-Seiten

Die Startseite liegt unter:

`index.html`

Weitere Seiten befinden sich unter:

`pages/`

Unterordner gruppieren zusammengehörige Bereiche, zum Beispiel Mannschaftsseiten, Dokumente oder Footer-Seiten.

Eine normale HTML-Seite bindet zentral ein:

```html
<link href="/assets/css/main.css" rel="stylesheet"/>
```

und am Ende:

```html
<script src="/assets/js/main.js" type="module"></script>
```

Header und Footer werden nicht auf jeder Seite kopiert, sondern über Platzhalter eingebunden:

```html
<div id="header-container"></div>
...
<div id="footer-container"></div>
```

Das JavaScript-Modul `assets/js/core/site-components.js` lädt anschließend die gemeinsamen Dateien.

## 5. Header und Navigation

Die zentrale Navigation liegt in:

`components/header.html`

Soll ein Menüpunkt hinzugefügt, entfernt oder umbenannt werden, erfolgt die Änderung dort.

Da alle Seiten denselben Header dynamisch laden, muss die Navigation nicht auf mehreren HTML-Seiten synchron gehalten werden.

Nach einer Änderung sollten mindestens Desktop- und Mobilansicht geprüft werden, insbesondere Dropdown-Menüs und Tastaturbedienung.

## 6. Footer

Der zentrale Footer liegt in:

`components/footer.html`

Dort befinden sich insbesondere:

- Links zu Kontakt, Impressum und Datenschutz,
- Sponsor-Links,
- Copyright-Ausgabe.

Sponsor-Ziele werden zusätzlich über die automatisch erzeugten Linkdaten verwaltet. Bei Sponsoränderungen deshalb auch `assets/python/config.py` prüfen.

## 7. CSS-Struktur

Zentraler Einstiegspunkt ist:

`assets/css/main.css`

Diese Datei importiert die einzelnen CSS-Module direkt. Es gibt keinen Build-Schritt.

Die Ordner sind grob aufgeteilt in:

- `assets/css/base/` – Reset und Grunddesign,
- `assets/css/layout/` – übergreifende Layoutbereiche,
- `assets/css/components/` – konkrete Komponenten.

Beispiele für Komponenten sind Tabellen, Galerie, News, Kontaktformular, Buttons und Accessibility-Regeln.

### Wartungsregel für CSS

Neue Regeln möglichst in das fachlich passende bestehende Modul einordnen.

Keine zusätzliche globale CSS-Datei anlegen, nur um einen einzelnen Konflikt schnell zu überschreiben. Das erschwert langfristig die Fehlersuche.

Responsive-Regeln gehören möglichst direkt zur jeweiligen Komponente.

## 8. JavaScript-Struktur

Zentraler Einstiegspunkt ist:

`assets/js/main.js`

Die JavaScript-Struktur ist aufgeteilt in:

- `core/` – gemeinsame technische Funktionen,
- `config/` – Konfigurationen,
- `features/` – konkrete Webseitenfunktionen,
- `utils/` – Hilfsfunktionen.

`main.js` prüft, welche Funktionen eine Seite tatsächlich benötigt, und lädt die entsprechenden Module dynamisch.

Beispiele:

- Tabellen,
- Galerie,
- Kontaktformular,
- News-Slider,
- Spielerlisten,
- externe Links,
- Einwilligung für eingebettete externe Inhalte,
- Animationen.

Dadurch müssen einzelne Seiten keine separaten JavaScript-Dateien manuell pflegen.

## 9. Tabellen und Spielbetriebsanzeige

Die Frontend-Konfiguration für Spielpläne und Tabellen liegt unter:

`assets/js/config/table-configs.js`

Dort wird festgelegt:

- welches HTML-Element befüllt wird,
- welche JSON-Datei geladen wird,
- welche Spalten angezeigt werden,
- welches Responsive-Verhalten verwendet wird,
- welche Leer- und Fehlermeldungen erscheinen.

Die eigentliche Ladefunktion liegt in:

`assets/js/features/tables.js`

JSON-Daten werden per `fetch` geladen und anschließend sicher als Text in Tabellenzellen geschrieben.

### Neue Mannschaft hinzufügen

Wenn künftig eine zusätzliche Mannschaft auf der Webseite dargestellt werden soll, sind typischerweise mehrere Stellen betroffen:

1. Scraper-Quelle in `assets/python/config.py` ergänzen.
2. Tabellen-/Spielplanquelle dort ergänzen.
3. Frontend-Konfiguration in `assets/js/config/table-configs.js` ergänzen.
4. entsprechende HTML-Seite bzw. Tabellen-IDs anlegen.
5. Navigation in `components/header.html` ergänzen.
6. Scraper manuell ausführen und Ergebnis prüfen.
7. Desktop- und Mobilansicht prüfen.

## 10. Automatische Daten aus click-TT / myTischtennis

Die Mannschafts-, Spielplan-, Tabellen- und Spielerdaten werden automatisch erzeugt.

Zentrale Dateien:

- `assets/python/config.py`
- `assets/python/scraper.py`
- `assets/python/validate_scraper_data.py`

Der Scraper verwendet Playwright und Chromium.

### Konfiguration

In `assets/python/config.py` stehen unter anderem:

- Saison,
- Spielplan-URLs,
- Tabellen-URLs,
- Spielerlisten,
- externe Links,
- Sponsoren.

Die erzeugten Dateien landen unter:

`assets/data/`

Dazu gehören beispielsweise:

- `spieleStartseite.json`
- `spieleHerren1.json`
- `tabelleHerren1.json`
- `spielerHerren.json`
- `links.json`

Diese Dateien sind **Ausgaben des Scrapers** und sollten nicht dauerhaft manuell gepflegt werden.

## 11. Auto-Update-Daten-Workflow

Workflow:

`.github/workflows/scraper.yml`

Anzeigename in GitHub Actions:

**Auto-Update Daten**

Der Workflow läuft:

- automatisch täglich,
- zusätzlich manuell über `workflow_dispatch`.

Der aktuelle Zeitplan ist `0 6 * * *`, also täglich um 06:00 UTC.

### Ablauf

Vereinfacht:

1. Repository auschecken.
2. Python 3.12 einrichten.
3. Playwright 1.62.0 und Chromium installieren.
4. bisherigen Datenstand sichern.
5. Scraper ausführen.
6. neue Daten zunächst als Kandidaten behandeln.
7. Kandidaten validieren.
8. nur gültige Daten übernehmen.
9. Änderungen committen und nach `main` pushen.
10. bei tatsächlichen Änderungen die Webseite deployen.

## 12. Schutz vor fehlerhaften Scraper-Daten

Vor der Übernahme prüft:

`assets/python/validate_scraper_data.py`

unter anderem:

- ob erwartete JSON-Dateien vorhanden sind,
- ob die Grundstruktur korrekt ist,
- ob Pflichtfelder vorhanden sind,
- ob wichtige Werte nicht leer sind,
- ob die Datenmenge ungewöhnlich stark eingebrochen ist.

Bei größeren unerwarteten Datenverlusten wird die Übernahme gestoppt.

Das schützt beispielsweise davor, dass eine temporär fehlerhafte externe Webseite leere oder unvollständige Daten auf die Vereinswebseite überträgt.

## 13. Saisonwechsel

Der Saisonwechsel ist der wichtigste planmäßige technische Wartungspunkt.

Aktuell steht die Saison zentral in:

`assets/python/config.py`

Beispiel:

```python
SAISON = "26--27"
```

Ein Saisonwechsel kann zusätzlich neue Liga-, Gruppen- oder Mannschafts-IDs auf click-TT/myTischtennis mit sich bringen. Deshalb reicht eine Änderung der Saisonnummer nicht zwingend aus.

### Empfohlener Ablauf zum Saisonwechsel

1. neue Saisonkennung in `assets/python/config.py` eintragen.
2. alle Spielplan-URLs kontrollieren.
3. alle Tabellen-URLs kontrollieren.
4. Spielerlisten kontrollieren.
5. neue Liga-/Gruppen-/Mannschafts-IDs übernehmen, falls erforderlich.
6. Änderungen committen.
7. **Auto-Update Daten** manuell starten.
8. bei absichtlich stark reduzierten Daten gegebenenfalls `allow_large_data_drop` aktivieren.
9. erzeugte JSON-Daten stichprobenartig prüfen.
10. Startseite und alle Mannschaftsseiten auf Desktop und Mobil kontrollieren.

### `allow_large_data_drop`

Der manuelle Workflow besitzt die Option:

`allow_large_data_drop`

Diese Option umgeht ausschließlich den Schutz gegen einen ungewöhnlich großen Rückgang der Datenmenge.

Sie sollte nur verwendet werden, wenn der Rückgang **erwartet und geprüft** ist, beispielsweise bei einem Saisonwechsel.

Sie ist kein allgemeiner „Fehler ignorieren“-Schalter.

## 14. Debugging des Scrapers

Schlägt der Scraper-Workflow fehl, lädt GitHub Actions vorhandene Debug-Dateien als Artefakt hoch.

Das Debug-Artefakt wird aktuell sieben Tage aufbewahrt.

Bei der Fehlersuche zuerst prüfen:

1. welcher Workflow-Schritt fehlgeschlagen ist,
2. die konkrete Fehlermeldung im Action-Log,
3. vorhandenes `scraper-debug-...`-Artefakt,
4. ob click-TT/myTischtennis sein HTML oder URLs geändert hat,
5. ob nur eine Mannschaft oder alle Datenquellen betroffen sind.

Nicht sofort den Validator deaktivieren. Er verhindert, dass fehlerhafte Daten produktiv werden.

## 15. News-System

Die News besitzen eine klare Source-of-Truth-Struktur.

Redaktionelle Quelle:

`content/news/*.md`

CMS-Konfiguration:

`.pages.yml`

Templates:

- `templates/news-article.html`
- `templates/news-overview.html`

Generator:

`assets/python/generate_news.py`

Abhängigkeiten:

`assets/python/news_requirements.txt`

Generierte Ausgaben:

- `pages/news/*.html`
- `pages/neuigkeiten.html`
- `assets/data/news.json`
- News-Einträge in `sitemap.xml`

Die generierten Dateien dürfen nicht als eigentliche News-Quelle verwendet werden.

## 16. Pages CMS

Pages CMS dient als redaktionelle Oberfläche für die News und als Lesebereich für die Dokumentation.

Die Konfiguration liegt in:

`.pages.yml`

Die Datei definiert:

- News-Felder,
- Medienordner,
- Inhaltsblöcke,
- Feldvalidierung,
- erlaubte Operationen,
- Dokumentationsansichten.

Änderungen an `.pages.yml` sollten besonders vorsichtig erfolgen, weil ein YAML-Fehler die CMS-Oberfläche beeinträchtigen kann.

Nach Änderungen:

1. YAML-Syntax prüfen,
2. CMS neu laden,
3. eine vorhandene News öffnen,
4. bei Feldänderungen testweise einen Beitrag bearbeiten,
5. Dokumentationsbereich kontrollieren.

## 17. News-Format

Das genaue neutrale Dateiformat ist zusätzlich dokumentiert in:

`docs/news-content-format.md`

Neue News verwenden YAML-Frontmatter und strukturierte `sections`.

Pflichtfelder sind insbesondere:

- `title`
- `publish_at`
- `image`
- `image_alt`
- `sections`

`summary` ist optional.

Der Generator validiert Inhalte vor der Ausgabe. Unter anderem wird rohes HTML in Rich-Text-Feldern nicht akzeptiert.

## 18. Geplante News

`publish_at` steuert den Veröffentlichungszeitpunkt.

Zeiten ohne expliziten Offset werden als `Europe/Berlin` interpretiert.

Eine News mit einem zukünftigen Zeitpunkt darf bereits im Repository liegen, erscheint aber noch nicht:

- als Artikelseite,
- in der News-Übersicht,
- im News-Slider,
- in der Sitemap.

## 19. News-generieren-Workflow

Workflow:

`.github/workflows/generate-news.yml`

Anzeigename:

**News generieren**

Er startet bei Änderungen an:

- `content/news/**`
- `assets/images/news/**`
- News-Generator,
- News-Abhängigkeiten,
- News-Templates,
- dem Workflow selbst.

Zusätzlich prüft er geplante Veröffentlichungen zweimal pro Stunde um Minute 17 und 47 in `Europe/Berlin`.

### Ablauf

1. Repository auschecken.
2. Python 3.13 einrichten.
3. News-Abhängigkeiten installieren.
4. Generator ausführen.
5. generierte Dateien vergleichen.
6. Änderungen committen.
7. bei Push-Konflikten bis zu drei Synchronisationsversuche durchführen.
8. anschließend zentral deployen.

## 20. News-Slider

`assets/data/news.json` wird vom News-Generator erstellt.

Der Slider enthält maximal die fünf neuesten veröffentlichten News.

Die Begrenzung steht im Generator als:

```python
SLIDER_LIMIT = 5
```

Eine Änderung dieser Zahl verändert die Anzahl der erzeugten Slider-Einträge. Danach auch Layout und Bedienbarkeit des Sliders prüfen.

## 21. Löschen von News

Wird eine Markdown-News gelöscht, entfernt der Generator beim nächsten Lauf auch die dazugehörige automatisch erzeugte Artikelseite, sofern sie als generierte News-Seite erkannt wird.

Außerdem werden Übersicht, Slider und Sitemap neu synchronisiert.

Deshalb generierte HTML-Dateien nicht separat löschen oder behalten wollen. Die Markdown-Quelle entscheidet über den Bestand.

## 22. Galerie

Galerie-Generator:

`assets/python/generate_gallery.py`

Ausgabe:

`assets/data/gallerie.json`

Workflow:

`.github/workflows/generate-gallery-json.yml`

Anzeigename:

**Generate Gallery JSON**

Der Workflow reagiert auf relevante Bildänderungen unter `assets/images/` sowie auf Änderungen am Galerie-Generator.

`assets/images/seo/**` und `assets/images/news/**` sind im Workflow ausdrücklich vom Galerie-Trigger ausgenommen.

## 23. Galerie-Struktur

Der Generator durchsucht Bilder unter `assets/images/`.

Bilder direkt im Stamm dieses Ordners landen in der allgemeinen Galerie.

Unterordner werden als eigene Galeriegruppen interpretiert. Der Ordnername wird als Titel verwendet und daraus eine technische ID erzeugt.

Unterstützte Bildformate des Generators:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.gif`

Der Generator erzeugt automatisch Alt-Texte aus Galerie- und Dateinamen.

Daher Bilder möglichst sinnvoll benennen.

## 24. Bekannter Wartungshinweis zur Galerie

Im aktuellen Stand besteht eine kleine Inkonsistenz zwischen Workflow/README und Generator:

- der Workflow behandelt `assets/images/news/**` als **keine Galeriequelle**,
- der Galerie-Generator selbst schließt in seiner internen Ordnerliste aktuell jedoch nur `seo` explizit aus.

Das bedeutet: Wird der Galerie-Generator aus einem anderen Grund ausgeführt, kann der Ordner `assets/images/news/` vom Generator mit erfasst werden.

Bei einer späteren Wartung sollte `news` im Generator ebenfalls explizit ausgeschlossen werden, damit Implementierung und dokumentiertes Verhalten vollständig übereinstimmen.

Bis dahin nach Galerie-Läufen `assets/data/gallerie.json` kurz auf eine unerwünschte News-Galerie kontrollieren.

## 25. Externe Links und Sponsoren

Die zentralen Linkquellen stehen in:

`assets/python/config.py`

Der Scraper erzeugt daraus:

`assets/data/links.json`

Die Frontend-Logik lädt diese Daten über:

`assets/js/features/links.js`

Soll ein externer Link oder Sponsor geändert werden, nicht nur die erzeugte JSON-Datei bearbeiten, sondern die Quelle in `config.py`.

Bei Sponsoränderungen zusätzlich prüfen, ob im gemeinsamen Footer ein entsprechender sichtbarer Eintrag angepasst werden muss.

## 26. Kontaktformular

Die Kontaktseite liegt unter:

`pages/footer/kontakt.html`

Das Formular verwendet Formspree als externen Formular-Dienst.

Die JavaScript-Logik liegt unter:

`assets/js/features/contact-form.js`

Das Skript sendet das Formular asynchron und zeigt Erfolgs-, Server- und Verbindungsfehler im Formular an.

Wird der Formspree-Endpunkt geändert, muss die `action` des Formulars in der Kontaktseite angepasst werden.

Anschließend eine echte Testnachricht senden und den Empfang prüfen.

## 27. Externe eingebettete Inhalte

Für externe Iframes existiert eine Einwilligungslogik unter:

`assets/js/features/iframe-consent.js`

Erlaubte Embed-Hosts werden sicherheitsseitig in:

`assets/js/utils/safe-url.js`

begrenzt.

Aktuell sind dort insbesondere Google-/Google-Maps- und YouTube-Domains vorgesehen.

Soll ein neuer externer Anbieter eingebunden werden, reicht deshalb nicht immer nur neues HTML. Gegebenenfalls muss der Host zusätzlich in der Allowlist ergänzt werden.

Datenschutzseite und Einwilligungstext anschließend ebenfalls prüfen.

## 28. GitHub Pages Deployment

Die Veröffentlichung erfolgt zentral über:

`.github/workflows/deploy-pages.yml`

Anzeigename:

**Website veröffentlichen**

Der Workflow kann gestartet werden durch:

- relevante Pushes auf `main`,
- manuellen Start,
- Aufruf durch andere Workflows.

Er deployed immer den aktuellen Stand von `main`.

## 29. Öffentliches Deployment-Artefakt

Vor der Veröffentlichung wird ein separates `.pages-site`-Artefakt erstellt.

Öffentlich ausgeliefert werden insbesondere:

- `index.html`
- `404.html`
- `CNAME`
- `robots.txt`
- `sitemap.xml`
- `components/`
- `pages/`
- `assets/css/`
- `assets/data/`
- `assets/images/`
- `assets/js/`

Technische Quellen werden nicht in das Pages-Artefakt aufgenommen.

Dazu gehören insbesondere:

- `assets/python/`
- `content/news/`
- `templates/`
- `.pages.yml`
- `docs/`
- Workflow-Dateien.

Wichtig: Das GitHub-Repository selbst ist öffentlich. Nicht deployte Dateien sind daher **nicht geheim**, sondern lediglich kein Bestandteil der eigentlichen Website-Auslieferung.

Keine Zugangsdaten, Tokens oder Passwörter im Repository speichern.

## 30. Wann wird automatisch deployed?

### Direkte Webseitenänderungen

Änderungen an öffentlichen HTML-, CSS-, JavaScript- und bestimmten Asset-Dateien können den Deployment-Workflow direkt auslösen.

### News

Der News-Workflow generiert zuerst die News-Ausgaben und ruft danach den zentralen Deployment-Workflow auf.

### Galerie

Der Galerie-Workflow generiert zuerst `gallerie.json` und deployt anschließend zentral.

### Scraper

Der Scraper deployt nur, wenn tatsächlich neue oder geänderte Daten übernommen und committed wurden.

## 31. Repository-Schreibkonkurrenz

News-, Galerie- und Scraper-Workflows können Dateien in `main` committen.

Sie verwenden deshalb gemeinsam die GitHub-Actions-Concurrency-Gruppe:

`repository-writer`

Dadurch sollen parallele automatische Schreibzugriffe auf das Repository vermieden werden.

Bei manuellen Änderungen während eines laufenden Workflows können trotzdem neue Commits entstehen. Deshalb bei unerklärlichen Push-/Rebase-Problemen den aktuellen `main`-Stand und die Action-Logs prüfen.

## 32. Manueller Deployment-Repair

Wenn die Webseite nicht dem aktuellen `main`-Stand entspricht:

1. GitHub öffnen.
2. Repository auswählen.
3. **Actions** öffnen.
4. **Website veröffentlichen** auswählen.
5. **Run workflow** starten.
6. nach erfolgreichem Lauf Webseite prüfen.

Wenn speziell News inkonsistent sind:

1. **Actions** öffnen.
2. **News generieren** auswählen.
3. **Run workflow** starten.
4. der Workflow erzeugt die News neu und ruft anschließend selbst das Deployment auf.

## 33. Domain und DNS

Die Custom Domain steht in:

`CNAME`

Aktueller Wert:

`www.ttf-laudenbach.de`

DNS wird außerhalb des Repositories beim Domainanbieter verwaltet.

Bei Änderungen an Domain oder DNS immer bedenken:

- `CNAME` und DNS müssen zusammenpassen,
- GitHub Pages muss die Domain akzeptieren,
- HTTPS-Zertifikate werden erst nach korrekter DNS-Konfiguration zuverlässig bereitgestellt,
- DNS- und Zertifikatsänderungen können verzögert wirksam werden.

Die Domain nicht testweise dauerhaft im Repository ändern, ohne auch die DNS-Seite mitzudenken.

## 34. Sitemap und robots.txt

`robots.txt` verweist auf:

`https://www.ttf-laudenbach.de/sitemap.xml`

Die Sitemap liegt im Repository als:

`sitemap.xml`

Statische Seiten werden dort direkt gepflegt. Die News-Einträge sowie die News-Übersicht werden vom News-Generator synchronisiert.

Bei neuen normalen HTML-Seiten prüfen, ob die Seite zusätzlich in der Sitemap aufgenommen werden soll.

## 35. Lokale Vorschau

Da die Webseite ES-Module und `fetch` verwendet, sollten HTML-Dateien nicht einfach per Doppelklick als `file://` geöffnet werden.

Für eine einfache lokale Vorschau im Repository-Stamm genügt beispielsweise Python:

```bash
python -m http.server 8000
```

Danach im Browser öffnen:

`http://localhost:8000`

Wichtig ist, den Server im Repository-Stamm zu starten, damit absolute Pfade wie `/assets/...` korrekt funktionieren.

## 36. News lokal generieren

Für lokale Arbeiten am News-System:

```bash
python -m pip install -r assets/python/news_requirements.txt
python assets/python/generate_news.py
```

Der Generator verändert generierte Dateien im Arbeitsverzeichnis.

Danach mit Git prüfen, welche Dateien geändert wurden.

Für reproduzierbare Tests kann der Generator optional einen festen Zeitpunkt erhalten:

```bash
python assets/python/generate_news.py --now 2026-09-01T12:00:00
```

## 37. Galerie lokal generieren

Die Galerie benötigt für den Generator selbst keine zusätzlichen Python-Pakete.

Ausführung:

```bash
python assets/python/generate_gallery.py
```

Danach insbesondere prüfen:

`assets/data/gallerie.json`

## 38. Scraper lokal ausführen

Der produktive GitHub-Workflow ist für normale Aktualisierungen vorzuziehen, weil er Sicherung, Validierung und Debug-Artefakte bereits enthält.

Für lokale Entwicklung wird Playwright benötigt, sinngemäß wie im Workflow:

```bash
python -m pip install "playwright==1.62.0"
python -m playwright install chromium
python assets/python/scraper.py
```

Achtung: Der Scraper schreibt in `assets/data/`.

Vor lokalen Experimenten deshalb Git-Status prüfen und keine ungeprüften Daten committen.

## 39. Git-Grundregel für Wartungsarbeiten

Vor größeren Änderungen:

```bash
git status
git pull
```

Nach Änderungen mindestens prüfen:

```bash
git diff
git diff --check
```

Generierte Dateien nur committen, wenn sie zur Änderung gehören oder vom vorgesehenen Generator erzeugt wurden.

Bei umfangreicheren technischen Änderungen möglichst einen eigenen Branch verwenden.

## 40. Typische Änderung – wo muss ich hin?

| Änderung | Zuständige Datei / Bereich |
|---|---|
| Navigation | `components/header.html` |
| Footer | `components/footer.html` |
| normaler Seiteninhalt | jeweilige Datei unter `pages/` bzw. `index.html` |
| allgemeines Styling | `assets/css/` |
| Frontend-Funktion | `assets/js/` |
| Tabellen-Frontend | `assets/js/config/table-configs.js` und `assets/js/features/tables.js` |
| Saison / Ligaquellen | `assets/python/config.py` |
| Scraper-Logik | `assets/python/scraper.py` |
| Scraper-Sicherheitsprüfung | `assets/python/validate_scraper_data.py` |
| News-Inhalt | Pages CMS / `content/news/*.md` |
| News-CMS-Felder | `.pages.yml` |
| News-Layout | `templates/` und `assets/css/components/news-content.css` |
| News-Generator | `assets/python/generate_news.py` |
| News-Slider-Frontend | `assets/js/features/news-slider.js` |
| Galerie-Daten | `assets/python/generate_gallery.py` |
| Galerie-Frontend | `assets/js/features/gallery.js` |
| externe Links / Sponsoren | `assets/python/config.py` |
| Kontaktformular | `pages/footer/kontakt.html`, `assets/js/features/contact-form.js` |
| externe Iframes | `assets/js/features/iframe-consent.js`, `assets/js/utils/safe-url.js` |
| Deployment | `.github/workflows/deploy-pages.yml` |
| Domain | `CNAME` und DNS-Anbieter |
| Suchmaschinen-Sitemap | `sitemap.xml`, teilweise News-Generator |

## 41. Fehler: Webseite zeigt alte Version

Prüfreihenfolge:

1. Ist die gewünschte Änderung wirklich in `main`?
2. Ist der zuständige Workflow erfolgreich gelaufen?
3. Bei normaler Seitenänderung: **Website veröffentlichen** prüfen.
4. Bei News: **News generieren** prüfen.
5. Bei Galerie: **Generate Gallery JSON** prüfen.
6. Bei Spielbetriebsdaten: **Auto-Update Daten** prüfen.
7. gegebenenfalls **Website veröffentlichen** manuell starten.
8. Browsercache ausschließen bzw. Seite hart neu laden.

## 42. Fehler: News erscheint nicht

Prüfen:

1. Liegt die Markdown-Datei unter `content/news/`?
2. Ist `publish_at` bereits erreicht?
3. Sind Titelbild und Bildpfade gültig?
4. Sind alle Pflichtfelder vorhanden?
5. Ist der Lauf **News generieren** erfolgreich?
6. Wurde die HTML-Seite unter `pages/news/` erzeugt?
7. Ist der Beitrag in `pages/neuigkeiten.html` enthalten?
8. Ist der Beitrag gegebenenfalls unter den fünf neuesten und damit im Slider?

Bei einem Generatorfehler immer zuerst die konkrete Validierungsfehlermeldung beheben und nicht die generierte HTML-Datei manuell erzeugen.

## 43. Fehler: Spielplan oder Tabelle leer

Prüfen:

1. entsprechenden JSON-Datenstand unter `assets/data/` ansehen.
2. **Auto-Update Daten** prüfen.
3. Action-Log auf Scraper- oder Validierungsfehler prüfen.
4. externe click-TT/myTischtennis-URL aus `config.py` kontrollieren.
5. prüfen, ob Saison, Liga oder Mannschafts-ID noch stimmt.
6. bei Workflow-Fehler Debug-Artefakt ansehen.

Ist die JSON-Datei korrekt, aber die Webseite zeigt nichts, Frontend-Konfiguration und HTML-Ziel-ID prüfen.

## 44. Fehler: Galerie zeigt falsche oder keine Bilder

Prüfen:

1. liegt das Bild im erwarteten Ordner?
2. wird die Dateiendung unterstützt?
3. **Generate Gallery JSON** erfolgreich?
4. `assets/data/gallerie.json` kontrollieren.
5. Browser-Konsole auf Ladefehler prüfen.
6. bekannten Hinweis zu `assets/images/news/` beachten.

## 45. Fehler: Kontaktformular sendet nicht

Prüfen:

1. Browser-Konsole und Netzwerk-Tab ansehen.
2. Formspree-Endpunkt in `pages/footer/kontakt.html` prüfen.
3. Formspree-Konto bzw. Zieladresse kontrollieren.
4. Datenschutzhinweis und Checkbox dürfen nicht versehentlich entfernt worden sein.
5. mit einer echten Testnachricht verifizieren.

## 46. Fehler: CMS funktioniert nicht korrekt

Prüfen:

1. `.pages.yml` auf gültiges YAML prüfen.
2. Pfade und Feldnamen kontrollieren.
3. prüfen, ob die referenzierten Dateien tatsächlich existieren.
4. Pages CMS neu laden.
5. GitHub-Berechtigungen bzw. CMS-Verbindung prüfen.
6. letzte Änderung an `.pages.yml` mit Git vergleichen.

Bei einem Konfigurationsfehler die letzte bekannte funktionierende Version über Git wiederherstellen, statt die News-Dateien umzustrukturieren.

## 47. Rollback über Git

Ein großer Vorteil der Architektur ist, dass Änderungen versioniert sind.

Bei einem fehlerhaften technischen Update:

1. problematischen Commit identifizieren.
2. möglichst einen normalen Revert-Commit erstellen.
3. nicht unnötig die Git-Historie von `main` umschreiben.
4. anschließend zuständige Generatoren bei Bedarf neu ausführen.
5. Deployment kontrollieren.

Bei generierten Daten immer überlegen, ob der Fehler in der Quelle liegt. Ein Revert der JSON-Ausgabe allein kann beim nächsten automatischen Lauf wieder überschrieben werden.

## 48. Sicherheit

Für diese statische Vereinsseite gelten einige einfache Regeln:

- keine Passwörter oder API-Tokens in HTML, JavaScript, Markdown oder Dokumentation speichern,
- keine GitHub-Secrets in Logs ausgeben,
- externe URLs nur über die vorgesehenen sicheren Mechanismen einbinden,
- Abhängigkeiten und GitHub Actions gelegentlich aktualisieren,
- technische Änderungen vor dem Merge prüfen,
- bei neuen externen Diensten Datenschutzseite anpassen.

Da Browsercode öffentlich ausgeliefert wird, kann JavaScript grundsätzlich keine geheimen Zugangsdaten sicher enthalten.

## 49. Abhängigkeiten

Die Webseite besitzt bewusst nur wenige externe technische Abhängigkeiten.

Wichtige Beispiele:

- GitHub / GitHub Actions / GitHub Pages,
- Pages CMS,
- Python,
- Playwright + Chromium für den Scraper,
- Python-Pakete aus `news_requirements.txt` für den News-Generator,
- Formspree für das Kontaktformular,
- click-TT/myTischtennis als Datenquelle,
- externe Karten-/Medienanbieter nur nach Einwilligung.

Bei einem Ausfall eines externen Dienstes zunächst unterscheiden, ob die eigentliche Vereinswebseite betroffen ist oder nur die jeweilige Zusatzfunktion.

## 50. Wartungsintervalle

Es ist kein aufwendiger regelmäßiger Technikbetrieb notwendig.

Sinnvolle Kontrollen sind:

### Gelegentlich

- GitHub Actions auf wiederkehrende Fehler prüfen,
- Kontaktformular testen,
- externe Links stichprobenartig prüfen,
- Browser-Konsole bei sichtbaren Problemen ansehen.

### Vor einer neuen Saison

- Saisonkennung und click-TT-URLs prüfen,
- Mannschaftsstruktur prüfen,
- Scraper manuell testen,
- alle Mannschaftsseiten prüfen.

### Nach größeren GitHub-/Python-/Pages-CMS-Änderungen

- Workflows testen,
- CMS testen,
- Desktop und Mobil prüfen.

## 51. Was nicht unnötig geändert werden sollte

Die Architektur wurde bewusst vereinfacht.

Ohne konkreten Bedarf sollten daher nicht eingeführt werden:

- großes JavaScript-Framework,
- CSS-Bundler,
- komplexes Node-Buildsystem,
- Datenbank nur für statische Inhalte,
- zusätzliche CMS-Schicht neben Pages CMS,
- unnötige Abstraktions- oder Wrapper-Ebenen.

Neue Technik sollte ein konkretes Wartungsproblem lösen und nicht nur „moderner“ wirken.

## 52. Übergabe an eine neue technische Betreuung

Bei einem Verantwortungswechsel sollten mindestens übergeben werden:

- GitHub-Repository-Zugriff,
- GitHub-Pages-/Repository-Berechtigungen,
- Pages-CMS-Zugriff bzw. Verbindung,
- Zugriff auf Domain/DNS,
- Zugriff auf Formspree,
- Ansprechpartner für Vereinsinhalte,
- diese Technikdokumentation,
- Redaktionshandbuch.

Passwörter nicht in dieser Dokumentation hinterlegen. Zugangsdaten separat und sicher übergeben.

## 53. Empfohlener Übernahmecheck

Eine neue technische Betreuung sollte einmal durchführen:

- [ ] Repository öffnen und Struktur nachvollziehen.
- [ ] GitHub Actions öffnen.
- [ ] **Website veröffentlichen** manuell erfolgreich ausführen.
- [ ] **News generieren** manuell erfolgreich ausführen.
- [ ] **Generate Gallery JSON** manuell erfolgreich ausführen.
- [ ] **Auto-Update Daten** manuell erfolgreich ausführen oder mindestens den letzten erfolgreichen Lauf prüfen.
- [ ] Pages CMS öffnen.
- [ ] Redaktionshandbuch und Technikdokumentation im CMS öffnen.
- [ ] eine vorhandene News testweise öffnen, ohne sie unnötig zu verändern.
- [ ] Startseite auf Desktop und Mobil prüfen.
- [ ] mindestens eine Mannschaftsseite prüfen.
- [ ] Galerie prüfen.
- [ ] Kontaktformular testweise absenden.
- [ ] Zugriff auf Domain/DNS und Formspree sicherstellen.

## 54. Wichtigste Recovery-Regeln

Wenn etwas nicht funktioniert:

1. **Nicht blind generierte Dateien reparieren.**
2. GitHub-Actions-Log lesen.
3. Zuständige Source-of-Truth-Datei ermitteln.
4. letzte Änderungen mit Git vergleichen.
5. Fehler an der Quelle korrigieren.
6. zuständigen Generator oder Workflow neu ausführen.
7. danach die öffentliche Webseite testen.

## 55. Weitere Dokumentation

Ergänzende Dateien im Repository:

- `docs/redaktion.md` – Bedienung für Redakteure,
- `docs/news-content-format.md` – technisches News-Dateiformat,
- `docs/news-baukasten.md` – ergänzende News-Baukasten-Dokumentation,
- `docs/pages-deployment.md` – Details zum GitHub-Pages-Deployment,
- `README.md` – kompakter Architekturüberblick.

## 56. Dokumentstand

**Projekt:** Vereinswebseite TTF Laudenbach  
**Dokument:** Technikdokumentation  
**Stand:** August 2026

Die Dokumentation beschreibt den technischen Stand zum Zeitpunkt der Übergabe. Werden Architektur, Workflows, externe Dienste oder zentrale Pfade geändert, sollte dieses Dokument im selben Änderungspaket aktualisiert werden.
