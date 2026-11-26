#!/usr/bin/env python3
"""Erzeugt Mannschaftsinformationen und ergänzt redaktionelle Fotoalben."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
from generate_site import ROOT, load, text, seq, local, render_page
from generate_gallery import build_gallery_data, slugify

TEAMS = ("herren1", "herren2", "herren3", "herren4", "herren5", "jugend1", "jugend2")


def image(value, prefix):
    return local(value, prefix, {".jpg", ".jpeg", ".png", ".webp", ".gif"})


def build(output):
    teams, albums = load("teams"), load("albums")
    for key in TEAMS:
        team = teams[key]
        info = f'<br/><p>Mannschaftsführer: {text(team["captain"])}</p>' if team.get("captain") else ""
        if team.get("photo"):
            info += f'<div class="news-rich-image"><img src="{image(team["photo"], "/assets/images/site/")}" alt="{text(team["photo_alt"])}" loading="lazy"/></div>'
        if render_page(output, f"pages/aktiverSpielbetrieb/{key}.html", {"team_info": info}) != {"team_info"}:
            raise ValueError(f"Mannschaft {key}: Platzhalter fehlt")
    gallery = build_gallery_data()
    ids = {r["id"] for r in gallery["galleries"]}
    for album in seq(albums.get("albums")):
        title = album["title"]
        text(title)
        id_ = "cms-" + slugify(title)
        if id_ == "cms-" or id_ in ids:
            raise ValueError("Galerie: eindeutige Albumtitel erforderlich")
        ids.add(id_)
        images = [{"src": image(r["src"], "/assets/images/gallery/"), "alt": r["alt"]} for r in seq(album.get("images"))]
        for img in images:
            text(img["alt"])
        event_date = album.get("date") or ""
        if event_date:
            date.fromisoformat(event_date)
        description = album.get("description") or ""
        if not isinstance(description, str):
            raise ValueError("Galerie: Beschreibung muss Text sein")
        if images:
            gallery["galleries"].append({"id": id_, "title": title, "images": images, "date": event_date, "description": description})
    (output / "assets/data/gallerie.json").write_text(json.dumps(gallery, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("CMS: Mannschaften und Galerien erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
