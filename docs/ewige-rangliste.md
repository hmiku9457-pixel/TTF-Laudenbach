# Ewige Rangliste – Betrieb und Master-Import

Die Vereinsrangliste wird nicht mehr in der HTML-Tabelle gepflegt.

## Datenmodell
- `content/ewige-rangliste/master/master_YYYY-MM-DD_vN.csv`: unveränderliche historische Masterstände
- `content/ewige-rangliste/aktiver-master.json`: aktivierte Masterversion
- `content/ewige-rangliste/delta/YYYY-YY.json`: saisonweise Begegnungen nach dem Masterstichtag und offene Auslesefehler
- `assets/data/ewigeRangliste.json`: berechnete öffentliche Ansicht und sichere Exportwerte
- `content/ewige-rangliste/import/`: Uploadordner für neue CSVs

**Zählregel:** Nur Erwachsene, pro Spieler und Mannschaftsbegegnung ein Einsatz (unabhängig von Einzel-/Doppelspielen). Begegnungen **bis einschließlich** Masterstichtag zählen nicht im Delta. Vereineigene Begegnungen zählen beide TTF-Aufstellungen. Unbekannte Spieler werden nur dann automatisch neu aufgenommen, wenn die Quelle eine eindeutige Personenkennung bereitstellt. Ansonsten erscheint ein Warnhinweis.

## Master hochladen

1. Auf der Seite "Ewige Rangliste" **CSV exportieren**. Der CSV-Stand ist höchstens der letzte nachweislich vollständig geprüfte Kalendertag, nicht zwangsläufig heute.
2. CSV mit Excel bearbeiten und wieder als CSV (UTF-8) speichern.
3. **Neue Datei mit eindeutigem Namen** in `content/ewige-rangliste/import/` auf GitHub hochladen; die bestehenden Masterdateien **nicht** bearbeiten.
4. GitHub Action **Ewige Rangliste – Master importieren** validiert sie automatisch und aktiviert sie ohne weitere Bestätigung. Bei einem Fehler bleibt der bisherige Master erhalten.
5. Die Aktion legt die neue Datei als `master_YYYY-MM-DD_vN.csv` im Archiv ab, entfernt alle Begegnungen `<=` neuem Datum aus den aktuellen Delta-Dateien und berechnet die Website-Datei neu.

Ein höherer Stichtag ist nur möglich, wenn die automatische Erfassung **bis mindestens zu diesem Stichtag vollständig** war. Bereits importierte Masterversionen bleiben erhalten. Bei demselben Datum wird eine neue Versionsnummer erzeugt. Alle Änderungen werden von GitHub im Commit-Verlauf nachvollziehbar protokolliert.

## CSV-Formate

Aktueller Export:
```csv
"Stand";"18.09.2026"
"Name";"Spiele"
"Johannes Scherrer";"870"
```
Das ursprüngliche fünffeldrige CSV-Format mit dem "(Stand ...)"-Kopf und historischem 2019-Vergleich wird weiterhin unterstützt.

## Saisonwechsel und Delta

Beim Saisonwechsel müssen wie bisher `SAISON` und die Erwachsenen-Mannschaftslinks in `assets/python/config.py` aktualisiert werden. Der Scraper erzeugt automatisch eine neue `delta/YYYY-YY.json` und behält ältere saisonale Deltas, solange sie nicht im Master aufgehen.

Der bestehende tägliche Workflow ruft nach dem regulären Scraper `assets/python/scrape_ewige_rangliste.py` auf. Bei einzelnen fehlenden Spielberichten bleiben bereits bekannte Einträge erhalten; andere Ergebnisse werden weiter verarbeitet. Warnungen erscheinen auf der Website. Die automatische Auswertung ist **nur dann als vollständig zu verstehen**, wenn alle fünf Erwachsenenmannschaftsseiten und ihre relevanten Berichte erreichbar und eindeutig auswertbar waren.

## Entwicklung und Test

```bash
python -m unittest discover -s tests -p 'test_ewige_rangliste.py' -v
python assets/python/ewige_rangliste.py build
```

**Hinweis vor der Aktivierung:** Der Spielberichtparser arbeitet bewusst konservativ. Die CSS/DOM-Struktur der aktuellen myTischtennis-Spielberichtseiten muss im GitHub-Actions-Lauf mit echten Begegnungen geprüft werden. Wenn die Trennung der TTF-Spieler von den Gegnern nicht eindeutig gelingt, wird nichts hinzuerfunden und stattdessen eine Warnung protokolliert. Außerdem muss der für automatisierte Abrufe vorgesehene Zugriff auf die Quelle geklärt sein.
