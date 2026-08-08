#!/usr/bin/env python3
"""Validiert neue Scraper-Daten gegen Schema und bisherigen Datenbestand."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Datei fehlt oder ist leer: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ungültiges JSON in {path}: {exc}") from exc


def require_records(data: Any, filename: str, fields: set[str]) -> None:
    if not isinstance(data, list):
        raise ValueError(f"{filename}: erwartet eine Liste, erhalten {type(data).__name__}")
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f"{filename}[{index}]: erwartet ein Objekt")
        missing = [field for field in fields if field not in record]
        if missing:
            raise ValueError(f"{filename}[{index}]: Pflichtfelder fehlen: {', '.join(missing)}")
        for field in fields:
            if record[field] is None:
                raise ValueError(f"{filename}[{index}].{field}: darf nicht null sein")


def validate_schema(filename: str, data: Any) -> None:
    lower = filename.lower()
    if lower == "links.json":
        if not isinstance(data, dict):
            raise ValueError("links.json: erwartet ein Objekt")
        required = {"spielplaene", "tabellen", "spielerlisten", "links"}
        missing = required.difference(data)
        if missing:
            raise ValueError("links.json: Pflichtbereiche fehlen: " + ", ".join(sorted(missing)))
        for key in required:
            if not isinstance(data[key], list):
                raise ValueError(f"links.json.{key}: erwartet eine Liste")
    elif lower.startswith("spiele"):
        require_records(data, filename, {"heim", "gast", "datum"})
    elif lower.startswith("tabelle"):
        require_records(data, filename, {"rang", "mannschaft", "punkte"})
    elif "spieler" in lower:
        require_records(data, filename, {"name"})


def compare_lists(before: Any, candidate: Any, path: str, allow_large_drop: bool, errors: list[str]) -> None:
    if isinstance(before, list) and isinstance(candidate, list):
        old_count = len(before)
        new_count = len(candidate)
        if old_count > 0 and new_count == 0:
            errors.append(f"{path}: bisher {old_count} Einträge, neu leer")
        elif not allow_large_drop and old_count >= 4:
            minimum = max(1, math.ceil(old_count * 0.5))
            if new_count < minimum:
                errors.append(f"{path}: ungewöhnlicher Rückgang von {old_count} auf {new_count} Einträge")
        for index, (old_item, new_item) in enumerate(zip(before, candidate)):
            compare_lists(old_item, new_item, f"{path}[{index}]", allow_large_drop, errors)
    elif isinstance(before, dict) and isinstance(candidate, dict):
        for key in before.keys() & candidate.keys():
            compare_lists(before[key], candidate[key], f"{path}.{key}", allow_large_drop, errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--allow-large-drop", action="store_true")
    args = parser.parse_args()

    before_files = {path.name: path for path in args.before.glob("*.json")}
    candidate_files = {path.name: path for path in args.candidate.glob("*.json")}
    errors: list[str] = []

    if not candidate_files:
        errors.append("Der Scraper hat keine JSON-Dateien erzeugt.")

    missing_files = sorted(set(before_files) - set(candidate_files))
    if missing_files:
        errors.append("Neue Ausgabe lässt bestehende Dateien vermissen: " + ", ".join(missing_files))

    for filename, candidate_path in sorted(candidate_files.items()):
        try:
            candidate = load_json(candidate_path)
            validate_schema(filename, candidate)
            if filename in before_files:
                before = load_json(before_files[filename])
                if type(before) is not type(candidate):
                    errors.append(f"{filename}: Wurzeltyp änderte sich von {type(before).__name__} zu {type(candidate).__name__}")
                compare_lists(before, candidate, filename, args.allow_large_drop, errors)
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        print("Scraper-Daten wurden abgelehnt:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print("Bei einem legitimen Saisonwechsel den Workflow manuell mit allow_large_data_drop starten.", file=sys.stderr)
        return 1

    print(f"Scraper-Daten erfolgreich geprüft: {len(candidate_files)} Dateien.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
