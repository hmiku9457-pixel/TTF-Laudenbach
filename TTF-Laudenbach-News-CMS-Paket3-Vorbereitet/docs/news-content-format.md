# News-Content-Format

Die Dateien unter `content/news/` sind die einzige redaktionelle Quelle für die News der Website.
Das Format ist bewusst CMS-unabhängig: YAML-Frontmatter plus Markdown.

## Beispiel

```markdown
---
title: "Vereinsmeisterschaften 2026"
publish_at: "2026-09-12T18:00"
summary: "Kurzer optionaler Teaser für Slider und Übersicht."
image: "/assets/images/news/vereinsmeisterschaften-2026.jpg"
image_alt: "Teilnehmer der Vereinsmeisterschaften 2026"
---

Der eigentliche Artikel beginnt hier.

## Zwischenüberschrift

Normaler Text mit **Fettschrift**, *Kursivschrift*, [Links](https://example.org)
und Listen.

| Platz | Name |
| --- | --- |
| 1. | Beispiel |
```

## Pflichtfelder

* `title`
* `publish_at`
* `image`
* `image_alt`
* Markdown-Body

`summary` ist optional. Fehlt es, erzeugt der Generator einen Teaser aus dem Artikeltext.

## Veröffentlichungszeit

`publish_at` wird als lokale Zeit in `Europe/Berlin` interpretiert, sofern kein expliziter UTC-Offset angegeben ist.
Artikel mit einem Zeitpunkt in der Zukunft werden noch nicht in HTML, Übersicht, Slider oder Sitemap aufgenommen.

## Dateiname / URL

Der Markdown-Dateiname ist der dauerhafte Slug und muss aus Kleinbuchstaben, Ziffern und Bindestrichen bestehen.

Beispiel:

`content/news/saisonstart-2026.md`

erzeugt:

`/pages/news/saisonstart-2026.html`

Eine spätere Änderung des Titels ändert die URL nicht.

## Unterstütztes Markdown

* Absätze
* H2 und H3
* Fett und Kursiv
* Links
* Aufzählungen und nummerierte Listen
* Bilder
* Tabellen
* Blockquotes
* Code

Eine zusätzliche H1 ist nicht erlaubt, weil der Artikeltitel bereits die H1 der Seite ist.
Rohes HTML ist nicht erlaubt.

## Bilder

Bilder müssen im Repository unter `/assets/images/` liegen.
Pages CMS speichert neue News-Bilder unter `/assets/images/news/`.
Bilder im Artikel benötigen einen nicht-leeren Alt-Text.

## Generierte Dateien

Nicht manuell bearbeiten:

* `pages/news/*.html`
* `pages/neuigkeiten.html`
* `assets/data/news.json`
* News-Einträge in `sitemap.xml`

Änderungen gehören in die Markdown-Datei, die Templates oder den Generator.
