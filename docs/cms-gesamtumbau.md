# Webseitenverwaltung – Teststand
Die CMS-Einträge unter content/site sind die redaktionelle Quelle. Die HTML-Dateien mit CMS-Platzhaltern sind technische Vorlagen. Das Deployment erzeugt daraus HTML im Pages-Artefakt; nicht im Repository bearbeiten. News-System und sportlicher Datenimport bleiben bestehen.

## Redaktion
Pages CMS öffnen, Repository und Testbranch cms-gesamtumbau auswählen. Training, Verein, Beiträge, Mannschaftsführer/Fotos, Sponsoren, Links, PDF-Dokumente, Newsletter und Header-Willkommenstext sind getrennte Formulare. Neue Alben können mit hochgeladenen Fotos und Bildbeschreibungen angelegt werden; historische Ordner bleiben zunächst automatisch verwaltet. Newsletter nutzt den bisherigen News-Baukasten. Das Speichern auf main löst später die Veröffentlichung aus; der Testbranch veröffentlicht nicht die Live-Seite.

## Gesamttest
- Training ändern: Startseite und Aktiver Spielbetrieb müssen denselben Wert zeigen.
- Hallennamen und Karte prüfen; Karte erst nach Zustimmung laden.
- Ausschuss, Ehrenmitglieder und Beiträge bearbeiten; mobile Tabellen prüfen.
- Sponsor hinzufügen/entfernen: Sponsorenseite, Footer und Links prüfen.
- Satzung/Beitrittsformular aktualisieren: Navigation, Dokumente und andere Verweise prüfen.
- Mannschaftsführer und optionales Foto bearbeiten; Tabellen und Spielpläne prüfen.
- Neues Album mit mehreren Fotos anlegen, Newsletter-Blöcke hinzufügen.
- News und automatischen Sportdatenimport nach Freigabe auf main unverändert prüfen.
- Keine vertraulichen Dateien hochladen. Rechte und Live-Vorschau separat testen.

## Noch offen
Allgemeiner Seitenbaukasten außerhalb des Newsletters, bestehende historische Alben im CMS, frei pflegbare Navigation, rechtliche Texte, exakte Live-Vorschau und Rollenmodell. Bestehende HTML-Seiten sind für Layout und dynamische Funktionen weiterhin Vorlagen. Alte Links aus dem manuellen Scraper werden im Deployment durch die redaktionellen Links ersetzt.

## Testartefakt
GitHub Actions > CMS Gesamttest > erfolgreicher Lauf > cms-testseite herunterladen, entpacken und im entpackten Verzeichnis einen lokalen Webserver starten (z. B. python -m http.server 8000). Im Browser http://localhost:8000 öffnen. Absolute Pfade funktionieren nicht über file://.
