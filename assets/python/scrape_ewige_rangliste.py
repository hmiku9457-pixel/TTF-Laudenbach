#!/usr/bin/env python3
"""Ewige Rangliste – saisonale Erwachsenen-Spielberichte aus der bestehenden myTT-Konfiguration.

Erfasst ausschließlich nachweisbare Aufstellungen. Niemals Teilnehmer aus der
Mannschaftsmeldung oder aus einem bloßen Ergebnis ableiten.
Bei Auslesefehlern bleiben frühere Begegnungsdaten erhalten (Fehlermodus B).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright
from config import SAISON, SPIELPLAENE
from scraper import get_rows, load_page, safe_text
from ewige_rangliste import CONTENT, DELTA_DIR, load_active, load_json, write_json, build

DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})")
RESULT_RE = re.compile(r"\b\d{1,2}\s*:\s*\d{1,2}\b")
REPORT_RE = re.compile(r"(clubMeetingReport|meeting=|/spielbericht|/spielberichte/)", re.I)
CLUB = "ttf laudenbach"


def parse_game_date(text):
    match = DATE_RE.search(text or "")
    if not match:
        return None
    day, month, year = map(int, match.groups())
    if year < 100:
        year += 2000
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def meeting_id(url):
    qs = parse_qs(urlparse(url).query)
    for k in ("meeting", "meetingId", "gameId", "matchId"):
        if qs.get(k):
            return str(qs[k][0])
    for pattern in (r"/begegnung/(\d+)", r"/spielbericht/(\d+)", r"/spiel/(\d+)"):
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # Deterministischer Fallback, falls ein Anbieter keine ID als Parameter ausgibt.
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def find_scheduled_games(page):
    games = []
    for row in get_rows(page):
        cols = row.query_selector_all("td")
        if len(cols) < 6:
            continue
        day = parse_game_date(safe_text(cols, 0))
        if not day:
            continue
        names = [safe_text(cols, i) for i in range(len(cols))]
        # Mannschaftslisten (6 Spalten) und Vereinsspielplan (7 Spalten).
        home, away = (names[3], names[4]) if len(cols) == 6 else (names[4], names[5])
        result = names[-1]
        links = []
        for anchor in row.query_selector_all("a[href]"):
            href = anchor.get_attribute("href") or ""
            if REPORT_RE.search(href) and not href.lower().endswith(".pdf"):
                url = anchor.evaluate("(a) => a.href")
                if url not in links:
                    links.append(url)
        games.append({"datum": day, "heim": home, "gast": away, "ergebnis": result, "links": links})
    return games


def read_club_players(page, home, away):
    """Sicherheitsorientiert: verwertbare Paarungszeilen müssen zwei Spieler-Seiten besitzen.

    Home/away wird ausschließlich aus der Position in Paarungszeilen ermittelt.
    Wenn eine Seite nicht nachweisbar ist, wird die Begegnung NICHT als vollständig
    verarbeitet. Ein expliziter Sonderfall sind Vereinsduelle: beide Seiten zählen.
    """
    sides = page.evaluate("""() => {
        const result = {home: [], away: [], lines: 0};
        const seen = [new Set(), new Set()];
        for (const tr of document.querySelectorAll('table tr')) {
            const cells = Array.from(tr.querySelectorAll(':scope > td'));
            const persons = cells.map(cell => Array.from(cell.querySelectorAll('a[href]'))
                .filter(a => /[?&]person=|playerPortrait|\\/spieler\\/|\\/person\\/|personId=/i.test(a.getAttribute('href') || ''))
                .map(a => {
                    const url = new URL(a.href, location.href);
                    return {
                      name: (a.textContent || '').trim(),
                      personId: url.searchParams.get('person') || url.searchParams.get('personId') || null
                    };
                }).filter(p => p.name && /[a-zäöüß]/i.test(p.name)));
            const nonempty = persons.map((arr, i) => ({arr, i})).filter(x => x.arr.length);
            if (nonempty.length !== 2) continue;
            result.lines++;
            for (let side = 0; side < 2; side++) {
                for (const p of nonempty[side].arr) {
                    const k = p.personId || p.name.toLocaleLowerCase('de');
                    if (seen[side].has(k)) continue;
                    seen[side].add(k);
                    result[side === 0 ? 'home' : 'away'].push(p);
                }
            }
        }
        return result;
    }""")
    if not sides or not sides["lines"]:
        raise ValueError("Keine eindeutigen Heim-/Gast-Spielerpaare im Spielbericht.")
    include_home = CLUB in home.casefold()
    include_away = CLUB in away.casefold()
    if not include_home and not include_away:
        raise ValueError("Kein TTF-Team in der Begegnung.")
    selected = []
    for group in (["home"] if include_home else []) + (["away"] if include_away else []):
        if not sides[group]:
            raise ValueError(f"TTF-Aufstellung für {group} konnte nicht ausgelesen werden.")
        selected.extend(sides[group])
    players = {}
    for p in selected:
        name = " ".join(p["name"].split())
        if "," in name:
            surname, firstname = name.split(",", 1)
            name = (firstname.strip() + " " + surname.strip()).strip()
        pid = p.get("personId")
        token = pid or name.casefold()
        if token and token not in players:
            players[token] = {"name": name, "personId": pid}
    # Auch Vierermannschaften sind erlaubt, aber extrem kleine oder große
    # Ergebnisse sollen keinesfalls still als vollständige Begegnung gelten.
    if not (3 <= len(players) <= 12):
        raise ValueError(f"Auffällige TTF-Spielerzahl: {len(players)}.")
    return list(players.values())


def scrape():
    active, _ = load_active()
    cutoff = active["stichtag"]
    season = SAISON.replace("--", "/")  # 26/27 -> nachfolgend 2026/27
    start = 2000 + int(SAISON[:2])
    season_label = f"{start}/{str(start + 1)[-2:]}"
    season_file = DELTA_DIR / f"{start}-{str(start+1)[-2:]}.json"
    data = load_json(season_file) if season_file.exists() else {
        "saison": season_label, "begegnungen": [], "fehler": [],
        "zuletztGeprueft": None, "vollstaendigBis": None
    }
    events = {str(e["id"]): e for e in data.get("begegnungen", []) if e["datum"] > cutoff}
    errors = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    plans = [p for p in SPIELPLAENE if p.get("type") == "mannschaft" and "Herren" in p["name"]]
    if len(plans) != 5:
        raise ValueError(f"Erwartete fünf Erwachsenenmannschaften, gefunden: {len(plans)}")
    processed = set()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        try:
            for plan in plans:
                name = plan["name"]
                if not load_page(page, plan["url"], name):
                    errors.append({"typ": "spielplan", "mannschaft": name, "meldung": "Spielplan nicht erreichbar."})
                    continue
                games = find_scheduled_games(page)
                if not games:
                    errors.append({"typ": "spielplan", "mannschaft": name, "meldung": "Kein Spielplan gefunden."})
                    continue
                for game in games:
                    day = game["datum"]
                    if day <= cutoff or day > today:
                        continue
                    if not (CLUB in game["heim"].casefold() or CLUB in game["gast"].casefold()):
                        continue
                    has_result = bool(RESULT_RE.search(game["ergebnis"] or ""))
                    if not game["links"]:
                        if has_result:
                            errors.append({"typ": "bericht", "mannschaft": name, "datum": day,
                                           "meldung": "Ergebnis vorhanden, aber kein HTML-Spielbericht verlinkt."})
                        continue
                    report = game["links"][0]
                    gid = meeting_id(report)
                    if gid in processed:
                        continue
                    processed.add(gid)
                    if re.search(r"kampflos|nicht angetreten", game["ergebnis"], re.I):
                        errors.append({"typ": "sonderfall", "datum": day, "spiel": gid, "meldung": "Kampflos: manuelle Prüfung."})
                        continue
                    try:
                        response = page.goto(report, wait_until="domcontentloaded", timeout=45000)
                        if response and response.status >= 400:
                            raise ValueError(f"HTTP {response.status}")
                        page.wait_for_selector("table tr", timeout=15000)
                        players = read_club_players(page, game["heim"], game["gast"])
                        event = {"id": gid, "datum": day, "heim": game["heim"], "gast": game["gast"],
                                 "url": report, "spieler": players}
                        events[gid] = event
                        print(f"OK {day} {gid}: {len(players)} TTF-Spieler")
                    except Exception as exc:
                        errors.append({"typ": "bericht", "mannschaft": name, "datum": day,
                                       "spiel": gid, "meldung": str(exc)[:180]})
                        print(f"WARNUNG {day} {gid}: {exc}")
                    finally:
                        # Die Mannschaftsseite wieder laden: Navigieren zum Bericht
                        # verändert sonst die DOM-Grundlage für den nächsten Spielplan.
                        pass
                # Nächster Plan lädt eine frische Mannschaftsseite.
        finally:
            browser.close()
    # Fehler vergangener Läufe nur dann entfernen, wenn ihre zugehörige
    # Begegnung inzwischen vollständig erfasst wurde. Fehlgeschlagene
    # Mannschaftsseiten dürfen zuvor bestehende Warnungen nicht verdecken.
    current_keys = {(x.get("typ"), x.get("spiel"), x.get("mannschaft"), x.get("datum")) for x in errors}
    for previous in data.get("fehler", []):
        if previous.get("datum") and previous["datum"] <= cutoff:
            continue
        if previous.get("spiel") and str(previous["spiel"]) in processed:
            continue
        token = (previous.get("typ"), previous.get("spiel"), previous.get("mannschaft"), previous.get("datum"))
        if token not in current_keys:
            errors.append(previous)
    data["begegnungen"] = sorted(events.values(), key=lambda e: (e["datum"], str(e["id"])))
    data["fehler"] = errors
    data["zuletztGeprueft"] = now
    if not errors:
        data["vollstaendigBis"] = max(data.get("vollstaendigBis") or cutoff, yesterday)
    elif data.get("vollstaendigBis") and any(
        err.get("datum") and err["datum"] <= data["vollstaendigBis"] for err in errors
    ):
        candidates = [date.fromisoformat(e["datum"]) - timedelta(days=1) for e in errors if e.get("datum")]
        data["vollstaendigBis"] = max(cutoff, min(candidates).isoformat()) if candidates else cutoff
    write_json(season_file, data)
    result = build()
    print(f"Delta {season_label}: {len(data['begegnungen'])} Begegnungen; {len(errors)} Fehler.")
    return result


if __name__ == "__main__":
    try:
        scrape()
    except Exception as exc:
        print(f"FEHLER Saison-Delta: {exc}", file=sys.stderr)
        sys.exit(1)
