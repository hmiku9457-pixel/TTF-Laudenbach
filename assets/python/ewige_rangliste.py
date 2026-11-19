#!/usr/bin/env python3
"""Ewige Rangliste: datierte Master, saisonbasierte Begegnungen und öffentliche Daten.

Aufruf:
  python assets/python/ewige_rangliste.py build
  python assets/python/ewige_rangliste.py import-master
Alle Veränderungen werden im GitHub-Workflow als EIN Commit veröffentlicht.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content" / "ewige-rangliste"
ACTIVE = CONTENT / "aktiver-master.json"
MASTER_DIR = CONTENT / "master"
DELTA_DIR = CONTENT / "delta"
IMPORT_DIR = CONTENT / "import"
OUTPUT = ROOT / "assets" / "data" / "ewigeRangliste.json"
ALIASES = {"peter pfüger": "Peter Pflüger", "steffen wolfert": "Steffen Wolfert (ehem. Fahrbach)"}


def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).replace("\u00a0", " ").split())


def key(value: str) -> str:
    return norm(value).casefold()


def iso_date(value: str) -> str:
    value = norm(value).strip("()")
    value = re.sub(r"^Stand\s+", "", value, flags=re.I)
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})", value)
    if m:
        d, month, year = map(int, m.groups())
        if year < 100:
            year += 2000
        return date(year, month, d).isoformat()
    return date.fromisoformat(value).isoformat()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def parse_master(path: Path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines:
        raise ValueError(f"Master ist leer: {path}")
    sep = ";" if lines[0].count(";") > lines[0].count(",") else ","
    rows = [r for r in csv.reader(lines, delimiter=sep) if any(c.strip() for c in r)]
    legacy = rows[0][:3] == ["Rang", "Name", "Spiele"]
    if legacy:
        if len(rows) < 3 or len(rows[1]) < 3:
            raise ValueError("Historische CSV benötigt eine Datumszeile.")
        cutoff = iso_date(rows[1][2])
        entries = [(r[1], r[2], r[3:5], i + 1) for i, r in enumerate(rows[2:], 2)]
    else:
        if len(rows[0]) < 2 or rows[0][0].strip().casefold() != "stand":
            raise ValueError("CSV-Kopf erwartet 'Stand;TT.MM.JJJJ'.")
        cutoff = iso_date(rows[0][1])
        if len(rows) < 2 or [s.strip().casefold() for s in rows[1][:2]] != ["name", "spiele"]:
            raise ValueError("CSV benötigt die Spalten 'Name;Spiele'.")
        entries = [(r[0], r[1], [], i + 1) for i, r in enumerate(rows[2:], 2)]
    names = {}
    for raw_name, raw_count, history, line in entries:
        name = norm(raw_name)
        name = ALIASES.get(key(name), name)
        if not name or name[0] in "=+@":
            raise ValueError(f"Ungültiger Spielername in Zeile {line}.")
        k = key(name)
        if k in names:
            raise ValueError(f"Doppelter Spielername: {name}")
        if not re.fullmatch(r"\d+", str(raw_count).strip()):
            raise ValueError(f"Ungültige Einsatzzahl in Zeile {line}: {raw_count}")
        count = int(raw_count)
        if history:
            if len(history) < 2 or not all(re.fullmatch(r"\d+", x.strip()) for x in history[:2]):
                raise ValueError(f"Ungültige Vergleichsspalten in Zeile {line}.")
            if count - int(history[0]) != int(history[1]):
                raise ValueError(f"Historische Differenz falsch in Zeile {line}.")
        names[k] = {"name": name, "spiele": count}
    if not names:
        raise ValueError("Master enthält keine Spieler.")
    if cutoff > date.today().isoformat():
        raise ValueError("Master-Stichtag liegt in der Zukunft.")
    return cutoff, names


def load_active():
    active = load_json(ACTIVE)
    filename = CONTENT / active["datei"]
    if not filename.resolve().is_relative_to(MASTER_DIR.resolve()):
        raise ValueError("Aktiver Master zeigt außerhalb des Masterarchivs.")
    cutoff, players = parse_master(filename)
    if cutoff != active["stichtag"]:
        raise ValueError("Masterdatum widerspricht aktiver-master.json.")
    return active, players


def read_deltas(cutoff):
    found = []
    all_events = []
    errors = []
    last_checks = []
    coverage = []
    seen = set()
    for file in sorted(DELTA_DIR.glob("*.json")):
        data = load_json(file)
        if not isinstance(data.get("begegnungen"), list):
            raise ValueError(f"{file.name}: Begegnungen fehlen.")
        for event in data["begegnungen"]:
            game_date = iso_date(event["datum"])
            if game_date <= cutoff:
                continue
            eid = str(event["id"])
            token = (data["saison"], eid)
            if token in seen:
                raise ValueError(f"Doppelte Begegnung: {token}")
            seen.add(token)
            if not isinstance(event.get("spieler"), list):
                raise ValueError(f"Spieler fehlen bei Begegnung {eid}.")
            all_events.append((data["saison"], event))
        for err in data.get("fehler", []):
            if not err.get("datum") or iso_date(err["datum"]) > cutoff:
                errors.append(err)
        if data.get("zuletztGeprueft"):
            last_checks.append(data["zuletztGeprueft"])
        if data.get("vollstaendigBis"):
            coverage.append(iso_date(data["vollstaendigBis"]))
        found.append(file.name)
    return all_events, errors, max(last_checks, default=None), max(coverage, default=None), found


def build():
    active, master = load_active()
    cutoff = active["stichtag"]
    events, errors, last_check, full_date, seasons = read_deltas(cutoff)
    totals = Counter({k: x["spiele"] for k, x in master.items()})
    master_counts = dict(totals)
    display = {k: x["name"] for k, x in master.items()}
    deltas = Counter()
    known_identity = {}
    name_identity = {}
    unknown = {}
    game_seen = set()
    for season, event in events:
        game_key = (season, str(event["id"]))
        game_seen.add(game_key)
        people = set()
        for player in event["spieler"]:
            if isinstance(player, str):
                player = {"name": player}
            name = norm(player.get("name", ""))
            if not name:
                continue
            k = key(ALIASES.get(key(name), name))
            identity = str(player.get("personId") or "")
            dedupe_id = identity if identity else k
            if dedupe_id in people or k in people:
                continue
            people.add(dedupe_id)
            people.add(k)
            if k not in master and not identity:
                unknown.setdefault(k, {"name": name, "datum": event["datum"], "spiel": event["id"]})
                continue
            if identity and identity in known_identity and known_identity[identity] != k:
                errors.append({"typ": "zuordnung", "datum": event["datum"], "spiel": event["id"],
                               "meldung": f"Personen-ID {identity} mit abweichenden Namen."})
                continue
            if identity and k in name_identity and name_identity[k] != identity:
                errors.append({"typ": "zuordnung", "datum": event["datum"], "spiel": event["id"],
                               "meldung": f"Gleicher Name {name} mit verschiedenen Personen-IDs."})
                continue
            if identity:
                known_identity[identity] = k
                name_identity[k] = identity
            if k not in display:
                display[k] = name
                master_counts[k] = 0
            totals[k] += 1
            deltas[k] += 1
    if unknown:
        errors += [{"typ": "spieler", **v} for v in unknown.values()]
    if full_date is None:
        full_date = cutoff
    full_date = max(full_date, cutoff)
    for e in errors:
        try:
            if e.get("datum"):
                candidate = (date.fromisoformat(iso_date(e["datum"])) - timedelta(days=1)).isoformat()
                full_date = min(full_date, candidate)
            else:
                full_date = cutoff
        except ValueError:
            full_date = cutoff
    full_date = max(cutoff, full_date)
    export_totals = Counter(master_counts)
    for _, event in events:
        if event["datum"] > full_date:
            continue
        seen_people = set()
        for player in event["spieler"]:
            if isinstance(player, str):
                player = {"name": player}
            k = key(ALIASES.get(key(player.get("name", "")), player.get("name", "")))
            pid = str(player.get("personId") or "")
            if (pid or k) in seen_people:
                continue
            seen_people.add(pid or k)
            if k in display and k not in unknown:
                export_totals[k] += 1
    sorted_players = sorted(totals, key=lambda k: (-totals[k], display[k].casefold()))
    output_rows = []
    last_count = None
    rank = 0
    for i, k in enumerate(sorted_players, start=1):
        if totals[k] != last_count:
            rank = i
        output_rows.append({
            "rang": rank,
            "name": display[k],
            "master": master_counts.get(k, 0),
            "delta": deltas[k],
            "spiele": totals[k],
            "exportSpiele": export_totals[k]
        })
        last_count = totals[k]
    final = {
        "schemaVersion": 1,
        "masterStichtag": cutoff,
        "exportStichtag": full_date,
        "zuletztGeprueft": last_check,
        "unvollstaendig": bool(errors) or last_check is None,
        "hinweise": errors[:50] if errors else ([] if last_check else [{"typ": "status", "meldung": "Automatischer Abgleich noch nicht erfolgt."}]),
        "anzahlFehler": len(errors),
        "anzahlBegegnungen": len(game_seen),
        "saisons": seasons,
        "spieler": output_rows
    }
    write_json(OUTPUT, final)
    print(f"Rangliste: {len(output_rows)} Spieler, {len(game_seen)} Begegnungen, {len(errors)} offene Hinweise; Exportstand {full_date}")
    return final


def import_master():
    files = sorted(IMPORT_DIR.glob("*.csv"))
    if len(files) != 1:
        raise ValueError("Genau eine neue CSV im Importordner erwartet.")
    source = files[0]
    if source.name.startswith("."):
        raise ValueError("Ungültiger Dateiname.")
    new_date, new_players = parse_master(source)
    old_active, old_players = load_active()
    old_date = old_active["stichtag"]
    if new_date < old_date:
        raise ValueError(f"Neuer Master {new_date} ist älter als aktiver {old_date}.")
    if new_date > old_date:
        current = load_json(OUTPUT) if OUTPUT.exists() else build()
        if current.get("unvollstaendig") or current.get("exportStichtag", old_date) < new_date:
            raise ValueError("Neuer Master kann wegen fehlender/ungeprüfter Begegnungen nicht sicher aktiviert werden.")
    missing = set(old_players) - set(new_players)
    if missing:
        raise ValueError("Spieler dürfen im Master nicht fehlen: " + ", ".join(old_players[k]["name"] for k in sorted(missing)[:15]))
    for k, old in old_players.items():
        if new_date > old_date and new_players[k]["spiele"] < old["spiele"]:
            print(f"HINWEIS: korrigierte Gesamtzahl bei {old['name']}: {old['spiele']} -> {new_players[k]['spiele']}")
    used = {p.name for p in MASTER_DIR.glob("master_*.csv")}
    version = 1
    while f"master_{new_date}_v{version}.csv" in used:
        version += 1
    dest = MASTER_DIR / f"master_{new_date}_v{version}.csv"
    # Erst alle Delta-Dateien vorbereiten, dann Dateien auf dem Arbeitsbranch gemeinsam committen.
    pending = []
    season_history = []
    for file in sorted(DELTA_DIR.glob("*.json")):
        data = load_json(file)
        keep = []
        moved = []
        for event in data.get("begegnungen", []):
            (moved if iso_date(event["datum"]) <= new_date else keep).append(event)
        if moved:
            archive_file = CONTENT / "saison-archiv" / file.name
            history = load_json(archive_file) if archive_file.exists() else {
                "saison": data["saison"], "begegnungen": []
            }
            if history["saison"] != data["saison"]:
                raise ValueError(f"Saisonarchiv passt nicht zum Delta: {file.name}")
            history_ids = {str(e["id"]) for e in history["begegnungen"]}
            for event in moved:
                if str(event["id"]) not in history_ids:
                    history["begegnungen"].append(event)
                    history_ids.add(str(event["id"]))
            season_history.append((archive_file, history))
        data["begegnungen"] = keep
        data["fehler"] = [e for e in data.get("fehler", []) if not e.get("datum") or iso_date(e["datum"]) > new_date]
        pending.append((file, data))
    shutil.copyfile(source, dest)
    for path, data in season_history:
        write_json(path, data)
    for path, data in pending:
        write_json(path, data)
    write_json(ACTIVE, {"datei": f"master/{dest.name}", "stichtag": new_date, "version": version})
    source.unlink()
    build()
    print(f"Neuer Master aktiviert: {dest.name} mit {len(new_players)} Spielern.")


if __name__ == "__main__":
    try:
        mode = sys.argv[1] if len(sys.argv) > 1 else "build"
        if mode == "build":
            build()
        elif mode == "import-master":
            import_master()
        else:
            raise ValueError(f"Unbekannter Modus: {mode}")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"FEHLER Ewige Rangliste: {exc}", file=sys.stderr)
        sys.exit(1)
