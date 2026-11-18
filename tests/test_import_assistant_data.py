"""Tests für den vorsichtigen Assistenten-Import."""
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "python"))
import import_assistant_data as mod


def row(date_string, result=None):
    return {"datum": date_string, "uhrzeit": "10:30", "spielort": "2",
            "heim": "TTF Laudenbach", "gast": "TSV Schrozberg",
            "ergebnis": result, "status": "gespielt" if result else "geplant"}


def match(result="9:2"):
    return {"datum": date.today().isoformat(), "heim": "TTF Laudenbach",
            "gast": "TSV Schrozberg", "ergebnis": result,
            "sourceUrl": "https://ttbw.click-tt.de/cgi-bin/WebObjects/nuLigaTTDE.woa/wa/clubInfoDisplay?club=3920"}


class ValidationTests(unittest.TestCase):
    def test_accepts_confirmed_result(self):
        items = mod.validate_matches([match()], "2026-09-18")
        self.assertEqual(len(items), 1)

    def test_rejects_missing_source_and_bad_result(self):
        bad = match()
        bad["sourceUrl"] = "https://example.org/result"
        with self.assertRaises(ValueError):
            mod.validate_matches([bad], "2026-09-18")
        bad = match("unknown")
        with self.assertRaises(ValueError):
            mod.validate_matches([bad], "2026-09-18")

    def test_rejects_conflicting_results(self):
        with self.assertRaises(ValueError):
            mod.validate_matches([match("9:2"), match("9:3")], "2026-09-18")

    def test_rejects_incomplete_table(self):
        with self.assertRaises(ValueError):
            mod.validate_tables([{"file": "tabelleHerren1.json",
                                  "sourceUrl": match()["sourceUrl"], "rows": []}])

    def test_rejects_fictional_roster(self):
        with self.assertRaises(ValueError):
            mod.validate_players({**match(), "spieler": [{"name": "Unbekannt"}]})

    def test_merges_without_deleting_unrelated_games(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "assets" / "data"
            feed = root / "content" / "assistant-import" / "aktuell.json"
            delta = root / "content" / "ewige-rangliste" / "delta" / "2026-27.json"
            for folder in (data, feed.parent, delta.parent):
                folder.mkdir(parents=True, exist_ok=True)
            saved = row(date.today().strftime("%a., %d.%m.%Y"))
            other = {"datum": "Fr., 25.04.2027", "uhrzeit": "19:00", "spielort": "1",
                     "heim": "TTF Laudenbach", "gast": "TSG Kirchberg",
                     "ergebnis": None, "status": "geplant"}
            games = data / "spieleHerren1.json"
            games.write_text(json.dumps([saved, other]), encoding="utf-8")
            delta.write_text(json.dumps({"saison": "2026/27", "begegnungen": [],
                                         "fehler": [], "vollstaendigBis": None,
                                         "zuletztGeprueft": None}), encoding="utf-8")
            feed.write_text(json.dumps({
                "schemaVersion": 1,
                "checkedAt": datetime.now(timezone.utc).isoformat(),
                "matches": [match()], "tables": []
            }), encoding="utf-8")
            with patch.object(mod, "GAMES", [games]), \
                 patch.object(mod, "INPUT", feed), \
                 patch.object(mod, "DATA", data), \
                 patch.object(mod, "DELTA", delta), \
                 patch.object(mod, "STATUS", data / "assistantStatus.json"), \
                 patch.object(mod, "load_active", return_value=({"stichtag": "2026-09-18"}, {})), \
                 patch.object(mod, "build") as build:
                mod.apply()
            output = json.loads(games.read_text(encoding="utf-8"))
            self.assertEqual(output[0]["ergebnis"], "9:2")
            self.assertEqual(output[0]["status"], "gespielt")
            self.assertIsNone(output[1]["ergebnis"])
            self.assertEqual(len(output), 2)
            build.assert_called_once()


if __name__ == "__main__":
    unittest.main()
