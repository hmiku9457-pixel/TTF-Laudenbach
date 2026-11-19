"""Offline-Tests für Meldungsmarkierung und Saisoneinsätze."""
import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assets/python"))
from ewige_rangliste_saison import generate, get_season


class EwigeRanglisteSaisonTests(unittest.TestCase):
    def test_current_season_and_roster(self):
        result = generate(ROOT, "26--27")
        self.assertEqual(result["saison"], "2026/27")
        self.assertGreaterEqual(result["erfassteBegegnungen"], 25)
        players = {p["name"]: p for p in result["spieler"]}
        self.assertEqual(players["Dietrich Kruth"]["einsätze"], 13)
        self.assertEqual(players["Steffen Wolfert (ehem. Fahrbach)"]["einsätze"], 5)
        self.assertTrue(players["Steffen Wolfert (ehem. Fahrbach)"]["gemeldet"])
        self.assertTrue(players["Andre Metzger"]["gemeldet"])
        self.assertEqual(players["Andre Metzger"]["einsätze"], 0)
        self.assertTrue(players["Johannes Scherrer"]["gemeldet"])
        self.assertEqual(players["Johannes Scherrer"]["einsätze"], 0)

    def make_root(self, folder):
        root = Path(folder)
        roster = root / "assets/data/spielerHerren.json"
        roster.parent.mkdir(parents=True)
        roster.write_text(json.dumps({"Herren 1": [
            {"name": "Steffen Wolfert"},
            {"name": "Testperson ohne Einsatz"}
        ]}), encoding="utf-8")
        return root

    def write_events(self, root, part, events):
        target = root / f"content/ewige-rangliste/{part}/2026-27.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"saison": "2026/27", "begegnungen": events,
            "fehler": [], "zuletztGeprueft": "2026-11-18T09:00:00Z",
            "vollstaendigBis": "2026-11-17"}), encoding="utf-8")

    def test_master_archive_preserves_full_season_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            self.write_events(root, "saison-archiv", [
                {"id": "a", "datum": "2026-09-19", "spieler": [
                    {"name": "Steffen Wolfert", "personId": "99"},
                    {"name": "Steffen Wolfert", "personId": "99"}]}
            ])
            self.write_events(root, "delta", [
                {"id": "b", "datum": "2026-11-18", "spieler": [
                    {"name": "Steffen Wolfert (ehem. Fahrbach)", "personId": "99"}]}
            ])
            result = generate(root, "26--27")
            players = {p["name"]: p for p in result["spieler"]}
            self.assertEqual(result["erfassteBegegnungen"], 2)
            self.assertEqual(players["Steffen Wolfert (ehem. Fahrbach)"]["einsätze"], 2)
            self.assertEqual(players["Testperson ohne Einsatz"]["einsätze"], 0)
            self.assertTrue(players["Testperson ohne Einsatz"]["gemeldet"])

    def test_duplicate_meeting_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            event = {"id": "one", "datum": "2026-09-19", "spieler": [{"name": "Steffen Wolfert"}]}
            self.write_events(root, "saison-archiv", [event])
            self.write_events(root, "delta", [event])
            with self.assertRaisesRegex(ValueError, "mehrfach"):
                generate(root, "26--27")

    def test_wrong_season_rejected(self):
        with self.assertRaisesRegex(ValueError, "aufeinanderfolgende"):
            get_season("26--28")


if __name__ == "__main__":
    unittest.main()
