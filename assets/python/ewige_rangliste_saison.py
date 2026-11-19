#!/usr/bin/env python3
"""Öffentliche Saisonzahlen für die Ewige Rangliste, ohne Webabruf.

Liest die aktuelle Erwachsenen-Meldung, die Begegnungen der aktuellen Saison
und die beim Masterimport archivierten Begegnungen. Der GitHub-Pages-Deploy
erzeugt die JSON-Datei direkt im veröffentlichten Artefakt.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

from config import SAISON
from ewige_rangliste import ALIASES, iso_date, key, load_json, norm, write_json

ROOT = Path(__file__).resolve().parents[2]


def get_season(config=SAISON):
    parts = config.split("--")
    if len(parts) != 2 or not all(len(p) == 2 and p.isdigit() for p in parts):
        raise ValueError(f"Ungültiger Saisonbezeichner: {config}")
    start, end = map(int, parts)
    if end != (start + 1) % 100:
        raise ValueError(f"Saison muss aufeinanderfolgende Jahre enthalten: {config}")
    return f"20{start:02d}-{end:02d}", f"20{start:02d}/{end:02d}", f"20{start:02d}-07-01", f"20{end:02d}-06-30"


def canonical(name):
    clean = norm(name)
    return ALIASES.get(key(clean), clean)


def generate(root=ROOT, season=SAISON):
    slug, display_season, start, end = get_season(season)
    roster = load_json(root / "assets/data/spielerHerren.json")
    delta_path = root / f"content/ewige-rangliste/delta/{slug}.json"
    archive_path = root / f"content/ewige-rangliste/saison-archiv/{slug}.json"
    registered = {}
    for team, players in roster.items():
        if not isinstance(players, list) or not team.startswith("Herren "):
            continue
        for player in players:
            name = canonical(player.get("name", ""))
            if not name:
                continue
            k = key(name)
            entry = registered.setdefault(k, {"name": name, "mannschaften": set()})
            entry["mannschaften"].add(team)

    seen_events = set()
    appearances = Counter()
    event_names = {}
    encounter_count = 0
    for file in (archive_path, delta_path):
        if not file.exists():
            continue
        payload = load_json(file)
        if payload.get("saison") != display_season:
            raise ValueError(f"Falsche Saison in {file}: {payload.get('saison')}")
        for event in payload.get("begegnungen", []):
            event_date = iso_date(event["datum"])
            if not start <= event_date <= end:
                raise ValueError(f"Begegnung außerhalb der Saison: {event.get('id')}")
            event_id = str(event["id"])
            if event_id in seen_events:
                raise ValueError(f"Begegnung mehrfach im aktiven und archivierten Delta: {event_id}")
            seen_events.add(event_id)
            encounter_count += 1
            counted = set()
            for player in event.get("spieler", []):
                name = player if isinstance(player, str) else player.get("name", "")
                name = canonical(name)
                if not name:
                    continue
                k = key(name)
                if k in counted:
                    continue
                counted.add(k)
                appearances[k] += 1
                event_names.setdefault(k, name)

    names = set(registered) | set(appearances)
    records = []
    for k in sorted(names):
        registered_item = registered.get(k)
        records.append({
            "name": registered_item["name"] if registered_item else event_names[k],
            "einsätze": appearances[k],
            "gemeldet": registered_item is not None,
            "mannschaften": sorted(registered_item["mannschaften"]) if registered_item else []
        })
    delta = load_json(delta_path) if delta_path.exists() else {}
    return {
        "schemaVersion": 1,
        "saison": display_season,
        "saisonBeginn": start,
        "saisonEnde": end,
        "erfassteBegegnungen": encounter_count,
        "vollstaendigBis": delta.get("vollstaendigBis"),
        "unvollstaendig": bool(delta.get("fehler", [])) or delta.get("zuletztGeprueft") is None,
        "spieler": records
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "assets/data/ewigeRanglisteSaison.json")
    args = parser.parse_args()
    result = generate()
    write_json(args.output, result)
    print(f"Saison {result['saison']}: {len(result['spieler'])} Spieler, "
          f"{result['erfassteBegegnungen']} Begegnungen; Ziel: {args.output}")


if __name__ == "__main__":
    main()
