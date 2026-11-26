# Webseitenverwaltung – Teststand
Die CMS-Einträge unter content/site sind die redaktionelle Quelle. Die HTML-Dateien mit CMS-Platzhaltern sind technische Vorlagen. Das Deployment erzeugt daraus HTML im Pages-Artefakt; nicht im Repository bearbeiten. News-System und sportlicher Datenimport bleiben bestehen.

## Redaktion
Pages CMS öffnen, Repository und Testbranch cms-gesamtumbau auswählen. Training, Verein, Beiträge, Mannschaftsführer/Fotos, Sponsoren, Links, PDF-Dokumente, Newsletter und Header-Willkommenstext sind getrennte Formulare. Neue Alben können mit hochgeladenen Fotos und Bildbeschreibungen angelegt werden; historische Ordner bleiben zunächst automatisch verwaltet. Unter Seitenbaukasten können zusätzliche frei sortierbare Inhaltsblöcke auf sieben vorhandenen Seiten eingefügt werden; auch der Newsletter nutzt den erweiterten Baukasten. Text, zwei Spalten, Veranstaltung, Einzelbild, externer Button, PDF-Download, Hinweisbox, Trenner und Abstand sind verfügbar. Das Speichern auf main löst später die Veröffentlichung aus; der Testbranch veröffentlicht nicht die Live-Seite.

## Gesamttest
- Training ändern: Startseite und Aktiver Spielbetrieb müssen denselben Wert zeigen.
- Hallennamen und Karte prüfen; Karte erst nach Zustimmung laden.
- Ausschuss, Ehrenmitglieder und Beiträge bearbeiten; mobile Tabellen prüfen.
- Sponsor hinzufügen/entfernen: Sponsorenseite, Footer und Links prüfen.
- Satzung/Beitrittsformular aktualisieren: Navigation, Dokumente und andere Verweise prüfen.
- Mannschaftsführer und optionales Foto bearbeiten; Tabellen und Spielpläne prüfen.
- Neues Album mit mehreren Fotos anlegen, Newsletter-Blöcke hinzufügen.
- Zusätzliche Seitenblöcke auf Startseite und Vereinsseite hinzufügen, umsortieren und wieder entfernen.
- News und automatischen Sportdatenimport nach Freigabe auf main unverändert prüfen.
- Keine vertraulichen Dateien hochladen. Rechte und Live-Vorschau separat testen.

## Noch offen
Freie Neuanordnung der bestehenden festen Seitenbereiche, beliebige neue Unterseiten, bestehende historische Alben im CMS, frei pflegbare Navigation, rechtliche Texte, exakte Live-Vorschau und Rollenmodell. Bestehende HTML-Seiten sind für Layout und dynamische Funktionen weiterhin Vorlagen. Der manuelle Scraper liest die redaktionellen Links ebenfalls aus content/site.

## Testartefakt
GitHub Actions > CMS Gesamttest > erfolgreicher Lauf > cms-testseite herunterladen, entpacken und im entpackten Verzeichnis einen lokalen Webserver starten (z. B. python -m http.server 8000). Im Browser http://localhost:8000 öffnen. Absolute Pfade funktionieren nicht über file://.

## Redaktionelle Abnahme am 26.11.2026
Alle 14 Punkte des Nutzertests wurden als bestanden gemeldet: CMS-Menü, Training, Spiellokale, Vereinsinformationen, Mitgliedschaft, Sponsoren, Mannschaften, Dokumente, Links, Galerie, Newsletter, Seitenbaukasten, Seiteneinstellungen und mobile Darstellung.
Der automatische Build nach CMS-Speicherung zeigte jedoch, dass vollständig leere Mannschaftsobjekte entfernt werden können. Der Generator behandelt fehlende optionale Mannschaftsangaben nun als leer; Regressionstest ergänzt.
Vor Produktivfreigabe die im Testbranch gespeicherten redaktionellen Änderungen (Mitgliedschaftstexte, Mannschaftsführer Herren III und hochgeladenes Galeriebild) auf beabsichtigte Übernahme prüfen. Sie wurden nicht automatisch zurückgesetzt.
Nächster Entwicklungsabschnitt: vollständige Inhaltsverwaltung (bestehende Fotoalben, flexible Seitenlayouts, neue Unterseiten und Navigation), danach redaktioneller Komfort und Produktivfreigabe.

## Phase B1–B4: vollständige Inhaltsverwaltung
- **Fotoalben:** Die beiden vorhandenen Alben (19 Bilder) sind nun im Formular enthalten. Reihenfolge, Titel, Beschreibung, Datum, Bilder und Alt-Texte sind änderbar. Entfernen eines Bildes aus dem Album entfernt die Anzeige, nicht automatisch die Datei. Alte Bildpfade wurden für bestehende Links beibehalten; die CMS-Kopien liegen unter assets/images/gallery.
- **Seitenlayouts:** Die bestehenden Funktionsbereiche von sieben Seiten können als Gruppen verschoben werden. Zusätzliche Bausteine sind innerhalb der Gruppe frei sortierbar; ihre Position und Breite sind änderbar. Entfernte Pflichtbereiche werden automatisch ergänzt. Neue Bausteine: Überschrift, drei Spalten, Bilderreihe.
- **Eigene Unterseiten:** Neue Seiten beginnen als Entwurf. Veröffentlichen aktivieren und speichern; URL /pages/individuell/<dateiname>.html. Titeländerungen ändern nicht die URL. Optional automatisch im Hauptmenü anzeigen oder über Navigation & Footer verlinken. Beim Löschen oder Deaktivieren verschwinden Seite, Sitemap-Eintrag und generierte Menüverweise beim nächsten Build. Öffentliches Repository: Entwürfe sind nicht vertraulich.
- **Navigation & Footer:** Hauptmenü und eine Untermenüebene sind frei sortierbar. Ziele: vorhandene Seiten, neue Unterseiten über Auswahl, externe URLs. Die Beschriftung ist optional; Standard ist der Seitentitel. Footer-Links, Copyright-Name und Sponsorenanzeige sind editierbar. Kontakt, Impressum und Datenschutz werden automatisch ergänzt. Bestehende Sportseiten bleiben erhalten, auch wenn Menülinks entfernt werden.
- **Test:** Bestehendes Album umbenennen und Bild umsortieren; anschließend wiederherstellen. Auf der Startseite zusätzliche Inhalte zwischen die Funktionsgruppen verschieben. Neue Unterseite als Entwurf anlegen, veröffentlichen, in Menü und Footer verlinken, Titel ändern, Seite löschen; nach jedem Speichern neuestes erfolgreiches Artefakt laden. Menü und Dropdowns auch auf Mobilgeräten prüfen. Testdaten vor der Freigabe entfernen.

## Abnahme B1–B4 am 26.11.2026
21 von 23 manuellen Prüfpunkten bestanden. B1 (5/5), B3 (5/5) und B4 (8/8) vollständig abgenommen. B2 (3/5): Funktionsbereiche verschieben, zusätzliche Inhalte zwischen Funktionsbereichen platzieren und Inhaltsbreite wechseln bestanden. Noch nicht getestet: Drei-Spalten-Baustein sowie Bilderreihe und Überschrift (gemeinsamer Prüfpunkt). Keine Fehler in diesen beiden Punkten gemeldet; keine Abnahme unterstellen. Die offenen Prüfungen beim nächsten Gesamttest erneut aufnehmen. Alle drei automatischen GitHub-Prüfungen des getesteten Branchstands erfolgreich. Nächster Abschnitt: C1 visuelle Vorschau und C2 Benutzerrechte und Veröffentlichungsstatus. Produktivfreigabe erst nach Abschluss der offenen Abnahmen und Prüfung der Testdaten.
