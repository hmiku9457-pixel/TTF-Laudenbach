---
title: "Redaktionshandbuch – TTF Laudenbach"
---

# Redaktionshandbuch – TTF Laudenbach

Dieses Handbuch richtet sich an alle Personen, die Neuigkeiten auf der Webseite der **Tischtennis-Freunde Laudenbach** pflegen. Für die normale redaktionelle Arbeit sind keine Kenntnisse in HTML, CSS, JavaScript, Python oder Git erforderlich.

Die Redaktion arbeitet ausschließlich über **Pages CMS**. Technische Dateien der Webseite werden dabei nicht manuell bearbeitet.

## 1. Was kann über das CMS gepflegt werden?

Über das CMS werden die **Neuigkeiten** der Vereinswebseite gepflegt. Dazu gehören:

- neue News erstellen,
- bestehende News bearbeiten,
- News für einen späteren Zeitpunkt planen,
- News löschen,
- Titelbilder und Bilder im Artikel verwenden,
- Texte formatieren,
- Tabellen einfügen,
- Inhalte in zwei Spalten darstellen,
- Veranstaltungen hervorheben,
- Trenner und zusätzliche Abstände verwenden.

Nicht zur normalen Redaktion gehören unter anderem Navigation, Footer, Seitendesign, Spielpläne, Tabellenstände, Spielerlisten, Scraper, Galerie-Automatisierung und technische Workflows. Diese Bereiche werden separat technisch betreut.

## 2. Pages CMS öffnen

1. Pages CMS öffnen.
2. Mit dem eingerichteten Zugang anmelden.
3. Das Repository der TTF Laudenbach auswählen.
4. Im Menü **Neuigkeiten** öffnen.

Zusätzlich steht im CMS der Bereich **Dokumentation** zur Verfügung. Dort kann dieses Redaktionshandbuch jederzeit eingesehen werden.

## 3. Übersicht der News

Im Bereich **Neuigkeiten** werden die vorhandenen Beiträge angezeigt. Die Liste ist standardmäßig nach dem Veröffentlichungszeitpunkt sortiert, neue Beiträge stehen oben.

Angezeigt werden insbesondere:

- Titel,
- Veröffentlichungszeitpunkt,
- Kurzbeschreibung.

Über die Suche können Beiträge nach Titel und Kurzbeschreibung gefunden werden.

## 4. Neue News erstellen

Zum Erstellen einer News im Bereich **Neuigkeiten** einen neuen Eintrag anlegen.

Eine News besteht aus folgenden Feldern:

1. **Titel**
2. **Veröffentlichung**
3. **Kurzbeschreibung** – optional
4. **Titelbild**
5. **Bildbeschreibung**
6. **Artikelinhalt**

### 4.1 Titel

Der Titel ist ein Pflichtfeld und sollte kurz und eindeutig beschreiben, worum es in der News geht.

Gute Beispiele:

- `Vereinsmeisterschaften 2026`
- `Saisonauftakt der Herren I`
- `Einladung zur Mitgliederversammlung`
- `Erfolgreiches Wochenende für unsere Jugend`

Beim erstmaligen Erstellen wird aus dem Titel automatisch der dauerhafte Dateiname des Beitrags erzeugt. Der Dateiname wird später nicht automatisch geändert, wenn nur der sichtbare Titel angepasst wird. Das verhindert, dass sich die Adresse einer bereits veröffentlichten News unnötig ändert.

### 4.2 Veröffentlichung

Das Feld **Veröffentlichung** enthält Datum und Uhrzeit.

Für eine sofortige Veröffentlichung kann der aktuelle Zeitpunkt verwendet werden. Für eine geplante Veröffentlichung wird ein zukünftiger Zeitpunkt eingetragen.

Zukünftig geplante Beiträge dürfen bereits gespeichert werden. Sie werden erst berücksichtigt, sobald ihr Veröffentlichungszeitpunkt erreicht ist und der automatische News-Workflow den nächsten Prüf-Lauf durchgeführt hat.

**Hinweis:** Die Prüfung geplanter Beiträge läuft zweimal pro Stunde. Eine geplante News kann deshalb einige Minuten nach der eingestellten Uhrzeit sichtbar werden.

### 4.3 Kurzbeschreibung

Die Kurzbeschreibung ist optional. Sie wird als Teaser unter anderem in der News-Übersicht und im News-Slider verwendet.

Empfehlung: Eine kurze, verständliche Zusammenfassung mit ein bis zwei Sätzen eintragen.

Wird das Feld leer gelassen, erzeugt das System automatisch eine Kurzbeschreibung aus dem Artikelinhalt.

### 4.4 Titelbild

Jede News benötigt ein Titelbild.

Das Titelbild wird unter anderem verwendet für:

- die News-Seite,
- die News-Übersicht,
- den News-Slider.

Unterstützt werden die Bildformate:

- JPG/JPEG,
- PNG,
- WebP.

Für News hochgeladene Bilder werden im dafür vorgesehenen News-Bildbereich gespeichert. Sie werden nicht automatisch Bestandteil der normalen Vereinsgalerie.

### 4.5 Bildbeschreibung

Die **Bildbeschreibung** ist ein Pflichtfeld. Sie dient insbesondere der Barrierefreiheit und beschreibt sachlich, was auf dem Titelbild zu sehen ist.

Beispiele:

- `Jugendmannschaft der TTF Laudenbach bei der Siegerehrung`
- `Spieler der Herren I während eines Heimspiels`
- `Gruppenfoto der Teilnehmer der Vereinsmeisterschaften`

Nicht sinnvoll sind Beschreibungen wie:

- `Bild`
- `Foto 1`
- `Newsbild`

## 5. Artikelinhalt und Inhaltsblöcke

Der eigentliche Artikel wird aus frei sortierbaren Inhaltsblöcken aufgebaut.

Zur Verfügung stehen fünf Blocktypen:

1. **Text**
2. **Zwei Spalten**
3. **Eventankündigung**
4. **Trenner**
5. **Abstand**

Ein Artikel benötigt mindestens einen inhaltlichen Block vom Typ **Text**, **Zwei Spalten** oder **Eventankündigung**.

Die Blöcke können in der gewünschten Reihenfolge angeordnet und bei Bedarf mehrfach verwendet werden.

## 6. Block „Text“

Der Textblock ist der Standardbaustein für normale Artikelinhalte.

Er besitzt zwei mögliche Textausrichtungen:

- **Linksbündig** – Standard für normalen Artikeltext.
- **Zentriert** – für kurze hervorgehobene Textbereiche, Ankündigungen oder einen Abschluss.

Für längere Fließtexte sollte normalerweise **Linksbündig** verwendet werden.

### Formatierung im Texteditor

Der Rich-Text-Editor unterstützt die üblichen redaktionellen Formatierungen, unter anderem:

- Absätze,
- Überschriften,
- Fettschrift,
- Kursivschrift,
- Aufzählungen,
- nummerierte Listen,
- Links,
- Bilder,
- Tabellen.

Für Überschriften innerhalb des Artikels dürfen nur die Ebenen **H1, H2 und H3** verwendet werden.

Direkt eingegebenes HTML ist im News-Inhalt nicht vorgesehen und wird vom Generator abgelehnt. Für die Redaktion ist es daher nicht notwendig, in einen Quellcode-Modus zu wechseln.

### Absätze sinnvoll einsetzen

Längere Texte sollten in kurze, thematisch passende Absätze gegliedert werden. Das verbessert insbesondere auf Smartphones die Lesbarkeit.

### Fett und kursiv

**Fettschrift** eignet sich für einzelne wichtige Angaben, beispielsweise:

- **Beginn: 18:00 Uhr**
- **Anmeldeschluss: 5. September**

*Kursive Schrift* sollte ebenfalls sparsam eingesetzt werden.

Große Teile eines Artikels sollten nicht vollständig fett oder kursiv formatiert werden.

### Listen

Listen eignen sich besonders für mehrere kurze Angaben, zum Beispiel:

- Hallenöffnung: 17:00 Uhr
- Meldeschluss: 17:30 Uhr
- Beginn: 18:00 Uhr
- Austragungsort: Bergstraßenhalle

### Links

Der Linktext sollte nach Möglichkeit beschreiben, wohin der Link führt.

Besser:

`Zur Turnieranmeldung`

statt:

`Hier klicken`

Nach der Veröffentlichung sollte ein neu eingefügter externer Link kurz getestet werden.

## 7. Bilder im Artikel

Neben dem verpflichtenden Titelbild können auch innerhalb der Rich-Text-Bereiche Bilder eingefügt werden.

Vor der Veröffentlichung sollte geprüft werden:

- Ist das Bild scharf und richtig ausgerichtet?
- Ist der relevante Inhalt gut erkennbar?
- Darf das Bild veröffentlicht werden?
- Sind keine vertraulichen oder ungeeigneten Informationen sichtbar?

Bilder werden auf der Webseite automatisch passend dargestellt. Es müssen keine Bildbreiten oder CSS-Klassen eingestellt werden.

## 8. Tabellen im Artikel

Tabellen können direkt im Rich-Text-Editor erstellt werden.

Sie eignen sich beispielsweise für kleine Ergebnisübersichten oder strukturierte Informationen.

| Platz | Spieler | Ergebnis |
| --- | --- | --- |
| 1 | Max Mustermann | 5:0 |
| 2 | Erika Beispiel | 4:1 |

Tabellen sollten möglichst kompakt bleiben. Sehr breite Tabellen mit vielen Spalten sind auf Smartphones schwer lesbar.

Offizielle Mannschaftstabellen, Spielpläne oder automatisch importierte Ergebnisse sollten nicht manuell über eine News-Tabelle nachgebaut werden.

## 9. Block „Zwei Spalten“

Der Block **Zwei Spalten** enthält zwei voneinander unabhängige Rich-Text-Bereiche.

Er eignet sich beispielsweise für:

- zwei zusammengehörige Informationen,
- Text und Bild nebeneinander,
- zwei kurze Listen,
- eine kleine Tabelle neben ergänzendem Text.

Auf Desktop-Bildschirmen werden die beiden Bereiche gleichmäßig nebeneinander dargestellt. Auf kleinen Displays werden sie automatisch untereinander angeordnet.

Bilder und Tabellen bleiben innerhalb ihrer jeweiligen Spalte.

Für sehr lange Fließtexte ist der normale Textblock meist übersichtlicher.

## 10. Block „Eventankündigung“

Der Block **Eventankündigung** hebt einen konkreten Termin innerhalb einer News hervor.

Er ist vollständig optional und sollte nur verwendet werden, wenn tatsächlich eine Veranstaltung oder ein Termin hervorgehoben werden soll.

### Pflichtfelder

- **Event**
- **Datum**

### Optionale Felder

- Uhrzeit,
- Ort,
- Beschreibung.

Die Uhrzeit wird im Format `HH:MM` eingegeben, beispielsweise `18:30`.

Geeignete Einsatzzwecke sind zum Beispiel:

- Vereinsmeisterschaften,
- Mitgliederversammlung,
- Sommerfest,
- Turnier,
- Trainingsveranstaltung.

Eine normale News benötigt keine Eventankündigung.

## 11. Block „Trenner“

Der Block **Trenner** erzeugt eine einheitliche horizontale Trennlinie zwischen Inhaltsbereichen.

Er sollte nur verwendet werden, wenn zwei Bereiche optisch deutlich voneinander getrennt werden sollen.

Eine eigene Designauswahl ist bewusst nicht vorgesehen.

## 12. Block „Abstand“

Der Block **Abstand** fügt zusätzlichen vertikalen Freiraum ein.

Zur Verfügung stehen:

- **Klein**,
- **Mittel**,
- **Groß**.

Abstände sollten sparsam eingesetzt werden. Das normale Seitenlayout erzeugt bereits automatisch passende Abstände zwischen vielen Elementen.

## 13. Sinnvoller Aufbau einer News

Eine einfache News benötigt häufig nur wenige Bausteine.

Beispiel:

1. Textblock mit Einleitung,
2. Textblock mit Bericht und Bild,
3. Eventankündigung für einen kommenden Termin,
4. abschließender Textblock.

Ein weiterer möglicher Aufbau:

1. kurzer zentrierter Text,
2. Trenner,
3. Zwei-Spalten-Bereich,
4. mittlerer Abstand,
5. normaler Textblock.

Nicht jeder verfügbare Baustein muss in jeder News verwendet werden.

## 14. News speichern und veröffentlichen

Nach Abschluss der Bearbeitung wird die News im CMS gespeichert.

Pages CMS speichert die redaktionelle Quelldatei im Repository. Anschließend übernimmt die vorhandene Automatisierung den technischen Rest:

1. News-Inhalte werden geprüft,
2. die einzelne Artikelseite wird erzeugt,
3. die News-Übersicht wird aktualisiert,
4. die Slider-Daten werden aktualisiert,
5. die Sitemap wird aktualisiert,
6. die Webseite wird veröffentlicht.

Für diese Schritte muss die Redaktion keine GitHub Actions starten und keine Dateien manuell bearbeiten.

## 15. News-Slider auf der Startseite

Der News-Slider wird automatisch aus den veröffentlichten News erzeugt.

Es werden die **fünf aktuellsten veröffentlichten News** verwendet.

Eine News muss daher nicht zusätzlich für den Slider aktiviert oder später wieder entfernt werden.

## 16. Bestehende News bearbeiten

Eine vorhandene News kann jederzeit im CMS geöffnet und bearbeitet werden.

Typische Korrekturen sind:

- Tippfehler korrigieren,
- Uhrzeit korrigieren,
- Link ergänzen,
- Bild austauschen,
- Formulierung verbessern,
- zusätzliche Informationen ergänzen.

Für kleine Änderungen wird keine neue News erstellt. Stattdessen wird der bestehende Beitrag korrigiert und erneut gespeichert.

Bei einer normalen Korrektur sollte der ursprüngliche Veröffentlichungszeitpunkt beibehalten werden. Wird er verändert, kann sich auch die Reihenfolge der News ändern.

## 17. News löschen

Nicht mehr benötigte News können über das CMS gelöscht werden.

Beim nächsten Generatorlauf werden die daraus erzeugten öffentlichen Dateien automatisch bereinigt beziehungsweise aktualisiert.

Alte Beiträge müssen allerdings nicht allein deshalb gelöscht werden, weil das darin beschriebene Ereignis bereits vergangen ist. Spielberichte, Vereinsmeisterschaften oder andere Vereinsereignisse können als Archiv weiterhin sinnvoll sein.

Vor dem Löschen sollte daher geprüft werden, ob der Beitrag wirklich dauerhaft entfernt werden soll.

## 18. Was darf nicht manuell bearbeitet werden?

Die News-Quelldateien liegen unter `content/news/`. Aus ihnen werden automatisch weitere Dateien erzeugt.

Insbesondere folgende News-Ausgaben werden automatisch gepflegt:

- `pages/neuigkeiten.html`
- `pages/news/*.html`
- `assets/data/news.json`
- die News-Einträge in `sitemap.xml`

Diese generierten Dateien dürfen nicht als Ersatz für das CMS manuell korrigiert werden. Solche Änderungen würden bei einer späteren Generierung wieder überschrieben.

Für redaktionelle Änderungen gilt daher:

> **News immer über Pages CMS bearbeiten.**

## 19. Galerie, Spielpläne und Mannschaftsdaten

Die normale Bildergalerie ist vom News-System getrennt. Bilder, die für eine News hochgeladen werden, werden nicht automatisch in die Galerie übernommen.

Auch Spielpläne, Tabellenstände und Spielerlisten gehören nicht zum News-CMS. Ein Teil dieser Daten wird automatisch verarbeitet.

Falls dort falsche oder fehlende Daten auffallen, sollte die technisch verantwortliche Person informiert werden, anstatt die generierten Dateien manuell zu ändern.

## 20. Datenschutz und Bildrechte

Die Vereinswebseite ist öffentlich erreichbar. Vor einer Veröffentlichung sollte deshalb geprüft werden, ob die verwendeten Inhalte für eine öffentliche Webseite geeignet sind.

Besondere Vorsicht gilt bei:

- privaten Telefonnummern,
- privaten E-Mail-Adressen,
- Anschriften,
- sonstigen personenbezogenen Informationen,
- Bildern von Personen,
- insbesondere Bildern von Kindern und Jugendlichen.

Bilder sollten nur verwendet werden, wenn sie für die Veröffentlichung vorgesehen beziehungsweise freigegeben sind.

Vertrauliche Informationen, Zugangsdaten oder interne Vereinsinformationen gehören nicht in eine öffentliche News.

## 21. Empfohlener Schreibstil

News sollten möglichst:

- sachlich,
- freundlich,
- verständlich,
- übersichtlich,
- auch für Außenstehende nachvollziehbar

geschrieben werden.

Interne Abkürzungen sollten vermieden oder beim ersten Auftreten erklärt werden.

Kurze Absätze und aussagekräftige Zwischenüberschriften verbessern die Lesbarkeit.

## 22. Kontrolle vor der Veröffentlichung

Vor dem Speichern beziehungsweise nach einer größeren Bearbeitung sollten folgende Punkte kurz geprüft werden:

- Ist der Titel korrekt?
- Sind Datum und Uhrzeit der Veröffentlichung korrekt?
- Ist die Kurzbeschreibung sinnvoll oder soll sie automatisch erzeugt werden?
- Ist das Titelbild korrekt?
- Ist die Bildbeschreibung aussagekräftig?
- Sind Rechtschreibung und Namen geprüft?
- Sind Absätze und Überschriften sinnvoll gesetzt?
- Funktionieren eingefügte Links?
- Sind Eventdatum, Uhrzeit und Ort korrekt?
- Enthält der Beitrag keine vertraulichen Informationen?
- Dürfen verwendete Bilder veröffentlicht werden?

Nach der Veröffentlichung sollte die öffentliche News-Seite kurz auf Desktop oder Smartphone kontrolliert werden.

## 23. Wenn eine Änderung nicht sichtbar wird

Nach dem Speichern wird die Webseite automatisch verarbeitet und veröffentlicht. Die Änderung muss deshalb nicht zwingend in derselben Sekunde auf der öffentlichen Webseite erscheinen.

Bei einer geplanten Veröffentlichung ist zusätzlich zu beachten, dass der automatische Zeitplan zweimal pro Stunde prüft, ob neue Beiträge freigegeben werden müssen.

Wenn eine Änderung auch nach dem automatischen Lauf nicht sichtbar ist:

1. prüfen, ob der Beitrag im CMS gespeichert wurde,
2. prüfen, ob der eingestellte Veröffentlichungszeitpunkt bereits erreicht ist,
3. prüfen, ob alle Pflichtfelder ausgefüllt sind,
4. die öffentliche Seite neu laden,
5. bei weiterhin bestehendem Problem die technische Betreuung informieren.

Hilfreich für die Fehlersuche sind:

- Titel der betroffenen News,
- ungefährer Zeitpunkt der Änderung,
- kurze Beschreibung des Problems,
- gegebenenfalls ein Screenshot einer Fehlermeldung.

Bei technischen Fehlern sollten keine generierten Dateien im Repository als Workaround verändert werden.

## 24. Kurzablauf: neue News

1. Pages CMS öffnen und anmelden.
2. **Neuigkeiten** öffnen.
3. Neue News anlegen.
4. Titel eintragen.
5. Veröffentlichung prüfen oder planen.
6. Optional eine Kurzbeschreibung eintragen.
7. Titelbild auswählen oder hochladen.
8. Bildbeschreibung eintragen.
9. Artikel aus den gewünschten Inhaltsblöcken aufbauen.
10. Inhalt kontrollieren.
11. Speichern.
12. Nach der automatischen Veröffentlichung die öffentliche News kurz prüfen.

## 25. Kurzablauf: bestehende News korrigieren

1. **Neuigkeiten** öffnen.
2. Betroffenen Beitrag auswählen.
3. Gewünschte Korrektur durchführen.
4. Veröffentlichungszeitpunkt nur ändern, wenn dies bewusst gewünscht ist.
5. Speichern.
6. Öffentliche News nach der Aktualisierung kontrollieren.

## 26. Kurzablauf: News löschen

1. Prüfen, ob die News wirklich dauerhaft entfernt werden soll.
2. Beitrag im CMS öffnen beziehungsweise auswählen.
3. Löschen ausführen.
4. Löschung bestätigen.
5. Nach der automatischen Aktualisierung News-Übersicht und gegebenenfalls Startseite kontrollieren.

## 27. Zuständigkeiten

### Redaktion

Die Redaktion ist insbesondere verantwortlich für:

- Inhalt und Formulierung der News,
- Rechtschreibung,
- Bilder und Bildbeschreibungen,
- Veranstaltungsinformationen,
- externe Links,
- inhaltliche Aktualität.

### Technische Betreuung

Zur technischen Betreuung gehören insbesondere:

- Quellcode,
- Navigation und Footer,
- Seitendesign,
- Pages-CMS-Konfiguration,
- GitHub Pages,
- automatische Workflows,
- News-Generator,
- Scraper und automatische Sportdaten,
- Galerie-Automatisierung,
- technische Fehler,
- Domain und HTTPS.

## 28. Wichtigste Regeln

1. News immer über **Pages CMS** bearbeiten.
2. Titelbild und Bildbeschreibung nicht vergessen.
3. Die Kurzbeschreibung kann bei Bedarf automatisch erzeugt werden.
4. Für normalen Fließtext den linksbündigen Textblock verwenden.
5. Eventankündigungen nur für konkrete Termine verwenden.
6. Bilder nur veröffentlichen, wenn sie dafür geeignet und freigegeben sind.
7. Generierte Dateien nicht manuell korrigieren.
8. Alte News nicht unnötig löschen – sie können als Vereinsarchiv dienen.
9. Nach größeren Änderungen die öffentliche Darstellung kurz kontrollieren.
10. Bei technischen Problemen die technische Betreuung informieren.

---

**Dokumentstand:** August 2026  
**Webseite:** TTF Laudenbach  
**Dokument:** Redaktionshandbuch
