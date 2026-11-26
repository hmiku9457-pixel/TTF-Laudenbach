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

## Phase C – Vorschau, Veröffentlichungsstand und Berechtigungen
C1: Der Workflow erstellt neben dem interaktiven Artefakt cms-testseite die visuelle Vorschau cms-visuelle-vorschau (Vorschau.html + Desktop-/Mobilbilder + bericht.json). Alle Seiten des gespeicherten Builds werden mit Chromium gerendert. Entwürfe eigener Seiten und geplante News sind nur in der gesonderten Vorschau enthalten. Externe Requests sind blockiert, es werden keine Formulare abgesendet. Sehr lange Seiten können als gekennzeichneter Ausschnitt erfasst werden. Die Vorschau ist kein interaktives Online-Staging und umfasst keine ungespeicherten Änderungen.
C2: CMS-Menü Vorschau & Veröffentlichungsstatus, Links zu Prüf- und Deploymentläufen, Ergebniszusammenfassungen, Commit-/Zeitstempel in cms-stand.json und redaktionsstatus.html. Live-Status erst nach Freigabe auf main. Produktionsbuild führt die CMS-Regressionstests vor dem Upload aus. Schaltfläche Vorschau und Inhaltsprüfung nutzt Pages-CMS-Actions; manuelles workflow_dispatch erfordert den Workflow auf dem Standardbranch. Automatische Builds auf Testbranch funktionieren unabhängig davon.
Rollen: E-Mail-Collaborators können redaktionelle Inhalte/Medien bearbeiten, nicht .pages.yml oder Benutzerverwaltung. Administratoren behalten GitHub-Zugang. Keine granularen Rollen oder erzwungenen Freigaben pro Sammlung/Branch; Review-Branch und PR sind ein organisatorischer Ablauf. Keine tatsächlichen Einladungen, Berechtigungs- oder Branchschutzänderungen ohne Zustimmung. Commit-Identität bleibt app, damit keine zusätzlichen persönlichen E-Mail-Adressen in öffentlichen Commit-Metadaten erscheinen.
Test: Vorschau öffnen ohne lokalen Server; Desktop/Mobil umschalten; Entwurf und geplante News in Vorschau, nicht im regulären Testartefakt prüfen; Commit-Stand vergleichen; ungültige Eingabe muss Build verhindern; CMS-Schaltfläche erst nach Merge testbar; E-Mail-Einladung mit autorisiertem Testredakteur separat prüfen. Offene B2-Prüfpunkte bleiben Drei-Spalten-Baustein sowie Bilderreihe und Überschrift.

## Phase D – technische Freigabe 26.11.2026
Auf ausdrücklichen Wunsch des Auftraggebers werden die offenen manuellen Abnahmen B2 und C organisatorisch freigegeben, jedoch nicht als tatsächlich durchgeführte manuelle Tests dokumentiert. Automatische Prüfungen der Phase C waren erfolgreich. Die beiden Teständerungen an Mitgliedschaft und Mannschaften wurden auf den Stand vor den manuellen Tests zurückgesetzt, das nicht referenzierte Test-Galeriebild wird entfernt. Historische Bilder bleiben erhalten. CMS-Menü in vier thematische Gruppen gegliedert. Rechtstexte sind strukturiert im CMS pflegbar; alte TMG-Referenzen und Register-Platzhalter entfallen. Registergericht, Registernummer, Vertretung und Anschrift sowie datenschutzrechtliche Details müssen vom Verein noch bestätigt werden. Keine Benutzer eingeladen oder Rechte ausgeweitet. Technische Rückfalloption: Revert statt Reset von main. Live-Freigabe erfolgt per PR #11.
