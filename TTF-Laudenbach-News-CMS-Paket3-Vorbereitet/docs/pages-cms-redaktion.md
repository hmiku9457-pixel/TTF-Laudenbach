# Pages CMS – Kurzanleitung für Redakteure

## Neue News erstellen

1. Pages CMS öffnen und anmelden.
2. **Neuigkeiten** auswählen.
3. **Neue News** erstellen.
4. Titel eingeben.
5. Veröffentlichungszeit prüfen.
6. Titelbild auswählen oder hochladen.
7. Bildbeschreibung eintragen.
8. Artikel im Editor schreiben.
9. Optional eine Kurzbeschreibung eintragen.
10. Speichern/Veröffentlichen.

Danach übernimmt GitHub automatisch die technische Veröffentlichung.

## Veröffentlichung planen

Im Feld **Veröffentlichung** kann ein zukünftiger Zeitpunkt gewählt werden.

Der Artikel wird bereits gespeichert, erscheint auf der Website aber erst, wenn dieser Zeitpunkt erreicht ist und der automatische News-Workflow gelaufen ist.

## Kurzbeschreibung

Die Kurzbeschreibung ist optional.

Wenn sie leer bleibt, erzeugt die Website automatisch einen kurzen Teaser aus dem Artikeltext.

## Artikel formatieren

Für normale News können verwendet werden:

* Absätze
* Fett und Kursiv
* H2/H3-Zwischenüberschriften
* Aufzählungen und nummerierte Listen
* Links
* Bilder
* Tabellen
* Zitate

Wichtig: Keine zusätzliche Überschrift 1/H1 im Artikel verwenden. Der News-Titel ist bereits die Hauptüberschrift.

## Bilder

Beim Titelbild und bei Bildern im Artikel immer einen sinnvollen Alt-Text bzw. eine Bildbeschreibung angeben.

Beispiel:

Gut:
`Jugendmannschaft der TTF Laudenbach beim Saisonauftakt`

Nicht hilfreich:
`Bild1`

## Bestehende News bearbeiten

Eine News öffnen, Inhalt ändern und speichern.

Der Dateiname und damit die bestehende Artikel-URL bleiben auch bei einer Titeländerung erhalten.

## News löschen

Nur löschen, wenn der Artikel wirklich entfernt werden soll.

Nach dem Löschen synchronisiert der GitHub-Workflow automatisch:

* Artikelseite
* News-Übersicht
* Startseiten-Slider
* Sitemap

## Wenn etwas nicht erscheint

Nicht die generierten HTML-Dateien oder `news.json` manuell bearbeiten.

Den technischen Administrator informieren. Die redaktionelle Quelle ist immer die News im CMS bzw. die zugehörige Markdown-Datei unter `content/news/`.
