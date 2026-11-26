#!/usr/bin/env python3
"""Erzeugt Mannschaftsinformationen und ergänzt redaktionelle Fotoalben."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from generate_site import ROOT, load, text, seq, local, render_page
from generate_gallery import build_gallery_data

TEAMS = ("herren1", "herren2", "herren3", "herren4", "herren5", "jugend1", "jugend2")


def image(value, prefix):
    return local(value, prefix, {".jpg", ".jpeg", ".png", ".webp", ".gif"})


def render_team_info(team):
    # Pages CMS may remove optional, entirely empty objects on save.
    if team is None:
        team = {}
    if not isinstance(team, dict):
        raise ValueError("Mannschaftsinformationen müssen ein Objekt sein")
    info = f'<br/><p>Mannschaftsführer: {text(team["captain"])}</p>' if team.get("captain") else ""
    if team.get("photo"):
        info += f'<div class="news-rich-image"><img src="{image(team["photo"], "/assets/images/site/")}" alt="{text(team.get("photo_alt"))}" loading="lazy"/></div>'
    return info


def build(output):
    teams = load("teams")
    for key in TEAMS:
        info = render_team_info(teams.get(key))
        if render_page(output, f"pages/aktiverSpielbetrieb/{key}.html", {"team_info": info}) != {"team_info"}:
            raise ValueError(f"Mannschaft {key}: Platzhalter fehlt")
    gallery = build_gallery_data()
    (output / "assets/data/gallerie.json").write_text(json.dumps(gallery, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("CMS: Mannschaften und Galerien erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
