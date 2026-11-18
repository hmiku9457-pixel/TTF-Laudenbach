# Täglicher ChatGPT-Datenabgleich

## Ablauf

Die in ChatGPT eingerichtete Aufgabe prüft jeden Morgen um 07:00 Uhr (Europe/Berlin)
die fünf Erwachsenen- und zwei Jugendmannschaften der TTF Laudenbach.
Sie sucht insbesondere nach seit dem 01.11.2026 fehlenden Ergebnissen und
offiziellen Spielberichten.

Nur **verifizierte Originalquellen** dürfen in
`content/assistant-import/aktuell.json` landen. Der ChatGPT-Agent ändert
**keine produktiven Website-Daten direkt**. Die GitHub Action
`assistant-import.yml` validiert den Eingang, führt nur sichere Änderungen
durch, erzeugt die Ewige Rangliste und veröffentlicht anschließend die Seite.

Der bisherige HTML-Scraper ist als manuelle Alt-Option erhalten,
seine tägliche GitHub-Schedule wird abgeschaltet. Falls der Push des
ChatGPT-Dateneingangs kein GitHub-Ereignis auslöst, versucht eine zusätzliche
GitHub-Actions-Schedule täglich um 07:45 UTC, die letzte Eingangsdatei zu
verarbeiten (im Winter 08:45 Uhr, im Sommer 09:45 Uhr in Deutschland).

## JSON-Format für ChatGPT

```json
{
  "schemaVersion": 1,
  "checkedAt": "2026-11-19T07:10:00+01:00",
  "matches": [
    {
      "datum": "2026-11-15",
      "heim": "TTF Laudenbach",
      "gast": "TSV Schrozberg",
      "ergebnis": "9:2",
      "sourceUrl": "https://ttbw.click-tt.de/EXAKTE-ORIGINALSEITE"
    }
  ],
  "tables": []
}
```

Dieses Beispiel ist **keine Importfreigabe**: Der Quellenlink ist nur ein
Platzhalter. Daten erst nach direkter fachlicher Prüfung übernehmen.

Pflicht bei jeder Begegnung: genaues Datum, Heim und Gast, Mannschaftsergebnis
und ein überprüfbarer Link zur Originalseite. Keine Suchmaschinen-Snippets,
keine geschätzten Resultate, keine nachträglich erfundenen Begegnungs-IDs.

Wenn der vollständige offizielle Spielbericht **alle** tatsächlich
eingesetzten TTF-Spieler belegt und eine echte Begegnungs-ID enthält,
dürfen zusätzlich folgende Felder eingetragen werden:

```json
{
  "meetingId": "12345678",
  "reportUrl": "https://ttbw.click-tt.de/EXAKTER-BERICHT",
  "spieler": [
    {"name": "Vorname Nachname", "personId": "12345"}
  ]
}
```

Die Werte sind reine Schemabeispiele, keine echten Spieler oder Spielberichte.
Keine Personen von Mannschaftsmeldungen übernehmen oder aus Resultaten
ableiten. Jugendspiele zählen **nicht** zur Ewigen Erwachsenen-Rangliste.

Tabellen dürfen als vollständiger Schnappschuss geliefert werden:
`tables[] = { "file": "tabelleHerren1.json", "sourceUrl": "...",
"rows": [...] }`. Jede Zeile benötigt die neun bisherigen Felder
`rang`, `mannschaft`, `partien`, `siege`, `unentschieden`,
`niederlagen`, `spiele`, `spieleDifferenz`, `punkte`.
Die Mannschaften Herren II und III teilen sich dieselbe Tabelle;
deshalb gegebenenfalls beide Tabellendateien auf denselben Stand bringen.

## Grenzen und Fehlerbehandlung

- Der Import aktualisiert zunächst ausschließlich **bekannte Begegnungen**.
  Neue oder verschobene Spielansetzungen werden nicht automatisch erzeugt.
- Ein widersprüchliches Ergebnis führt zum Abbruch statt zum Überschreiben.
- Ohne vollständigen Nachweis wird der Export-Stichtag der Ewigen Rangliste
  nicht erhöht. Fehlende Spieleraufstellungen bleiben sichtbar.
- Nur erfolgreich geprüfte Änderungen werden veröffentlicht. Ein Fehler
  verändert keine Dateien auf GitHub; eine gescheiterte Ausführung
  erfordert eine Kontrolle in GitHub Actions.
- Keine Umgehung von Zugriffskontrollen oder gegen Nutzungsbedingungen
  verstoßende automatische Abfragen.
- ChatGPT-Aufgaben und GitHub-Zugriff können ausfallen. Die letzte gültige
  Version bleibt dann erhalten; dies ist kein garantierter Echtzeit-Feed.
- `assets/data/assistantStatus.json` protokolliert den letzten Import.

## Testen

```bash
python -m unittest discover -s tests -p "test_import_assistant_data.py" -v
python assets/python/import_assistant_data.py
```

Der zweite Befehl verändert bei gültigem, nichtleerem Import lokal die
Ziel-JSON-Dateien; nur auf einem Testbranch oder mit gesicherten Daten ausführen.
