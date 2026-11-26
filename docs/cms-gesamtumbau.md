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
