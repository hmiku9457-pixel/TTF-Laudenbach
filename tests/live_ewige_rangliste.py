"""Einzelner Online-Smoke-Test für den Match-Link und die TTF-Aufstellung.

Nur für PR-/Testzwecke; keine Daten werden in das Repository geschrieben.
Erwarteter Fall: TTF Laudenbach – TSV Schrozberg am 15.11.2026.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/python"))

from playwright.sync_api import sync_playwright
from config import SPIELPLAENE
from scraper import load_page
from scrape_ewige_rangliste import find_scheduled_games, read_club_players


def main():
    plan = next(p for p in SPIELPLAENE if p.get("name") == "Spiele Herren 1")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            if not load_page(page, plan["url"], "Live-Smoke-Test"):
                raise RuntimeError("myTischtennis-Mannschaftsseite nicht erreichbar.")
            games = find_scheduled_games(page)
            game = next((g for g in games if g["datum"] == "2026-11-15"
                         and "schrozberg" in (g["heim"] + g["gast"]).casefold()), None)
            if not game:
                raise RuntimeError(f"Begegnung 15.11. nicht gefunden; {len(games)} andere Spielplanzeilen.")
            if not game["links"]:
                raise RuntimeError("Für die abgeschlossene Begegnung kein Spielbericht-Link gefunden.")
            url = game["links"][0]
            response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if response and response.status >= 400:
                raise RuntimeError(f"Spielbericht antwortet mit HTTP {response.status}")
            page.wait_for_selector("table tr", timeout=15000)
            players = read_club_players(page, game["heim"], game["gast"])
            names = {p["name"] for p in players}
            required = {"Peter Pflüger", "Thomas Ruske", "Gerhard Wolfert"}
            missing = required - names
            if missing:
                raise RuntimeError(f"Bekannte eingesetzte Spieler fehlen: {sorted(missing)}; erkannt: {sorted(names)}")
            if len(players) != 6:
                raise RuntimeError(f"Erwartete 6 Spieler, gefunden {len(players)}: {sorted(names)}")
            print(json.dumps({"spielbericht": url, "datum": game["datum"], "spieler": players},
                             ensure_ascii=False, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
