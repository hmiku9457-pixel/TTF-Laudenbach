#!/usr/bin/env python3
"""Erzeugt statische CMS-Seiten ausschließlich im Website-Artefakt."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, quote, unquote
from generate_news import render_markdown

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "content/site"
DAYS = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")


def load(name):
    value = json.loads((SOURCE / f"{name}.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name}: Objekt erwartet")
    return value


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Ungültiges Textfeld: {value!r}")
    return escape(value.strip(), quote=True)


def seq(value):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Liste erwartet")
    return value


def web(value):
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError("Ungültige Webadresse")
    p = urlsplit(value)
    if p.scheme not in ("https", "http") or not p.hostname or p.username or p.password or "\\" in value:
        raise ValueError(f"Ungültige Webadresse: {value}")
    return escape(value, quote=True)


def local(value, prefix, suffixes):
    if not isinstance(value, str):
        raise ValueError("Dateipfad fehlt")
    value = unquote(value)
    if not value.startswith(prefix) or "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError(f"Ungültiger Dateipfad: {value}")
    p = ROOT / value.lstrip("/")
    base = ROOT / prefix.lstrip("/")
    if not p.resolve().is_relative_to(base.resolve()) or p.suffix.lower() not in suffixes or not p.is_file():
        raise ValueError(f"Datei fehlt oder falscher Dateityp: {value}")
    return quote(value, safe="/-._~")


def rich(value, name):
    if not isinstance(value, str):
        raise ValueError(f"{name}: Text erwartet")
    return render_markdown(value, SOURCE / f"{name}.json")


def table(title, rows, headers=(), cls="", row_header=False):
    head = ""
    if headers:
        head = "<thead><tr>" + "".join(f'<th scope="col">{text(v)}</th>' for v in headers) + "</tr></thead>"
    body = []
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            tag = "th" if row_header and i == 0 else "td"
            scope = ' scope="row"' if tag == "th" else ""
            cells.append(f"<{tag}{scope}>{value}</{tag}>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    attr = f' class="{cls}"' if cls else ""
    return f'<table{attr}><caption class="visually-hidden">{text(title)}</caption>{head}<tbody>{"".join(body)}</tbody></table>'


def button(name, href):
    return f'<a class="button button--card" href="{href}" rel="noopener noreferrer" target="_blank">{text(name)}</a>'


def render_training(data):
    halls = {k: data["hall" + k] for k in ("1", "2")}
    rows = []
    prior_day = prior_hall = None
    for item in seq(data.get("times")):
        day, group, time, hall = (item[k] for k in ("day", "group", "time", "hall"))
        if day not in DAYS or group not in ("Jugend", "Erwachsene", "Alle") or hall not in halls:
            raise ValueError("Training: ungültige Auswahl")
        if not isinstance(time, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", time):
            raise ValueError("Training: Uhrzeit muss HH:MM sein")
        rows.append([text(day) if day != prior_day else "", text(group), f"Ab {time} Uhr", text(halls[hall]["name"]) if day != prior_day or hall != prior_hall else ""])
        prior_day, prior_hall = day, hall
    out = "<h2>Tischtennis Training</h2><br/>" + rich(data["intro"], "training")
    out += '<br/><h3 class="underline">Trainingszeiten:</h3>' + table("Trainingszeiten:", rows, ("Tag", "Für", "Uhrzeit", "Ort"))
    if data.get("notice"):
        out += f'<p class="u-text-center"><span class="underline">{text(data["notice"])}</span></p>'
    return out


def render_hall(hall, nr):
    out = f"<h2>Spiellokal {nr}</h2>" + "".join(f"<p>{text(hall[k])}</p>" for k in ("name", "street", "city"))
    out += "".join(f"<p>{text(hall[k])}</p>" for k in ("changing", "showers") if hall.get(k))
    if hall.get("map_url"):
        url = hall["map_url"]
        p = urlsplit(url)
        if p.scheme != "https" or p.netloc != "www.google.com" or p.path != "/maps/embed":
            raise ValueError("Spiellokal: nur https://www.google.com/maps/embed erlaubt")
        out += f'<div class="map-container"><div class="iframe-consent" data-src="{web(url)}"><p>Um die Google Maps Karte zu sehen, bitte zustimmen.</p><button class="button button--card" data-iframe-consent-load="">Karte laden</button></div></div>'
    return out


def link_groups(links, sponsors):
    groups = []
    for key, items in (("tt-links", links.get("tt")), ("sport_allgemein", links.get("sports")), ("dies_und_das", links.get("other")), ("sponsoren", sponsors.get("items"))):
        result = []
        for i, item in enumerate(seq(items)):
            text(item["name"])
            web(item["url"])
            result.append({"id": f"{key}-{i+1}", "name": item["name"], "url": item["url"]})
        groups.append({"gruppe": key, "links": result})
    return groups


def render_page(output, target, values):
    page = (ROOT / target).read_text(encoding="utf-8")
    used = set()
    def replace(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f"{target}: unbekannter CMS-Platzhalter {key}")
        used.add(key)
        return values[key]
    page = re.sub(r"<!-- CMS:([a-z0-9_]+) -->", replace, page)
    if "<!-- CMS:" in page:
        raise ValueError(f"Nicht ersetzter Platzhalter: {target}")
    (output / target).write_text(page, encoding="utf-8")
    return used


def build(output):
    training, sponsors, links = [load(n) for n in ("training", "sponsors", "links")]
    items = seq(sponsors.get("items"))
    values = {"training": render_training(training), "hall1": render_hall(training["hall1"], 1), "hall2": render_hall(training["hall2"], 2),
              "sponsors": "".join(button(r["name"], web(r["url"])) for r in items)}
    targets = ["index.html", "pages/aktiverSpielbetrieb.html", "pages/sponsoren.html"]
    seen = set()
    for target in targets:
        seen |= render_page(output, target, values)
    if set(values) - seen:
        raise ValueError(f"Nicht verwendete CMS-Bausteine: {set(values)-seen}")
    link_file = output / "assets/data/links.json"
    data = json.loads(link_file.read_text(encoding="utf-8"))
    data["links"] = link_groups(links, sponsors)
    link_file.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("CMS: Training, Sponsoren und Links erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
