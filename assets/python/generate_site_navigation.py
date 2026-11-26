#!/usr/bin/env python3
"""Custom pages and CMS-managed navigation/footer, built only into Pages output."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from generate_site import ROOT, load, text, seq, web
from generate_site_extra import page_sections, pdf

CUSTOM = ROOT / "content/custom-pages"
BASE = "https://www.ttf-laudenbach.de"
PREFIX = "/pages/individuell/"
FIXED = json.loads(r'''{"home":["Startseite","/index.html"],"club":["Unser Verein","/pages/unserVerein.html"],"training":["Aktiver Spielbetrieb","/pages/aktiverSpielbetrieb.html"],"membership":["Vereinsmitgliedschaft","/pages/vereinsmitgliedschaft.html"],"documents":["Dokumente","/pages/dokumente.html"],"gallery":["Historische Fotos","/pages/dokumente/historischeFotos.html"],"newsletter":["Newsletter","/pages/dokumente/newsletter.html"],"statutes":["Satzung","@statutes"],"join":["Mitgliedschaft","@join"],"sponsors":["Sponsoren","/pages/sponsoren.html"],"links":["Links","/pages/links.html"],"news":["Neuigkeiten","/pages/neuigkeiten.html"],"contact":["Kontakt","/pages/footer/kontakt.html"],"imprint":["Impressum","/pages/footer/impressum.html"],"privacy":["Datenschutz","/pages/footer/datenschutz.html"],"ranking":["Ewige Rangliste","/pages/aktiverSpielbetrieb/ewigeRangliste.html"],"herren1":["1. Herrenmannschaft","/pages/aktiverSpielbetrieb/herren1.html"],"herren2":["2. Herrenmannschaft","/pages/aktiverSpielbetrieb/herren2.html"],"herren3":["3. Herrenmannschaft","/pages/aktiverSpielbetrieb/herren3.html"],"herren4":["4. Herrenmannschaft","/pages/aktiverSpielbetrieb/herren4.html"],"herren5":["5. Herrenmannschaft","/pages/aktiverSpielbetrieb/herren5.html"],"jugend1":["1. Jugendmannschaft","/pages/aktiverSpielbetrieb/jugend1.html"],"jugend2":["2. Jugendmannschaft","/pages/aktiverSpielbetrieb/jugend2.html"]}''')
LEGAL = ("contact", "imprint", "privacy")
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def render_custom_pages(output, source=CUSTOM):
    directory = output / PREFIX.lstrip("/")
    directory.mkdir(parents=True, exist_ok=True)
    template = (ROOT / "templates/custom-page.html").read_text(encoding="utf-8")
    pages = {}
    for path in sorted(source.glob("*.json")):
        slug = path.stem
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 120:
            raise ValueError(f"Ungültiger Seitenname: {path.name}")
        data = json.loads(path.read_text(encoding="utf-8"))
        title = text(data["title"])
        if data.get("published") is not True:
            continue
        url = PREFIX + slug + ".html"
        description = text(data.get("description") or data["title"])
        width = data.get("width") or "full"
        if width not in ("full", "narrow"):
            raise ValueError(f"{path.name}: ungültige Breite")
        body = page_sections(data.get("sections"), path)
        tokens = {"TITLE": title, "DESCRIPTION": description, "CANONICAL": BASE + url,
                  "WIDTH": " cms-narrow" if width == "narrow" else "", "BODY": body}
        html = re.sub(r"@@([A-Z]+)@@", lambda m: tokens[m.group(1)], template)
        dest = directory / (slug + ".html")
        if dest.exists():
            raise ValueError(f"Kollision mit vorhandener Seite: {dest.name}")
        dest.write_text(html, encoding="utf-8")
        pages["content/custom-pages/" + path.name] = {"title": data["title"], "url": url,
            "auto_menu": data.get("auto_menu") is True, "nav_label": data.get("nav_label") or data["title"]}
    return pages


def resolve(row, custom, documents):
    target = row.get("target")
    if target in FIXED:
        default, href = FIXED[target]
        external = href.startswith("@")
        if external:
            href = pdf(documents[href[1:]])
    elif target == "custom":
        reference = row.get("custom_page")
        key = reference.lstrip("/") if isinstance(reference, str) else ""
        entry = custom.get(key)
        if not entry:
            print(f"CMS-Hinweis: Unterseite nicht veröffentlicht oder gelöscht: {reference!r}")
            return None
        default, href, external = entry["nav_label"], entry["url"], False
    elif target == "external":
        default, href, external = row.get("url"), web(row.get("url")), True
    else:
        raise ValueError(f"Unbekanntes Navigationsziel: {target!r}")
    label = text(row.get("label") or default)
    return label, href, external


def anchor(item):
    label, href, external = item
    attrs = ' rel="noopener noreferrer" target="_blank"' if external else ""
    return f'<a href="{href}"{attrs}>{label}</a>'


def render_menu(rows, custom, documents):
    parts, linked = [], set()
    for row in seq(rows):
        item = resolve(row, custom, documents)
        children = []
        for child in seq(row.get("children")):
            value = resolve(child, custom, documents)
            if value:
                linked.add(value[1])
                children.append(value)
        if not item:
            # Preserve valid children even if their custom parent was deleted.
            parts.extend("<li>" + anchor(x) + "</li>" for x in children)
            continue
        linked.add(item[1])
        if children:
            submenu = "".join("<li>" + anchor(x) + "</li>" for x in children)
            parts.append(f'<li class="dropdown">{anchor(item)}<ul class="submenu" id="submenu-{len(parts)+1}">{submenu}</ul></li>')
        else:
            parts.append("<li>" + anchor(item) + "</li>")
    for entry in custom.values():
        if entry["auto_menu"] and entry["url"] not in linked:
            parts.append("<li>" + anchor((text(entry["nav_label"]), entry["url"], False)) + "</li>")
    if not parts:
        parts.append("<li>" + anchor(resolve({"target": "home"}, custom, documents)) + "</li>")
    return '<ul class="menu">' + "\n".join(parts) + "</ul>"


def render_footer(data, custom, documents, sponsors):
    rows = seq(data.get("footer"))
    links = [value for row in rows if (value := resolve(row, custom, documents))]
    existing = {row.get("target") for row in rows}
    for target in LEGAL:
        if target not in existing:
            links.append(resolve({"target": target}, custom, documents))
    copyright_name = text(data.get("copyright") or "TTF Laudenbach")
    sponsor_items = seq(sponsors.get("items")) if data.get("show_sponsors", True) is not False else []
    boxes = [f'<div class="footer-sponsor">{anchor((text(r["name"]), web(r["url"]), True))}</div>' for r in sponsor_items]
    split = len(boxes)//2
    center = f'<div class="footer-content"><p>© <span data-current-year>2026</span> {copyright_name}</p><div class="footer-links">{"".join(anchor(x) for x in links)}</div></div>'
    return f'<footer class="footer" style="--footer-columns: {min(len(boxes)+1,5)}">{"".join(boxes[:split])}{center}{"".join(boxes[split:])}</footer>\n'


def sync_sitemap(path, pages):
    ET.register_namespace("", NS)
    tree = ET.parse(path)
    root = tree.getroot()
    tag = lambda name: f"{{{NS}}}{name}"
    for url in list(root):
        loc = url.find(tag("loc"))
        if loc is not None and (loc.text or "").startswith(BASE + PREFIX):
            root.remove(url)
    for entry in pages.values():
        url = ET.SubElement(root, tag("url"))
        ET.SubElement(url, tag("loc")).text = BASE + entry["url"]
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def build(output):
    custom = render_custom_pages(output)
    data, documents, sponsors = load("navigation"), load("documents"), load("sponsors")
    path = output / "components/header.html"
    page = path.read_text(encoding="utf-8")
    menu = render_menu(data.get("menu"), custom, documents)
    # The source header has exactly one nav; preserve logo, welcome text and accessibility.
    page, n = re.subn(r'(<nav aria-label="Hauptnavigation">)[\s\S]*?(</nav>)',
                       lambda m: m.group(1) + "\n" + menu + "\n" + m.group(2), page)
    if n != 1:
        raise ValueError("Header: Hauptnavigation fehlt")
    path.write_text(page, encoding="utf-8")
    (output / "components/footer.html").write_text(render_footer(data, custom, documents, sponsors), encoding="utf-8")
    sync_sitemap(output / "sitemap.xml", custom)
    print(f"CMS: {len(custom)} eigene Unterseiten, Navigation, Footer und Sitemap erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
