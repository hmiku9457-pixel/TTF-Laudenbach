#!/usr/bin/env python3
"""Validiert vom Scraper erzeugte Kandidaten vor der Übernahme."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GAME_KEYS = {"datum", "uhrzeit", "spielort", "heim", "gast", "ergebnis"}
TABLE_KEYS = {
    "rang",
    "mannschaft",
    "partien",
    "siege",
    "unentschieden",
    "niederlagen",
    "spiele",
    "spieleDifferenz",
    "punkte",
}
PLAYER_KEYS = {"rang", "position", "name", "qttr", "a", "status"}
LINK_KEYS = {"spielplaene", "tabellen", "spielerlisten", "links"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--allow-large-drop",
        action="store_true",
        help="Große Datenrückgänge ausnahmsweise erlauben.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Ungültiges JSON in {path}: {error}") from error


def managed_names(directory: Path) -> set[str]:
    names: set[str] = set()
    for pattern in ("spiele*.json", "tabelle*.json", "spieler*.json"):
        names.update(path.name for path in directory.glob(pattern) if path.is_file())
    if (directory / "links.json").is_file():
        names.add("links.json")
    return names


def require_object_list(data: Any, filename: str) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        raise ValueError(f"{filename}: erwartet wird eine JSON-Liste.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{filename}: alle Listeneinträge müssen Objekte sein.")
    return data


def require_keys(item: dict[str, Any], keys: set[str], context: str) -> None:
    missing = sorted(keys - item.keys())
    if missing:
        raise ValueError(f"{context}: fehlende Felder: {', '.join(missing)}")


def validate_games(data: Any, filename: str) -> None:
    rows = require_object_list(data, filename)
    for index, item in enumerate(rows, start=1):
        require_keys(item, GAME_KEYS, f"{filename} Zeile {index}")
        if not str(item.get("heim") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: heim ist leer.")
        if not str(item.get("gast") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: gast ist leer.")


def validate_table(data: Any, filename: str) -> None:
    rows = require_object_list(data, filename)
    for index, item in enumerate(rows, start=1):
        require_keys(item, TABLE_KEYS, f"{filename} Zeile {index}")
        if not str(item.get("mannschaft") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: mannschaft ist leer.")


def validate_players(data: Any, filename: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{filename}: erwartet wird ein Objekt mit Mannschaften.")
    for team, players in data.items():
        if not isinstance(team, str) or not team.strip():
            raise ValueError(f"{filename}: ungültiger Mannschaftsname.")
        if not isinstance(players, list):
            raise ValueError(f"{filename}: {team} muss eine Spielerliste sein.")
        for index, player in enumerate(players, start=1):
            if not isinstance(player, dict):
                raise ValueError(f"{filename}: {team} Spieler {index} ist kein Objekt.")
            require_keys(player, PLAYER_KEYS, f"{filename}: {team} Spieler {index}")
            if not str(player.get("rang") or "").strip():
                raise ValueError(f"{filename}: {team} Spieler {index}: rang ist leer.")
            if not str(player.get("name") or "").strip():
                raise ValueError(f"{filename}: {team} Spieler {index}: name ist leer.")


def validate_links(data: Any, filename: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{filename}: erwartet wird ein JSON-Objekt.")
    require_keys(data, LINK_KEYS, filename)
    for key in LINK_KEYS:
        if not isinstance(data[key], list):
            raise ValueError(f"{filename}: {key} muss eine Liste sein.")


def validate_schema(filename: str, data: Any) -> None:
    # "spieler..." beginnt ebenfalls mit "spiele"; daher zuerst prüfen.
    if filename.startswith("spieler"):
        validate_players(data, filename)
    elif filename.startswith("spiele"):
        validate_games(data, filename)
    elif filename.startswith("tabelle"):
        validate_table(data, filename)
    elif filename == "links.json":
        validate_links(data, filename)


def item_count(filename: str, data: Any) -> int:
    if filename.startswith(("spiele", "tabelle")) and isinstance(data, list):
        return len(data)
    if filename.startswith("spieler") and isinstance(data, dict):
        return sum(len(value) for value in data.values() if isinstance(value, list))
    if filename == "links.json" and isinstance(data, dict):
        return sum(len(data.get(key, [])) for key in LINK_KEYS)
    return 0


def validate_drop(
    filename: str,
    before_data: Any,
    candidate_data: Any,
    allow_large_drop: bool,
) -> None:
    if allow_large_drop or filename == "links.json":
        return
    before_count = item_count(filename, before_data)
    candidate_count = item_count(filename, candidate_data)
    if before_count < 4:
        return

    minimum = max(1, before_count // 2)
    if candidate_count < minimum:
        raise ValueError(
            f"{filename}: auffälliger Datenrückgang von {before_count} auf "
            f"{candidate_count}. Falls das beabsichtigt ist, Workflow mit "
            f"allow_large_data_drop starten."
        )


def main() -> int:
    args = parse_args()
    if not args.before.is_dir():
        raise FileNotFoundError(f"Before-Verzeichnis fehlt: {args.before}")
    if not args.candidate.is_dir():
        raise FileNotFoundError(f"Candidate-Verzeichnis fehlt: {args.candidate}")

    before_names = managed_names(args.before)
    candidate_names = managed_names(args.candidate)
    if not before_names:
        raise ValueError("Im bisherigen Datenstand wurden keine Scraper-Dateien gefunden.")

    missing = sorted(before_names - candidate_names)
    if missing:
        raise ValueError(
            "Im Kandidaten fehlen Scraper-Dateien: " + ", ".join(missing)
        )

    checked = 0
    for filename in sorted(candidate_names):
        candidate_path = args.candidate / filename
        candidate_data = load_json(candidate_path)
        validate_schema(filename, candidate_data)

        before_path = args.before / filename
        if before_path.is_file():
            before_data = load_json(before_path)
            validate_drop(
                filename,
                before_data,
                candidate_data,
                args.allow_large_drop,
            )
        checked += 1

    print(f"Scraper-Daten erfolgreich validiert: {checked} Dateien.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
