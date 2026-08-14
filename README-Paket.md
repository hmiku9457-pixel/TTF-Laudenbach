# News-Baukasten-Paket

Dieses Paket erweitert den bereits funktionierenden Pages-CMS-Newseditor um genau fünf optionale Inhaltsblöcke:

1. Text – linksbündig oder zentriert
2. Zwei Spalten
3. Eventankündigung
4. Trenner
5. Abstand – klein, mittel oder groß

Die Eventankündigung ist **kein Pflichtbestandteil** eines Artikels. Sie erscheint nur, wenn der Redakteur diesen Block bewusst hinzufügt.

Bilder und Tabellen bleiben normale Rich-Text-Inhalte. Das Paket ändert ausschließlich deren Website-CSS:

* normale Artikel: volle Artikelbreite,
* Zwei-Spalten-Bereich: volle Breite der jeweiligen Spalte.

## Enthaltene Dateien

* `.pages.yml`
* `assets/python/generate_news.py`
* `assets/css/components/news-content.css`
* `content/news/training-bei-den-tischtennis-freunden-laudenbach.md`
* `content/news/vierelemente-sponsort-jacken.md`
* `docs/news-content-format.md`
* `docs/news-baukasten.md`

## Anwendung

1. ZIP im Root des Repositories entpacken und vorhandene Dateien überschreiben.
2. Änderungen normal mit deinem GitHub-Benutzer committen und nach `main` pushen.
3. Der bestehende Workflow **News generieren** startet aufgrund der geänderten News-/Generator-Dateien automatisch.
4. Workflow vollständig grün abwarten.
5. Pages CMS neu laden.
6. Bestehende zwei News öffnen und prüfen.
7. Einen Testartikel mit den fünf Blocktypen erstellen.
8. Desktop und Mobile prüfen.
9. Testartikel anschließend wieder über Pages CMS löschen.

Es wird **kein neuer temporärer Workflow** benötigt.
