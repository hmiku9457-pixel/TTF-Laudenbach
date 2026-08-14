# News-Content-Format

Die Dateien unter `content/news/` sind die einzige redaktionelle Quelle für die News der Website.
Das Format bleibt CMS-unabhängig: YAML-Frontmatter mit strukturierten `sections`; Rich-Text-Inhalte innerhalb der Blöcke bleiben Markdown.

## Pflichtfelder

* `title`
* `publish_at`
* `image`
* `image_alt`
* `sections` mit mindestens einem inhaltlichen Block

`summary` ist optional. Fehlt es, erzeugt der Generator einen Teaser aus dem gerenderten Artikelinhalt.

## Baukasten

Unter `sections` stehen frei sortierbare Blöcke.

### Text

```yaml
- type: text
  alignment: left
  body: |-
    Normaler **Rich Text**.
```

`alignment` ist `left` oder `center`.

### Zwei Spalten

```yaml
- type: two_columns
  left: |-
    Inhalt links.
  right: |-
    Inhalt rechts.
```

Desktop: zwei gleich breite Spalten. Mobil: untereinander.

### Eventankündigung

Der Eventblock ist vollständig optional und nur für Artikel gedacht, in denen ein konkreter Termin hervorgehoben werden soll.

```yaml
- type: event
  title: "Vereinsmeisterschaften"
  date: "2026-09-12"
  time: "14:00"
  location: "Bergstraßenhalle"
  description: |-
    Weitere Informationen zur Veranstaltung.
```

Pflicht innerhalb eines Eventblocks: `title`, `date`.
Optional: `time`, `location`, `description`.

### Trenner

```yaml
- type: divider
```

### Abstand

```yaml
- type: spacer
  size: medium
```

Erlaubte Größen: `small`, `medium`, `large`.

## Markdown innerhalb von Rich-Text-Feldern

Unterstützt:

* Absätze
* H1, H2 und H3
* Fett und Kursiv
* Links
* Listen
* Bilder
* Tabellen
* Blockquotes
* Code

Rohes HTML ist nicht erlaubt.

Das Titelbild benötigt weiterhin `image_alt`.
Inline-Bilder dürfen einen Alt-Text besitzen; Pages CMS kann sie auch mit `alt=""` speichern. Solche Bilder werden als dekorativ behandelt.

## Bilder und Tabellen

Bilder und Tabellen sind keine eigenen Baukasten-Blöcke.

Sie bleiben normale Rich-Text-Inhalte und werden per CSS automatisch auf die verfügbare Breite gesetzt:

* im normalen Artikel: volle Artikelbreite,
* im Zwei-Spalten-Bereich: volle Breite der jeweiligen Spalte.

Text bleibt im normalen Textblock auf eine gut lesbare Zeilenbreite begrenzt.

## Legacy-Kompatibilität

Der Generator akzeptiert weiterhin ältere News-Dateien mit einem normalen Markdown-Body unterhalb des Frontmatters.
Neue CMS-Artikel sollen ausschließlich `sections` verwenden.

## Veröffentlichungszeit

`publish_at` wird als lokale Zeit in `Europe/Berlin` interpretiert, sofern kein expliziter UTC-Offset angegeben ist.
Artikel mit einem Zeitpunkt in der Zukunft werden noch nicht in HTML, Übersicht, Slider oder Sitemap aufgenommen.

## Dateiname / URL

Der Markdown-Dateiname ist der dauerhafte Slug.

`content/news/saisonstart-2026.md`

erzeugt:

`/pages/news/saisonstart-2026.html`

Eine spätere Titeländerung ändert die URL nicht.

## Generierte Dateien

Nicht manuell bearbeiten:

* `pages/news/*.html`
* `pages/neuigkeiten.html`
* `assets/data/news.json`
* News-Einträge in `sitemap.xml`

Änderungen gehören in `content/news/`, `.pages.yml`, die Templates, das News-CSS oder den Generator.
