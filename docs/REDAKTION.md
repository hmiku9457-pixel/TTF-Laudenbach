# Redaktionsdokumentation – TTF Laudenbach

Diese Dokumentation richtet sich an alle Personen, die Inhalte auf der Webseite der **TTF Laudenbach** pflegen.

Für die normale redaktionelle Arbeit sind **keine Programmierkenntnisse** erforderlich. Insbesondere müssen keine HTML-, CSS-, JavaScript-, Python- oder GitHub-Dateien manuell bearbeitet werden.

---

# 1. Grundprinzip der Webseite

Die Webseite ist technisch von ihren redaktionellen Inhalten getrennt.

Redakteure kümmern sich ausschließlich um Inhalte, die für die Veröffentlichung vorgesehen sind. Die technische Struktur der Webseite wird separat verwaltet.

## Redaktionelle Aufgaben

Zu den typischen redaktionellen Aufgaben gehören insbesondere:

* News erstellen
* bestehende News bearbeiten
* News löschen
* Texte innerhalb von News formatieren
* Bilder in News einfügen
* Tabellen innerhalb von News verwenden
* Veranstaltungen innerhalb einer News hervorheben

## Keine redaktionellen Aufgaben

Folgende Bereiche gehören **nicht** zur normalen redaktionellen Pflege:

* Navigation
* Seitenlayout
* Farben und Design
* CSS
* JavaScript
* Tabellen des Spielbetriebs
* Mannschaftsdaten
* Spielerlisten
* Spielergebnisse
* Tabellenstände
* automatische Datenimporte
* Header und Footer
* SEO-Grundstruktur
* Sitemap
* technische Konfigurationsdateien
* generierte JSON-Dateien

Diese Bereiche werden entweder automatisch erzeugt oder gehören zur technischen Wartung der Webseite.

**Wichtig:** Dateien im GitHub-Repository sollten von Redakteuren nicht manuell verändert werden, sofern dies nicht ausdrücklich in dieser Dokumentation beschrieben ist.

---

# 2. Pages CMS

Für die Pflege der News wird **Pages CMS** verwendet.

Pages CMS stellt eine grafische Oberfläche bereit, über die Inhalte bearbeitet werden können, ohne direkt mit dem Quellcode der Webseite arbeiten zu müssen.

## Zugang

CMS-Adresse:

**[CMS-Adresse bei Übergabe eintragen]**

Der Zugang zur Webseite wird bei der Übergabe eingerichtet.

Nach erfolgreicher Anmeldung wird das Repository der TTF Laudenbach ausgewählt.

Anschließend stehen die für die Redaktion freigegebenen Inhaltsbereiche zur Verfügung.

---

# 3. News-System

Der wichtigste redaktionell gepflegte Bereich der Webseite sind die **Neuigkeiten**.

Eine News besteht grundsätzlich aus:

* den allgemeinen Angaben des Beitrags
* dem eigentlichen Inhalt
* optionalen Bildern
* optionalen Tabellen
* optionalen besonderen Inhaltsblöcken

Das System erstellt aus den Eingaben automatisch die erforderlichen Webseiten.

Redakteure müssen deshalb **keine eigene HTML-Seite für eine News erstellen**.

---

# 4. Neue News erstellen

## 4.1 News-Bereich öffnen

Nach der Anmeldung in Pages CMS:

1. den Bereich **News** öffnen,
2. eine neue News anlegen,
3. die benötigten Angaben eintragen,
4. den Inhalt zusammenstellen,
5. Beitrag speichern beziehungsweise veröffentlichen.

Die technische Verarbeitung erfolgt anschließend automatisch.

---

# 5. Titel einer News

Jede News benötigt einen eindeutigen und verständlichen Titel.

Gute Beispiele:

* `Saisonauftakt der Herren I`
* `Vereinsmeisterschaften 2026`
* `Einladung zur Mitgliederversammlung`
* `Erfolgreiches Wochenende für unsere Jugend`

Weniger geeignet sind sehr allgemeine Titel wie:

* `Neuigkeiten`
* `Information`
* `Wichtig`
* `Update`

Der Titel sollte bereits erkennen lassen, worum es im Beitrag geht.

---

# 6. Datum

Für jede News wird ein Datum angegeben.

Das Datum dient unter anderem dazu, Beiträge zeitlich einzuordnen und entsprechend auf der Webseite darzustellen.

Beim Erstellen einer neuen News sollte normalerweise das Datum verwendet werden, an dem die Nachricht veröffentlicht werden soll.

Bei einer nachträglichen Korrektur eines bestehenden Beitrags sollte das ursprüngliche Veröffentlichungsdatum normalerweise **nicht verändert werden**.

---

# 7. Inhalt einer News

Der Inhalt einer News wird aus verschiedenen **Inhaltsblöcken** aufgebaut.

Die Reihenfolge der Blöcke kann frei gewählt werden.

Dadurch können sowohl sehr einfache als auch umfangreichere Beiträge erstellt werden.

Zur Verfügung stehen insbesondere:

* **Text**
* **Zwei Spalten**
* **Eventankündigung**
* **Trenner**
* **Abstand**

Je nach Inhalt können mehrere Blöcke desselben Typs verwendet werden.

Beispiel:

1. Text
2. Bild innerhalb des Textes
3. Zwei Spalten
4. Abstand
5. Eventankündigung
6. Trenner
7. Text

---

# 8. Inhaltsblock „Text“

Der Block **Text** ist der Standardblock für normale News.

Er eignet sich beispielsweise für:

* Berichte
* Ankündigungen
* Ergebnisse
* Rückblicke
* Informationen an Mitglieder
* allgemeine Vereinsnachrichten

Innerhalb des Texteditors können Inhalte formatiert werden.

Je nach Editor stehen beispielsweise zur Verfügung:

* Absätze
* Überschriften
* fett hervorgehobener Text
* kursiver Text
* Listen
* Links
* Bilder
* Tabellen

Für normale Beiträge sollte dieser Block bevorzugt werden.

---

# 9. Überschriften innerhalb einer News

Zusätzliche Überschriften sollten verwendet werden, wenn ein längerer Beitrag mehrere Themen oder Abschnitte enthält.

Beispiel:

# Vereinsmeisterschaften 2026

Einleitungstext …

## Herren

Text …

## Jugend

Text …

## Siegerehrung

Text …

Bei kurzen Beiträgen sind zusätzliche Überschriften normalerweise nicht notwendig.

Zu viele Überschriften machen einen kurzen Beitrag unnötig unruhig.

---

# 10. Absätze

Längere Texte sollten in sinnvolle Absätze unterteilt werden.

Als Richtwert gilt:

Ein Absatz sollte normalerweise nur einen Gedanken oder Themenabschnitt enthalten.

Statt eines sehr langen Textblocks:

> Am vergangenen Wochenende fanden unsere Vereinsmeisterschaften statt. Insgesamt nahmen zahlreiche Spieler teil. Am Vormittag wurde die Jugendkonkurrenz ausgespielt. Danach folgten die Wettbewerbe der Erwachsenen. Am Abend fand die Siegerehrung statt. Anschließend saßen die Teilnehmer noch gemeinsam zusammen.

besser:

> Am vergangenen Wochenende fanden unsere Vereinsmeisterschaften statt. Insgesamt nahmen zahlreiche Spieler teil.
>
> Am Vormittag wurde die Jugendkonkurrenz ausgespielt. Danach folgten die Wettbewerbe der Erwachsenen.
>
> Am Abend fand die Siegerehrung statt. Anschließend saßen die Teilnehmer noch gemeinsam zusammen.

---

# 11. Fett und kursiv

**Fettschrift** sollte sparsam zur Hervorhebung wichtiger Informationen eingesetzt werden.

Geeignete Beispiele:

* **Samstag, 12. September**
* **Beginn: 18:00 Uhr**
* **Anmeldeschluss: 5. September**

*Kursive Schrift* kann für leichte Hervorhebungen oder besondere Hinweise verwendet werden.

Große Teile eines Beitrags sollten weder vollständig fett noch kursiv geschrieben werden.

---

# 12. Listen

Listen eignen sich besonders für mehrere kurze Informationen.

Beispiel:

* Beginn: 18:00 Uhr
* Hallenöffnung: 17:00 Uhr
* Meldeschluss: 17:30 Uhr
* Austragungsort: Bergstraßenhalle

Für solche Informationen ist eine Liste meist übersichtlicher als ein langer Fließtext.

---

# 13. Links

Links können beispielsweise verwendet werden für:

* externe Verbandsseiten
* Turnieranmeldungen
* weiterführende Informationen
* externe Ergebnisse
* andere relevante Webseiten

Der sichtbare Linktext sollte möglichst beschreiben, wohin der Link führt.

Besser:

`Zur Turnieranmeldung`

statt:

`Hier klicken`

Links sollten nach dem Veröffentlichen kurz getestet werden.

---

# 14. Bilder in News

Bilder können innerhalb der dafür vorgesehenen Inhaltsfelder hochgeladen beziehungsweise ausgewählt werden.

Geeignet sind beispielsweise:

* Mannschaftsfotos
* Bilder von Veranstaltungen
* Siegerehrungen
* Turnierbilder
* Vereinsaktionen

## Empfehlungen für Bilder

Vor dem Hochladen sollte geprüft werden:

* Ist das Bild scharf?
* Ist die Ausrichtung korrekt?
* Ist der relevante Bildinhalt gut erkennbar?
* Darf das Bild veröffentlicht werden?
* Enthält das Bild keine unnötigen oder sensiblen Informationen?

Extrem große Originaldateien sollten nach Möglichkeit vermieden werden.

## Aussagekräftige Bilder verwenden

Ein Bild sollte einen tatsächlichen Mehrwert für den Beitrag haben.

Nicht jede News benötigt zwingend ein Bild.

Ein guter kurzer Vereinsbeitrag ohne Bild ist besser als ein unpassendes oder qualitativ schlechtes Bild.

---

# 15. Tabellen innerhalb von News

Der Rich-Text-Editor kann auch für Tabellen verwendet werden.

Tabellen eignen sich für strukturierte Informationen wie:

| Platz | Spieler        | Ergebnis |
| ----- | -------------- | -------- |
| 1     | Max Mustermann | 5:0      |
| 2     | Erika Beispiel | 4:1      |
| 3     | Peter Muster   | 3:2      |

Tabellen sollten möglichst klein und übersichtlich bleiben.

Sehr breite Tabellen sind insbesondere auf Smartphones schwer darzustellen.

Für offizielle Mannschaftstabellen, Spielpläne oder automatisch importierte Ergebnisse sollte **keine manuelle News-Tabelle als Ersatz** erstellt werden.

---

# 16. Inhaltsblock „Zwei Spalten“

Mit dem Block **Zwei Spalten** können zwei Inhalte nebeneinander dargestellt werden.

Der Block eignet sich beispielsweise für:

* zwei zusammengehörige Informationen
* zwei kurze Listen
* Text und ergänzende Information
* zwei unterschiedliche Themenbereiche

Der Zwei-Spalten-Block sollte nur verwendet werden, wenn die Inhalte tatsächlich zusammengehören.

Sehr lange Texte sollten besser untereinander dargestellt werden.

Auf kleineren Bildschirmen kann die Darstellung automatisch angepasst werden.

---

# 17. Inhaltsblock „Eventankündigung“

Für Veranstaltungen steht ein eigener Block **Eventankündigung** zur Verfügung.

Dieser Block hebt wichtige Veranstaltungsinformationen optisch hervor.

Geeignete Beispiele:

* Vereinsmeisterschaften
* Mitgliederversammlung
* Sommerfest
* Turniere
* Trainingsveranstaltungen
* sonstige Vereinstermine

Für eine Eventankündigung müssen mindestens folgende Angaben vorhanden sein:

* **Eventname**
* **Datum**

Weitere Informationen können abhängig vom jeweiligen Beitrag im umgebenden Text ergänzt werden.

Der Eventblock sollte nur verwendet werden, wenn tatsächlich eine konkrete Veranstaltung angekündigt wird.

Für normale Vereinsnachrichten ist der normale Textblock besser geeignet.

---

# 18. Inhaltsblock „Trenner“

Ein **Trenner** erzeugt eine sichtbare Abgrenzung zwischen zwei Bereichen einer News.

Er eignet sich beispielsweise, wenn innerhalb eines Beitrags zwei deutlich unterschiedliche Themen behandelt werden.

Trenner sollten sparsam eingesetzt werden.

Mehrere Trenner direkt hintereinander sind nicht sinnvoll.

---

# 19. Inhaltsblock „Abstand“

Der Block **Abstand** erzeugt zusätzlichen vertikalen Freiraum zwischen zwei Bereichen.

Er kann eingesetzt werden, wenn zwei Elemente optisch etwas stärker voneinander getrennt werden sollen.

Auch dieser Block sollte sparsam verwendet werden.

Das normale Layout der Webseite erzeugt bereits automatisch passende Abstände.

---

# 20. Reihenfolge der Inhaltsblöcke

Die Inhaltsblöcke können entsprechend dem gewünschten Aufbau sortiert werden.

Eine typische News könnte beispielsweise so aufgebaut sein:

**Text**

Kurze Einleitung und Erklärung des Ereignisses.

**Text mit Bild**

Bericht über die Veranstaltung.

**Zwei Spalten**

Ergebnisse oder weitere Informationen.

**Eventankündigung**

Hinweis auf die nächste Veranstaltung.

**Text**

Abschließende Informationen.

Der Aufbau muss nicht bei jeder News gleich sein.

---

# 21. News vor der Veröffentlichung prüfen

Vor dem Speichern einer neuen News sollten mindestens folgende Punkte kontrolliert werden:

* [ ] Titel korrekt?
* [ ] Datum korrekt?
* [ ] Rechtschreibung grob geprüft?
* [ ] Absätze sinnvoll gesetzt?
* [ ] Bilder korrekt?
* [ ] Links korrekt?
* [ ] Eventdaten korrekt?
* [ ] Keine versehentlich eingefügten Platzhalter?
* [ ] Keine internen oder vertraulichen Informationen enthalten?
* [ ] Beitrag auch für Außenstehende verständlich?

---

# 22. News veröffentlichen

Nach Abschluss der Bearbeitung wird die News in Pages CMS gespeichert.

Die weitere technische Verarbeitung erfolgt automatisch.

Im Hintergrund werden aus den redaktionellen Inhalten unter anderem die für die Webseite benötigten News-Daten und Webseiten erzeugt.

Dazu gehören insbesondere:

* die News-Übersicht
* die einzelne News-Seite
* die Daten für die News-Darstellung
* notwendige Aktualisierungen der Sitemap

Anschließend wird die aktualisierte Webseite veröffentlicht.

Redakteure müssen diese Dateien **nicht selbst erzeugen oder bearbeiten**.

---

# 23. Änderungen sind nicht immer sofort sichtbar

Nach dem Speichern muss die Webseite technisch neu erzeugt und veröffentlicht werden.

Deshalb kann zwischen dem Speichern im CMS und der sichtbaren Änderung auf der öffentlichen Webseite eine kurze Verzögerung entstehen.

Während dieser Verarbeitung sollte ein Beitrag nicht mehrfach gespeichert werden, nur weil die Änderung noch nicht unmittelbar auf der Webseite sichtbar ist.

---

# 24. News-Slider

Auf der Webseite werden aktuelle News zusätzlich über einen News-Slider hervorgehoben.

Der Slider wird automatisch aus den vorhandenen News erzeugt.

Dabei werden die **fünf aktuellsten News** verwendet.

Redakteure müssen Beiträge nicht zusätzlich in den Slider eintragen.

Soll eine ältere News aus dem Slider verschwinden, muss sie ebenfalls nicht manuell entfernt werden. Sobald neuere Beiträge vorhanden sind, ändert sich die Auswahl automatisch.

---

# 25. Bestehende News bearbeiten

Bestehende Beiträge können erneut über Pages CMS geöffnet werden.

Typische nachträgliche Änderungen sind:

* Tippfehler korrigieren
* falsche Uhrzeit korrigieren
* Links ergänzen
* Bilder ergänzen
* Ergebnisse nachtragen
* Formulierungen verbessern

Nach dem Speichern wird die Webseite erneut automatisch erzeugt.

## Keine neue News für kleine Korrekturen

Bei einem Tippfehler oder einer kleinen Ergänzung sollte normalerweise der bestehende Beitrag bearbeitet werden.

Es ist nicht notwendig, denselben Beitrag erneut als neue News anzulegen.

---

# 26. News löschen

Nicht mehr benötigte News können über Pages CMS gelöscht werden.

Nach dem Löschen verarbeitet die automatische News-Generierung die Änderung.

Dabei werden die von der News abhängigen Dateien ebenfalls aktualisiert.

Ein Beitrag sollte nur gelöscht werden, wenn er tatsächlich dauerhaft entfernt werden soll.

## Löschen oder bestehen lassen?

Alte News müssen nicht grundsätzlich gelöscht werden.

Vergangene:

* Veranstaltungen
* Spielberichte
* Vereinsmeisterschaften
* Saisonberichte
* Vereinsereignisse

können weiterhin als Vereinschronik beziehungsweise Archiv sinnvoll sein.

Eine News sollte daher nicht allein deshalb gelöscht werden, weil sie nicht mehr aktuell ist.

---

# 27. Was passiert technisch nach einer Änderung?

Für die normale Redaktion ist dieser Ablauf nicht erforderlich, kann aber bei der Fehlersuche hilfreich sein.

Vereinfacht läuft eine Änderung so ab:

**Pages CMS**

↓

**redaktionelle Inhaltsdatei wird gespeichert**

↓

**automatische News-Generierung**

↓

**News-Daten und Webseiten werden aktualisiert**

↓

**Webseite wird veröffentlicht**

Dazu existieren automatisierte Workflows.

Redakteure müssen diese normalerweise nicht manuell starten.

---

# 28. Niemals generierte Dateien manuell bearbeiten

Ein besonders wichtiger Punkt:

Bestimmte Dateien werden automatisch aus den redaktionellen Inhalten erzeugt.

Diese Dateien dürfen **nicht als eigentliche Quelle einer News verwendet oder manuell korrigiert werden**.

Eine manuelle Änderung könnte bei der nächsten automatischen Generierung wieder überschrieben werden.

Änderungen an einer News müssen deshalb immer an der dafür vorgesehenen redaktionellen Quelle vorgenommen werden – normalerweise über Pages CMS.

---

# 29. Galerie

Die Bildergalerie der Webseite ist technisch vom News-System getrennt.

News-Bilder werden deshalb **nicht automatisch zu Galerie-Bildern**.

Umgekehrt sind Galerie-Bilder nicht automatisch Bestandteil einer News.

Die Galerie besitzt eine eigene automatische Datenaufbereitung und sollte nicht über die News-Verwaltung gepflegt werden.

Die technische Pflege beziehungsweise der entsprechende Galerie-Ablauf wird separat dokumentiert.

---

# 30. Mannschaften, Ergebnisse und Tabellen

Mannschaftsinformationen, Spielergebnisse und Tabellen gehören nicht zum News-CMS.

Ein Teil dieser Daten wird automatisch verarbeitet beziehungsweise aus den dafür vorgesehenen Datenquellen erzeugt.

Redakteure sollten deshalb keine Ergebnisse oder Tabellenstände in technischen Dateien korrigieren.

Falls dort ein Fehler auftritt, sollte dieser an die technisch verantwortliche Person weitergegeben werden.

Natürlich können Ergebnisse zusätzlich in einem normalen Spielbericht erwähnt werden.

---

# 31. Technische Fehlermeldungen

Bei einer normalen redaktionellen Änderung sollte keine technische Bearbeitung erforderlich sein.

Tritt dennoch ein Fehler auf, sollte zuerst geprüft werden:

1. Wurde der Beitrag im CMS tatsächlich gespeichert?
2. Sind alle Pflichtfelder ausgefüllt?
3. Wurde ein Bild vollständig hochgeladen?
4. Besteht die Internetverbindung?
5. Ist die Änderung nach der Veröffentlichung weiterhin nicht sichtbar?

Wenn die Änderung danach weiterhin fehlt, sollte der Fehler an die technisch verantwortliche Person weitergegeben werden.

Hilfreich sind dabei:

* Titel des betroffenen Beitrags
* Zeitpunkt der Änderung
* kurze Beschreibung des Problems
* Screenshot der Fehlermeldung
* Information, was geändert werden sollte

Redakteure sollten bei technischen Fehlern **nicht eigenständig Dateien im GitHub-Repository verändern**, um das Problem zu umgehen.

---

# 32. Verhalten bei einer fehlerhaften Veröffentlichung

Falls nach einer Änderung auf der öffentlichen Webseite ein Fehler auffällt:

## Inhaltlicher Fehler

Beispiele:

* Tippfehler
* falsches Datum
* falsche Uhrzeit
* falscher Link

→ Beitrag im CMS korrigieren und erneut speichern.

## Darstellungsfehler

Beispiele:

* Layout verschoben
* Inhalt außerhalb des Bildschirms
* News-Seite lädt nicht
* Navigation funktioniert nicht
* Tabelle ist technisch beschädigt

→ Nicht versuchen, den Fehler über den News-Inhalt oder GitHub zu reparieren.

→ Technisch verantwortliche Person informieren.

---

# 33. Empfohlener Schreibstil

News sollten möglichst:

* sachlich
* freundlich
* verständlich
* nicht unnötig kompliziert
* für Mitglieder und Außenstehende nachvollziehbar

geschrieben werden.

Interne Abkürzungen sollten vermieden oder beim ersten Auftreten erklärt werden.

## Beispiel

Weniger gut:

> H1 gewinnt nach starkem Spiel das BK-Duell und steht jetzt 3:1.

Besser:

> Unsere Herren I gewinnen ihr Spiel in der Bezirksklasse und stehen damit nach vier Begegnungen bei drei Siegen und einer Niederlage.

---

# 34. Datenschutz und Persönlichkeitsrechte

Vor der Veröffentlichung personenbezogener Inhalte sollte geprüft werden, ob diese für die Vereinswebseite geeignet sind.

Besondere Vorsicht gilt bei:

* privaten Telefonnummern
* privaten E-Mail-Adressen
* Anschriften
* personenbezogenen Informationen
* Bildern von Personen
* insbesondere Bildern von Kindern und Jugendlichen

Nicht benötigte personenbezogene Daten sollten nicht veröffentlicht werden.

Im Zweifelsfall sollte vor der Veröffentlichung Rücksprache mit der verantwortlichen Person im Verein gehalten werden.

---

# 35. Keine vertraulichen Inhalte veröffentlichen

Die Vereinswebseite ist öffentlich erreichbar.

Alles, was über das CMS veröffentlicht wird, sollte deshalb grundsätzlich als öffentlich zugänglich betrachtet werden.

Nicht veröffentlicht werden sollten beispielsweise:

* interne Zugangsdaten
* Passwörter
* private Kontaktdaten ohne Freigabe
* interne Vereinsdiskussionen
* vertrauliche Dokumente
* interne technische Informationen

---

# 36. Redaktionelle Grundregel

Für die tägliche Arbeit gilt:

> **Inhalte über die dafür vorgesehene Redaktionsoberfläche pflegen – Technik nicht manuell verändern.**

Bei einer normalen News-Veröffentlichung muss ein Redakteur keine Dateien erzeugen, keine Skripte starten und keinen Quellcode bearbeiten.

---

# 37. Kurzablauf für eine neue News

* [ ] Pages CMS öffnen
* [ ] anmelden
* [ ] Bereich „News“ öffnen
* [ ] neue News erstellen
* [ ] Titel eintragen
* [ ] Datum kontrollieren
* [ ] benötigte Inhaltsblöcke hinzufügen
* [ ] Text schreiben und formatieren
* [ ] gegebenenfalls Bilder oder Tabellen ergänzen
* [ ] gegebenenfalls Eventankündigung ergänzen
* [ ] Beitrag kontrollieren
* [ ] speichern
* [ ] automatische Veröffentlichung abwarten
* [ ] öffentliche News-Seite kurz kontrollieren

---

# 38. Kurzablauf für eine Korrektur

* [ ] Pages CMS öffnen
* [ ] betreffende News auswählen
* [ ] Fehler korrigieren
* [ ] keine unnötigen anderen Inhalte verändern
* [ ] speichern
* [ ] veröffentlichte News kontrollieren

---

# 39. Kurzablauf zum Löschen einer News

* [ ] prüfen, ob die News wirklich dauerhaft entfernt werden soll
* [ ] betreffende News im CMS auswählen
* [ ] löschen
* [ ] Löschung bestätigen
* [ ] automatische Aktualisierung abwarten
* [ ] News-Übersicht kontrollieren

---

# 40. Zuständigkeiten

## Redaktion

Verantwortlich für:

* News-Inhalte
* Rechtschreibung
* Bilder innerhalb von News
* Veranstaltungsinformationen
* Links
* inhaltliche Aktualität

## Technische Betreuung

Verantwortlich für:

* Quellcode
* Seitenstruktur
* Design
* GitHub Pages
* Pages-CMS-Konfiguration
* automatische Workflows
* News-Generator
* Datenimporte
* Spielbetriebsdaten
* Galerie-Automatisierung
* technische Fehler
* Deployment
* Domain und HTTPS

---

# 41. Wichtigste Regeln zusammengefasst

1. News immer über **Pages CMS** bearbeiten.
2. Generierte Dateien niemals als Ersatz für das CMS bearbeiten.
3. Für normale News bevorzugt den **Textblock** verwenden.
4. Eventankündigungen nur für tatsächliche Veranstaltungen verwenden.
5. Bilder nur veröffentlichen, wenn sie dafür geeignet und freigegeben sind.
6. Links nach Möglichkeit kontrollieren.
7. Alte News müssen nicht automatisch gelöscht werden.
8. Technische Dateien nicht verändern.
9. Nach einer Veröffentlichung die öffentliche Webseite kurz kontrollieren.
10. Bei technischen Problemen lieber die technische Betreuung informieren, statt selbst am Quellcode Änderungen vorzunehmen.

---

# 42. Ansprechpartner

## Redaktionelle Fragen

**Ansprechpartner:** [Name eintragen]
**E-Mail:** [E-Mail-Adresse eintragen]

## Technische Fragen

**Ansprechpartner:** Sascha Warth
**E-Mail:** warth.sascha@outlook.de

---

# 43. Dokumentstand

**Webseite:** TTF Laudenbach
**Dokument:** Redaktionsdokumentation
**Stand:** August 2026

Diese Dokumentation beschreibt die redaktionelle Bedienung der Vereinswebseite. Technische Einrichtung, Architektur, automatisierte Workflows, Generatoren, Datenquellen und Wartungsarbeiten werden separat in der **Technikdokumentation** beschrieben.
