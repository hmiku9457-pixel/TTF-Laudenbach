# News CMS – Paket 1

Dieses einmalige Update-Paket baut die CMS-unabhängige News-Content-Pipeline auf.

## Enthalten

- Markdown als Source of Truth unter `content/news/`
- zentraler Python-Generator
- Artikel- und Übersichts-Template
- generierte Seite `pages/neuigkeiten.html`
- maximal 5 Einträge in `assets/data/news.json`
- automatische News-Einträge in `sitemap.xml`
- isolierte Styles für News-Artikel und News-Übersicht
- Migration der bisherigen Inhalte
- Validierung und Idempotenztest

## Noch nicht enthalten

- dauerhafter GitHub-Actions-Workflow für Publish/Schedule/Rebuild (Paket 2)
- Pages-CMS-Konfiguration und Benutzeroberfläche (Paket 3)

## Anwendung

1. ZIP entpacken.
2. Den Inhalt mit identischer Ordnerstruktur in das Repository-Root hochladen.
3. Diese Paketdateien committen.
4. Unter **Actions → News CMS Paket 1 anwenden → Run workflow** den Workflow manuell starten.
5. Nach erfolgreichem Lauf die Website auf Desktop und Mobil testen.

Der Workflow committet nur die produktiven Änderungen. Die Paketdateien unter
`tools/news-cms-package1/` und `.github/workflows/news-cms-package1.yml` werden nicht
durch den Bot verändert oder gelöscht.
