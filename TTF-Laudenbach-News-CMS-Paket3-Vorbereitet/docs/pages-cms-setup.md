# Pages CMS – Einrichtung und Administration

## Zweck

Pages CMS ist nur die Redaktionsoberfläche für die News.
Die dauerhafte Quelle bleibt `content/news/*.md` im GitHub-Repository.
Die bestehende Action **News generieren** übernimmt weiterhin HTML, Slider, Übersicht und Sitemap.

## Einmalige Einrichtung

1. Das Phase-3-Paket in das Root des Repositories übernehmen und nach `main` committen.
2. Prüfen, dass `.pages.yml` im Repository-Root vorhanden ist.
3. Die gehostete Pages-CMS-Anwendung öffnen.
4. Als technischer Administrator mit GitHub anmelden.
5. Die Pages-CMS-GitHub-App für das Repository `TTF-Laudenbach` installieren/freigeben.
6. Repository und Branch `main` öffnen.
7. Prüfen, dass links die Collection **Neuigkeiten** erscheint.
8. Die beiden vorhandenen News öffnen und kontrollieren, ohne sie zunächst zu verändern.

## Konfiguration

`.pages.yml` stellt ausschließlich `content/news/` als News-Collection bereit.

Redaktionelle Felder:

* Titel
* Veröffentlichung
* optionale Kurzbeschreibung
* Titelbild
* Bildbeschreibung
* Artikel als Rich-Text

Neue News-Bilder werden unter `assets/images/news/` gespeichert.

Beim Erstellen wird aus dem Titel automatisch ein Dateiname erzeugt.
Danach ist das Umbenennen der Datei im CMS deaktiviert. Eine spätere Titeländerung ändert damit die bestehende Artikel-URL nicht.

## Veröffentlichungszeit

Das Feld **Veröffentlichung** ist ein Date-Time-Feld und wird bei einem neuen Artikel mit der aktuellen lokalen Zeit vorbelegt.

* Zeitpunkt jetzt/in der Vergangenheit: Artikel wird beim nächsten Generatorlauf veröffentlicht.
* Zeitpunkt in der Zukunft: Datei liegt bereits in GitHub, wird von der Website aber bis zum Zeitpunkt ignoriert.
* Die GitHub Action prüft geplante Veröffentlichungen zweimal pro Stunde.

Hinweis: Das öffentliche GitHub-Repository enthält einen geplanten Artikel bereits vor seiner Veröffentlichung auf der Website. Für vertrauliche Vorab-Inhalte ist dieses Verfahren nicht vorgesehen.

## Redakteure ohne GitHub-Account

Nach erfolgreichem Administrator-Test können Redakteure in Pages CMS per E-Mail als Collaborators eingeladen werden.

Collaborators dürfen Content und Medien bearbeiten, aber nicht `.pages.yml` oder die Collaborator-Verwaltung administrieren.

Die Konfiguration verwendet bewusst `commit.identity: app`, damit persönliche E-Mail-Adressen der Redakteure nicht als Committer-Metadaten im öffentlichen Repository veröffentlicht werden.

## Empfohlener Phase-3-Abnahmetest

### A. Vorhandene News lesen

Beide vorhandenen Artikel im CMS öffnen und prüfen:

* Titel korrekt
* Datum/Uhrzeit korrekt
* Titelbild sichtbar
* Bildbeschreibung vorhanden
* Artikeltext im Rich-Text-Editor sichtbar

### B. Testartikel erstellen

Einen eindeutig als Test gekennzeichneten Artikel anlegen, z. B. `CMS-Test Phase 3`.

Mindestens verwenden:

* Titel
* aktueller Veröffentlichungszeitpunkt
* Titelbild
* Bildbeschreibung
* mehrere Absätze
* H2-Zwischenüberschrift
* Fettschrift
* Liste
* Link
* Bild im Text mit Alt-Text
* kleine Tabelle

Kurzbeschreibung einmal bewusst leer lassen, um die automatische Teaser-Erzeugung zu testen.

### C. Publish prüfen

Nach dem Speichern/Veröffentlichen:

1. GitHub-Commit durch Pages CMS vorhanden.
2. Workflow **News generieren** startet.
3. Workflow erfolgreich.
4. Testartikel erscheint auf `pages/neuigkeiten.html`.
5. Testartikel erscheint im Slider, sofern er zu den fünf neuesten Artikeln gehört.
6. Artikelseite funktioniert auf Desktop und Mobil.
7. Tabelle ist mobil nutzbar.
8. Inline-Bild und Alt-Text sind korrekt.

### D. Bearbeiten prüfen

Im CMS den Titel oder einen Absatz ändern und erneut speichern.

Erwartung:

* Workflow läuft erneut.
* Artikelinhalt wird aktualisiert.
* URL bleibt unverändert.

### E. Löschen prüfen

Den Testartikel über Pages CMS löschen.

Erwartung:

* Workflow läuft erneut.
* generierte Artikelseite verschwindet.
* News-Übersicht, Slider und Sitemap werden synchronisiert.

## Optionaler Scheduling-Test

Nach dem normalen E2E-Test kann ein zweiter Testartikel mit einem Zeitpunkt etwa 30–60 Minuten in der Zukunft erstellt werden.

Vor dem Zeitpunkt darf er nicht auf der Website erscheinen.
Nach Erreichen des Zeitpunkts sollte einer der geplanten Läufe von **News generieren** ihn veröffentlichen.

## Notfall / Repair

Falls ein CMS-Commit korrekt im Repository liegt, die Website aber nicht synchron ist:

GitHub → Actions → **News generieren** → **Run workflow**

Dieser manuelle Lauf bleibt der vollständige Rebuild-/Repair-Weg.

## Pages CMS ist austauschbar

Ein Ausfall von Pages CMS betrifft nur die Redaktionsoberfläche.

Unverändert bleiben:

* `content/news/*.md`
* `assets/images/news/*`
* `assets/python/generate_news.py`
* Templates
* GitHub Actions
* generierte Website

Ein anderes CMS oder eine eigene Übergangslösung muss lediglich dasselbe dokumentierte Markdown-Format erzeugen.
