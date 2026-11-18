#!/usr/bin/env python3
"""Validierter Import recherchierter Ergebnisse in vorhandene Website-Daten.

Eingang: content/assistant-import/aktuell.json
Nur bereits bekannte Begegnungen werden ergänzt. Keine Schätzungen, keine
direkten Änderungen durch den recherchierenden Assistenten an Produktivdaten.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from ewige_rangliste import DELTA_DIR, build, load_active, write_json

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "assets" / "data"
INPUT = ROOT / "content" / "assistant-import" / "aktuell.json"
DELTA = DELTA_DIR / "2026-27.json"
STATUS = DATA / "assistantStatus.json"
GAMES = sorted(DATA.glob("spiele*.json")) + [DATA / "startseiteSpiele.json"]
TABLE_FIELDS = {
    "rang", "mannschaft", "partien", "siege", "unentschieden",
    "niederlagen", "spiele", "spieleDifferenz", "punkte",
}
RESULT = re.compile(r"^\d{1,2}:\d{1,2}$")
DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
HOSTS = {"ttbw.click-tt.de", "ttvwh.click-tt.de", "mytischtennis.de", "www.mytischtennis.de"}
CLUB = "ttf laudenbach"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(value):
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).casefold().split())


def game_date(value):
    value = str(value or "")
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        match = DATE.search(value)
        if not match:
            raise ValueError("Unbekanntes Datumsformat: " + value)
        day, month, year = map(int, match.groups())
        return date(year, month, day).isoformat()


def key(value):
    return game_date(value["datum"]), normalized(value["heim"]), normalized(value["gast"])


def valid_source(value):
    url = urlparse(str(value or ""))
    if url.scheme != "https" or (url.hostname or "").lower() not in HOSTS or not url.path or url.username or url.password:
        raise ValueError("Keine zulässige, konkrete Original-URL: " + str(value))
    return value


def require(value, field):
    if not str(value or "").strip():
        raise ValueError(f"Pflichtfeld fehlt: {field}")
    return str(value).strip()


def validate_matches(items, cutoff):
    if not isinstance(items, list) or len(items) > 150:
        raise ValueError("matches muss eine Liste mit höchstens 150 Einträgen sein.")
    matches = {}
    today = date.today().isoformat()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Begegnungen müssen Objekte sein.")
        for field in ("datum", "heim", "gast", "ergebnis", "sourceUrl"):
            require(item.get(field), field)
        match_date = game_date(item["datum"])
        if not (cutoff < match_date <= today):
            raise ValueError("Begegnung außerhalb des gültigen Zeitraums: " + match_date)
        if CLUB not in normalized(item["heim"]) and CLUB not in normalized(item["gast"]):
            raise ValueError("Keine TTF-Begegnung: " + str(item))
        if not RESULT.fullmatch(item["ergebnis"]):
            raise ValueError("Ungültiges Mannschaftsergebnis: " + item["ergebnis"])
        a, b = map(int, item["ergebnis"].split(":"))
        if a + b == 0 or a > 20 or b > 20:
            raise ValueError("Unplausibles Mannschaftsergebnis.")
        valid_source(item["sourceUrl"])
        k = key(item)
        if k in matches and matches[k]["ergebnis"] != item["ergebnis"]:
            raise ValueError("Widersprüchliche recherchierte Ergebnisse: " + str(k))
        if k in matches and bool(item.get("spieler")) and bool(matches[k].get("spieler")) and item["spieler"] != matches[k]["spieler"]:
            raise ValueError("Widersprüchliche Aufstellungen: " + str(k))
        if k not in matches or (item.get("spieler") and not matches[k].get("spieler")):
            matches[k] = item
    return matches


def validate_tables(items):
    if not isinstance(items, list) or len(items) > 7:
        raise ValueError("tables muss eine Liste mit höchstens 7 Einträgen sein.")
    results = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Tabellen-Eintrag muss ein Objekt sein.")
        filename = require(item.get("file"), "file")
        if not re.fullmatch(r"tabelle(?:Herren[1-5]|Jugend[12])\.json", filename):
            raise ValueError("Unbekannte Tabelle: " + filename)
        if filename in results:
            raise ValueError("Doppelte Tabelle: " + filename)
        valid_source(item.get("sourceUrl"))
        rows = item.get("rows")
        if not isinstance(rows, list) or not 4 <= len(rows) <= 30:
            raise ValueError("Nur vollständige Tabellen (4–30 Vereine) übernehmen.")
        ranks, teams = set(), set()
        for row in rows:
            if not isinstance(row, dict) or not TABLE_FIELDS.issubset(row):
                raise ValueError("Tabellenfelder fehlen: " + filename)
            if any(not isinstance(row[field], str) or not row[field].strip() for field in TABLE_FIELDS):
                raise ValueError("Ungültige Tabellenzelle: " + filename)
            rank = int(row["rang"]) if row["rang"].isdigit() else 0
            if rank < 1 or rank > len(rows) or rank in ranks:
                raise ValueError("Ungültige oder doppelte Tabellenposition.")
            ranks.add(rank)
            team = normalized(row["mannschaft"])
            if team in teams:
                raise ValueError("Doppelte Mannschaft in Tabelle.")
            teams.add(team)
            numbers = [row[field] for field in ("partien", "siege", "unentschieden", "niederlagen")]
            if any(not value.isdigit() for value in numbers):
                raise ValueError("Ungültige Tabellenspiele.")
            games, wins, draws, losses = map(int, numbers)
            if games != wins + draws + losses:
                raise ValueError("Tabellensumme ist inkonsistent.")
            if not RESULT.fullmatch(row["spiele"]) or not RESULT.fullmatch(row["punkte"]):
                raise ValueError("Ungültige Spiele- oder Punktezahlen.")
        if ranks != set(range(1, len(rows) + 1)):
            raise ValueError("Lückenhafte Tabellenpositionen.")
        results[filename] = rows
    return results


def validate_players(match):
    players = match.get("spieler")
    if players is None:
        return None
    # Keine Spielberichte oder Aufstellungen aus Mannschaftsmeldungen erfinden.
    report = valid_source(match.get("reportUrl"))
    meeting = require(match.get("meetingId"), "meetingId")
    if not re.fullmatch(r"\d{3,20}", meeting):
        raise ValueError("Es muss eine nachgewiesene numerische Begegnungs-ID vorliegen.")
    if not isinstance(players, list) or not 3 <= len(players) <= 12:
        raise ValueError("Die tatsächliche TTF-Aufstellung muss 3–12 Spieler umfassen.")
    people, seen = [], set()
    for player in players:
        if not isinstance(player, dict):
            raise ValueError("Spielerobjekt erwartet.")
        name = require(player.get("name"), "spieler.name")
        pid = player.get("personId")
        if pid is not None and not re.fullmatch(r"\d{1,25}", str(pid)):
            raise ValueError("Ungültige Spieler-ID.")
        token = str(pid) if pid is not None else normalized(name)
        if token in seen:
            raise ValueError("Doppelter Spieler in Begegnung: " + name)
        seen.add(token)
        people.append({"name": name, "personId": str(pid) if pid is not None else None})
    return {"id": meeting, "datum": game_date(match["datum"]),
            "heim": match["heim"], "gast": match["gast"],
            "url": report, "spieler": people}


def apply():
    if not INPUT.exists():
        raise ValueError("Assistenten-Importdatei existiert nicht.")
    feed = load(INPUT)
    if not isinstance(feed, dict) or feed.get("schemaVersion") != 1:
        raise ValueError("Unbekannte Assistenten-Importversion.")
    checked = datetime.fromisoformat(require(feed.get("checkedAt"), "checkedAt").replace("Z", "+00:00"))
    if checked.tzinfo is None or checked.astimezone(timezone.utc) > datetime.now(timezone.utc):
        raise ValueError("checkedAt muss ein überprüfbarer Zeitstempel mit Zeitzone sein.")
    cutoff = load_active()[0]["stichtag"]
    matches = validate_matches(feed.get("matches", []), cutoff)
    tables = validate_tables(feed.get("tables", []))
    if not matches and not tables:
        print("Keine gesicherten Änderungen geliefert.")
        return
    original_games = {p: load(p) for p in GAMES}
    changed = {}
    found = set()
    match_changes = 0
    for path, rows in original_games.items():
        altered = []
        for row in rows:
            entry = dict(row)
            k = key(row)
            if k in matches:
                found.add(k)
                candidate = matches[k]["ergebnis"]
                old = str(row.get("ergebnis") or "").strip()
                if old and old != candidate:
                    raise ValueError(f"Abweichendes vorhandenes Ergebnis in {path.name}: {k}: {old} / {candidate}")
                if old != candidate:
                    entry["ergebnis"] = candidate
                    entry["status"] = "gespielt"
                    match_changes += 1
            altered.append(entry)
        if altered != rows:
            changed[path] = altered
    missing = set(matches) - found
    if missing:
        raise ValueError("Begegnung nicht im bestehenden Spielplan gefunden: " + repr(sorted(missing)))
    table_changes = 0
    for filename, rows in tables.items():
        path = DATA / filename
        previous = load(path)
        if len(rows) < max(4, len(previous) // 2):
            raise ValueError("Auffälliger Tabellenrückgang: " + filename)
        prior = {normalized(row["mannschaft"]): int(row["partien"]) for row in previous}
        for row in rows:
            old = prior.get(normalized(row["mannschaft"]))
            if old is not None and int(row["partien"]) < old:
                raise ValueError("Tabelle enthält älteren Stand als bisher: " + filename)
        if rows != previous:
            changed[path] = rows
            table_changes += 1
    old_delta = load(DELTA)
    events = {str(e["id"]): e for e in old_delta.get("begegnungen", [])}
    added_reports = 0
    for k, match in matches.items():
        if match.get("spieler") is None:
            continue
        if not ("ttf laudenbach" in normalized(match["heim"]) or "ttf laudenbach" in normalized(match["gast"])):
            continue
        event = validate_players(match)
        eid = event["id"]
        if eid in events and events[eid] != event:
            raise ValueError("Vorhandener Bericht widerspricht der neuen Quelle: " + eid)
        if eid not in events:
            events[eid] = event
            added_reports += 1
    # Auch unbeantwortete alte Begegnungen als Lücken melden. Kein
    # Vollständigkeits-Stichtag wird ohne vollständigen Nachweis erhöht.
    errors, outstanding = [], set()
    for path, rows in original_games.items():
        if not re.fullmatch(r"spieleHerren[1-5]\.json", path.name):
            continue
        for row in rows:
            d = game_date(row["datum"])
            if not cutoff < d <= date.today().isoformat():
                continue
            k = key(row)
            if k in outstanding:
                continue
            outstanding.add(k)
            event_exists = any((e["datum"], normalized(e["heim"]), normalized(e["gast"])) == k for e in events.values())
            if not event_exists:
                errors.append({"typ": "bericht", "datum": d, "mannschaft": path.stem,
                               "meldung": "Bestätigte TTF-Aufstellung aus Spielbericht fehlt."
                               if row.get("ergebnis") or k in matches
                               else "Ergebnis oder TTF-Aufstellung noch nicht verifiziert."})
    new_delta = dict(old_delta)
    new_delta["begegnungen"] = sorted(events.values(), key=lambda e: (e["datum"], str(e["id"])))
    new_delta["fehler"] = errors
    new_delta["zuletztGeprueft"] = checked.astimezone(timezone.utc).isoformat(timespec="seconds")
    new_delta["vollstaendigBis"] = old_delta.get("vollstaendigBis")
    changed[DELTA] = new_delta
    changed[STATUS] = {
        "schemaVersion": 1,
        "lastImportedAt": new_delta["zuletztGeprueft"],
        "providedMatches": len(matches),
        "updatedGameRows": match_changes,
        "updatedTables": table_changes,
        "newVerifiedReports": added_reports,
        "unverifiedAdultMatches": len(errors),
        "sourceUrls": sorted({m["sourceUrl"] for m in matches.values()} |
                             {item["sourceUrl"] for item in feed.get("tables", [])}),
    }
    for path, rows in changed.items():
        write_json(path, rows)
    build()
    print(f"Assistenten-Import: {match_changes} Ergebniszeilen, {table_changes} Tabellen, "
          f"{added_reports} Spielberichte, {len(errors)} ungeprüfte Erwachsenenbegegnungen.")


if __name__ == "__main__":
    try:
        apply()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FEHLER Assistenten-Import: {exc}", file=sys.stderr)
        sys.exit(1)
