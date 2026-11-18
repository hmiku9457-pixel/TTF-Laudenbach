"""Offline-Tests der Ewigen Rangliste; benötigt keinen Netzwerkzugriff."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "assets" / "python" / "ewige_rangliste.py"
spec = importlib.util.spec_from_file_location("ewige_rangliste", MODULE_PATH)
ranking = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ranking)


class EwigeRanglisteTests(unittest.TestCase):
    def test_original_master(self):
        path = ranking.ROOT / "content/ewige-rangliste/master/master_2026-09-18_v1.csv"
        cutoff, players = ranking.parse_master(path)
        self.assertEqual(cutoff, "2026-09-18")
        self.assertEqual(len(players), 120)
        self.assertEqual(sum(p["spiele"] for p in players.values()), 12438)
        self.assertIn("peter pflüger", players)
        self.assertNotIn("peter pfüger", players)

    def test_invalid_master_and_export_format(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "sample.csv"
            file.write_text('Stand;18.09.2026\nName;Spiele\n"Johannes Scherrer";870\n"Peter Pflüger";3\n', encoding="utf-8")
            cutoff, players = ranking.parse_master(file)
            self.assertEqual((cutoff, players["peter pflüger"]["spiele"]), ("2026-09-18", 3))
            file.write_text("Stand;18.09.2026\nName;Spiele\nA;3\nA;4\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Doppelter"):
                ranking.parse_master(file)

    def temp_paths(self, path):
        content = path / "content/ewige-rangliste"
        master = content / "master"
        delta = content / "delta"
        incoming = content / "import"
        for p in (master, delta, incoming):
            p.mkdir(parents=True, exist_ok=True)
        original = ranking.ROOT / "content/ewige-rangliste/master/master_2026-09-18_v1.csv"
        (master / original.name).write_bytes(original.read_bytes())
        active = content / "aktiver-master.json"
        active.write_text(json.dumps({"datei": f"master/{original.name}", "stichtag": "2026-09-18", "version": 1}))
        output = path / "assets/data/ewigeRangliste.json"
        return content, delta, incoming, active, master, output

    def test_delta_deduplication_new_player_and_cutoff(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            content, delta, incoming, active, master, output = self.temp_paths(path)
            events = [
                {"id": "old", "datum": "2026-09-18", "spieler": [{"name": "Johannes Scherrer"}]},
                {"id": "a", "datum": "2026-09-19",
                 "spieler": [{"name": "Johannes Scherrer"}, {"name": "Johannes Scherrer"}, {"name": "Neuer Spieler", "personId": "1001"}]},
                {"id": "b", "datum": "2026-09-20", "spieler": [{"name": "Johannes Scherrer"}, {"name": "Unbekannt"}]},
            ]
            ranking.write_json(delta / "2026-27.json", {"saison": "2026/27", "begegnungen": events, "fehler": [],
                                                          "zuletztGeprueft": "2026-09-21T06:00:00Z", "vollstaendigBis": "2026-09-20"})
            with patch.multiple(ranking, CONTENT=content, ACTIVE=active, MASTER_DIR=master, DELTA_DIR=delta,
                                IMPORT_DIR=incoming, OUTPUT=output):
                actual = ranking.build()
                self.assertEqual(actual["anzahlBegegnungen"], 2)
                scherrer = next(x for x in actual["spieler"] if x["name"] == "Johannes Scherrer")
                self.assertEqual(scherrer["spiele"], 872)
                self.assertTrue(actual["unvollstaendig"])
                self.assertEqual(actual["exportStichtag"], "2026-09-19")
                self.assertEqual(next(x for x in actual["spieler"] if x["name"] == "Neuer Spieler")["spiele"], 1)
                self.assertEqual(scherrer["exportSpiele"], 871)

    def test_master_import_prunes_deltas_and_keeps_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            content, delta, incoming, active, master, output = self.temp_paths(path)
            old = ranking.ROOT / "content/ewige-rangliste/master/master_2026-09-18_v1.csv"
            _, players = ranking.parse_master(old)
            csvtext = "Stand;20.09.2026\nName;Spiele\n" + "\n".join(
                f'"{p["name"].replace(chr(34), chr(34)*2)}";{p["spiele"]}' for p in players.values()
            ) + "\n"
            (incoming / "korrektur.csv").write_text(csvtext, encoding="utf-8")
            ranking.write_json(delta / "2026-27.json", {
                "saison": "2026/27", "begegnungen": [
                    {"id": "one", "datum": "2026-09-19", "spieler": [{"name": "Paul Stumpp"}]},
                    {"id": "two", "datum": "2026-09-21", "spieler": [{"name": "Paul Stumpp"}]}
                ], "fehler": [], "zuletztGeprueft": "2026-09-22T08:00:00Z",
                "vollstaendigBis": "2026-09-21"})
            with patch.multiple(ranking, CONTENT=content, ACTIVE=active, MASTER_DIR=master, DELTA_DIR=delta,
                                IMPORT_DIR=incoming, OUTPUT=output):
                ranking.build()
                ranking.import_master()
                new_active = ranking.load_json(active)
                self.assertEqual(new_active["stichtag"], "2026-09-20")
                self.assertTrue((master / "master_2026-09-18_v1.csv").exists())
                self.assertTrue((master / "master_2026-09-20_v1.csv").exists())
                self.assertEqual(len(ranking.load_json(delta / "2026-27.json")["begegnungen"]), 1)
                self.assertFalse((incoming / "korrektur.csv").exists())
                final = ranking.load_json(output)
                paul = next(x for x in final["spieler"] if x["name"] == "Paul Stumpp")
                self.assertEqual(paul["spiele"], 841)

    def test_unsafe_master_rejected_without_deleting_upload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            content, delta, incoming, active, master, output = self.temp_paths(path)
            master_file = master / "master_2026-09-18_v1.csv"
            cutoff, players = ranking.parse_master(master_file)
            newer = incoming / "master.csv"
            newer.write_text("Stand;21.09.2026\nName;Spiele\n" +
                "\n".join(f'{p["name"]};{p["spiele"]}' for p in players.values()) + "\n", encoding="utf-8")
            ranking.write_json(delta / "2026-27.json", {
                "saison": "2026/27", "begegnungen": [], "fehler": [],
                "zuletztGeprueft": None, "vollstaendigBis": None
            })
            with patch.multiple(ranking, CONTENT=content, ACTIVE=active, MASTER_DIR=master, DELTA_DIR=delta,
                                IMPORT_DIR=incoming, OUTPUT=output):
                ranking.build()
                with self.assertRaisesRegex(ValueError, "ungeprüfter|fehlender|fehlender/ungeprüfter"):
                    ranking.import_master()
                self.assertTrue(newer.exists())
                self.assertEqual(ranking.load_json(active)["stichtag"], cutoff)


if __name__ == "__main__":
    unittest.main()
