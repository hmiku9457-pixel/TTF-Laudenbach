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
* H1, H2 und H3
* Fett und Kursiv
* Links
* Aufzählungen und nummerierte Listen
* Bilder
* Tabellen
* Blockquotes
* Code

H1, H2 und H3 sind im Artikeltext erlaubt. Der Seitentitel bleibt unabhängig davon die Hauptüberschrift des News-Artikels.
Rohes HTML ist nicht erlaubt.

## Bilder

Bilder müssen im Repository unter `/assets/images/` liegen.
Neue CMS-Bilder sollen später bevorzugt unter `/assets/images/news/` abgelegt werden.
Das Titelbild benötigt weiterhin das Pflichtfeld `image_alt`. Inline-Bilder können einen Alt-Text besitzen; Pages CMS kann sie jedoch auch mit leerem `alt=""` speichern. Solche Inline-Bilder werden als dekorativ behandelt.

## Generierte Dateien

Nicht manuell bearbeiten:

* `pages/news/*.html`
* `pages/neuigkeiten.html`
* `assets/data/news.json`
* News-Einträge in `sitemap.xml`

Änderungen gehören in die Markdown-Datei, die Templates oder den Generator.

## Automatisierung

Der dauerhafte Workflow **News generieren** verwendet immer denselben Generator `assets/python/generate_news.py`.

Er startet:

* bei relevanten Änderungen auf `main` (`content/news/`, `assets/images/news/`, News-Templates, Generator oder Requirements),
* zweimal pro Stunde in der Zeitzone `Europe/Berlin` für geplante Veröffentlichungen,
* manuell über **Actions → News generieren → Run workflow**.

Jeder Lauf berechnet den vollständigen Sollzustand neu. Dadurch werden auch gelöschte Artikel, die News-Übersicht, die fünf Slider-Einträge und die News-Einträge der Sitemap konsistent synchronisiert.

Der manuelle Lauf ist zugleich der Rebuild-/Repair-Weg. Er fordert auch dann einen neuen GitHub-Pages-Build an, wenn keine generierte Datei geändert werden musste.

GitHub kann geplante Workflows in öffentlichen Repositories nach 60 Tagen ohne Repository-Aktivität automatisch deaktivieren. Falls eine geplante News nicht erscheint, zuerst den Workflow **News generieren** prüfen beziehungsweise manuell ausführen und einen deaktivierten Schedule wieder aktivieren.
