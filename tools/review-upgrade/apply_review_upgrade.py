#!/usr/bin/env python3
"""Wendet die Abschlussverbesserungen idempotent auf das Repository an."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "payload.zip"

ACTION_PINS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",  # v4.4.0
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",  # v7.0.0
    "actions/setup-node": "820762786026740c76f36085b0efc47a31fe5020",  # v7.0.0
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",  # v4.6.2
}

SPECIAL_HEADINGS = {
    "index.html": "Tischtennis-Freunde Laudenbach",
    "pages/aktiverSpielbetrieb.html": "Training und Spiellokale",
    "pages/links.html": "Links",
    "pages/footer/kontakt.html": "Kontakt",
}


def copy_templates() -> None:
    if not PAYLOAD.is_file():
        raise FileNotFoundError(f"Payload fehlt: {PAYLOAD}")
    with zipfile.ZipFile(PAYLOAD) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            relative = Path(member.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Unsicherer Payload-Pfad: {member.filename}")
            destination = ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
            print(f"Aktualisiert: {relative.as_posix()}")


def safe_http_url(value: object) -> str | None:
    """Akzeptiert ausschließlich vollständige HTTP(S)-URLs."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return candidate


def load_static_link_targets() -> tuple[dict[str, str], dict[str, str]]:
    """Erzeugt ID->URL- und ID->Beschriftung-Zuordnungen aus links.json."""
    path = ROOT / "assets/data/links.json"
    if not path.is_file():
        return {}, {}

    data = json.loads(path.read_text(encoding="utf-8"))
    targets: dict[str, str] = {}
    labels: dict[str, str] = {}

    for section in ("tabellen", "spielplaene"):
        entries = data.get(section, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_id = entry.get("id")
            url = safe_http_url(entry.get("url"))
            if isinstance(entry_id, str) and entry_id and url:
                targets[f"link-{entry_id}"] = url

    sponsor_ids = {"sponsor1", "sponsor2", "sponsor3", "sponsor4"}
    groups = data.get("links", [])
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                continue
            links = group.get("links", [])
            if not isinstance(links, list):
                continue
            for entry in links:
                if not isinstance(entry, dict):
                    continue
                entry_id = entry.get("id")
                if entry_id not in sponsor_ids:
                    continue
                url = safe_http_url(entry.get("url"))
                name = entry.get("name")
                if not url:
                    continue
                for suffix in ("", "-main", "-footer"):
                    element_id = f"link-{entry_id}{suffix}"
                    targets[element_id] = url
                    if isinstance(name, str) and name.strip():
                        labels[element_id] = name.strip()

    return targets, labels


def hydrate_static_links(
    soup: BeautifulSoup,
    targets: dict[str, str],
    labels: dict[str, str],
) -> bool:
    """Schreibt dynamische Linkziele als progressiven HTML-Fallback vor."""
    changed = False
    for element_id, url in targets.items():
        anchor = soup.find("a", id=element_id)
        if not anchor:
            continue
        if anchor.get("href") != url:
            anchor["href"] = url
            changed = True
        if anchor.has_attr("aria-disabled"):
            del anchor["aria-disabled"]
            changed = True
        classes = list(anchor.get("class", []))
        if "is-disabled" in classes:
            anchor["class"] = [name for name in classes if name != "is-disabled"]
            changed = True
        label = labels.get(element_id)
        if label and anchor.get_text(" ", strip=True) != label:
            anchor.clear()
            anchor.string = label
            changed = True
    return changed


def patch_html_documents(
    static_targets: dict[str, str],
    static_labels: dict[str, str],
) -> None:
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if "<html" not in text.lower():
            continue

        soup = BeautifulSoup(text, "html.parser")
        if not soup.html or not soup.body:
            continue

        relative = path.relative_to(ROOT).as_posix()
        body = soup.body

        # Produktions-CSS verwenden.
        for link in soup.find_all("link", rel=lambda value: value and "stylesheet" in value):
            href = link.get("href", "")
            if href.endswith("/assets/css/main.css") or href.endswith("/assets/css/style.css"):
                link["href"] = "/assets/css/site.bundle.css"

        ensure_static_structure(soup, relative)
        normalize_headings(soup, relative)
        improve_tables(soup, relative)
        convert_inline_iframe_handlers(soup)
        ensure_contact_status(soup)
        hydrate_static_links(soup, static_targets, static_labels)

        output = str(soup)
        if not output.lstrip().lower().startswith("<!doctype html>"):
            output = "<!DOCTYPE html>\n" + output
        path.write_text(output.rstrip() + "\n", encoding="utf-8")
        print(f"HTML überarbeitet: {relative}")


def direct_children_between(body: Tag, excluded: set[Tag]) -> list[Tag | NavigableString]:
    result: list[Tag | NavigableString] = []
    for child in list(body.children):
        if isinstance(child, NavigableString) and not child.strip():
            continue
        if isinstance(child, Tag) and child in excluded:
            continue
        if isinstance(child, Tag) and child.name == "script":
            continue
        result.append(child)
    return result


def ensure_static_structure(soup: BeautifulSoup, relative: str) -> None:
    body = soup.body
    header = body.find(id="header-container", recursive=False)
    footer = body.find(id="footer-container", recursive=False)
    main = body.find("main", recursive=False)
    skip = body.find("a", class_="skip-link", recursive=False)

    if not skip:
        skip = soup.new_tag("a", href="#main-content")
        skip["class"] = ["skip-link"]
        skip.string = "Direkt zum Inhalt"
        body.insert(0, skip)
    else:
        skip["href"] = "#main-content"

    if not main:
        main = soup.new_tag("main", id="main-content")
        main["tabindex"] = "-1"
        if header:
            header.insert_after(main)
        else:
            skip.insert_after(main)
    else:
        main["id"] = "main-content"
        main["tabindex"] = "-1"

    excluded = {skip, main}
    if header:
        excluded.add(header)
    if footer:
        excluded.add(footer)

    # Direkte Inhaltsknoten außerhalb des Main-Landmarks hineinverschieben.
    movable = direct_children_between(body, excluded)
    for child in movable:
        main.append(child.extract())

    # Der Footer soll nach dem Hauptinhalt stehen, Skripte dürfen danach folgen.
    if footer and footer.previous_sibling is not main:
        main.insert_after(footer.extract())


def derive_heading(soup: BeautifulSoup, relative: str) -> str:
    if relative in SPECIAL_HEADINGS:
        return SPECIAL_HEADINGS[relative]
    title = soup.title.get_text(" ", strip=True) if soup.title else "TTF Laudenbach"
    title = re.split(r"\s*[|–-]\s*TTF(?:\s+Laudenbach)?\s*$", title, flags=re.I)[0].strip()
    if title.lower() in {"ttf laudenbach", "tischtennis-freunde laudenbach"}:
        return "Tischtennis-Freunde Laudenbach"
    return title or "TTF Laudenbach"


def normalize_headings(soup: BeautifulSoup, relative: str) -> None:
    main = soup.find("main", id="main-content")
    if not main:
        return

    if relative == "pages/aktiverSpielbetrieb.html":
        for heading in main.find_all("h1"):
            if heading.get_text(" ", strip=True).lower().startswith("spiellokal"):
                heading.name = "h2"
    elif relative == "pages/links.html":
        for heading in main.find_all("h1"):
            heading.name = "h2"

    # Kontaktüberschrift sichtbar als Hauptüberschrift verwenden.
    if relative == "pages/footer/kontakt.html" and not main.find("h1"):
        contact_heading = main.find(["h2", "h3"], string=lambda value: value and value.strip().lower() == "kontakt")
        if contact_heading:
            contact_heading.name = "h1"

    h1s = main.find_all("h1")
    if not h1s:
        heading = soup.new_tag("h1")
        heading["class"] = ["visually-hidden", "page-heading"]
        heading.string = derive_heading(soup, relative)
        main.insert(0, heading)
        h1s = [heading]

    for duplicate in h1s[1:]:
        duplicate.name = "h2"


def nearest_heading_text(table: Tag, soup: BeautifulSoup, relative: str) -> str:
    previous = table.find_previous(["h1", "h2", "h3", "h4"])
    if previous:
        value = previous.get_text(" ", strip=True)
        if value:
            return value
    return derive_heading(soup, relative)


def replace_tag(soup: BeautifulSoup, old: Tag, name: str) -> Tag:
    new = soup.new_tag(name)
    for key, value in old.attrs.items():
        new[key] = value
    for child in list(old.contents):
        new.append(child.extract())
    old.replace_with(new)
    return new


def improve_tables(soup: BeautifulSoup, relative: str) -> None:
    for table in soup.find_all("table"):
        caption = table.find("caption")
        if not caption:
            caption = soup.new_tag("caption")
            caption["class"] = ["visually-hidden"]
            caption.string = nearest_heading_text(table, soup, relative)
            table.insert(0, caption)

        thead = table.find("thead")
        if thead:
            for cell in thead.find_all(["td", "th"]):
                if cell.name == "td":
                    cell = replace_tag(soup, cell, "th")
                cell["scope"] = "col"

        # Beitragstabelle erhält einen echten Tabellenkopf.
        if relative == "pages/vereinsmitgliedschaft.html" and not thead:
            first_row = table.find("tr")
            column_count = len(first_row.find_all(["td", "th"], recursive=False)) if first_row else 2
            headers = ["Mitgliedschaft", "Jahresbeitrag"]
            new_head = soup.new_tag("thead")
            row = soup.new_tag("tr")
            for index in range(column_count):
                th = soup.new_tag("th", scope="col")
                th.string = headers[index] if index < len(headers) else f"Spalte {index + 1}"
                row.append(th)
            new_head.append(row)
            caption.insert_after(new_head)

        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False) if tbody else []
        for row in rows:
            cells = row.find_all(["td", "th"], recursive=False)
            if 2 <= len(cells) <= 3 and cells[0].name == "td" and cells[0].get_text(" ", strip=True):
                first = replace_tag(soup, cells[0], "th")
                first["scope"] = "row"


def convert_inline_iframe_handlers(soup: BeautifulSoup) -> None:
    for element in soup.find_all(attrs={"onclick": True}):
        handler = element.get("onclick", "")
        if "loadIframe" in handler:
            del element["onclick"]
            element["data-iframe-consent-load"] = ""


def ensure_contact_status(soup: BeautifulSoup) -> None:
    form = soup.find("form", id="contactForm")
    if not form:
        return
    status = soup.find(id="contactFormStatus")
    if status:
        return
    status = soup.new_tag("p", id="contactFormStatus")
    status["class"] = ["form-status"]
    status["role"] = "status"
    status["aria-live"] = "polite"
    status["aria-atomic"] = "true"
    button = form.find(id="contactSubmitButton")
    if button:
        button.insert_after(status)
    else:
        form.append(status)


def patch_header_component() -> None:
    path = ROOT / "components/header.html"
    if not path.is_file():
        return
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for index, dropdown in enumerate(soup.select("li.dropdown"), start=1):
        link = dropdown.find("a", recursive=False)
        submenu = dropdown.find("ul", class_="submenu", recursive=False)
        if not link or not submenu:
            continue
        submenu_id = submenu.get("id") or f"submenu-{index}"
        submenu["id"] = submenu_id
        toggle = dropdown.find("button", class_="submenu-toggle", recursive=False)
        if not toggle:
            toggle = soup.new_tag("button", type="button")
            toggle["class"] = ["submenu-toggle"]
            toggle["aria-expanded"] = "false"
            toggle["aria-controls"] = submenu_id
            toggle["aria-label"] = f"Untermenü {link.get_text(' ', strip=True)} öffnen"
            icon = soup.new_tag("span")
            icon["aria-hidden"] = "true"
            icon.string = "▾"
            toggle.append(icon)
            link.insert_after(toggle)
    path.write_text(str(soup).strip() + "\n", encoding="utf-8")
    print("Header-Navigation überarbeitet.")


def patch_links_json() -> None:
    path = ROOT / "assets/data/links.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "url" and isinstance(item, str) and "jako" in item.lower() and item.startswith("http://"):
                    value[key] = "https://" + item[len("http://"):]
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Sponsor-Links geprüft.")


def patch_component_links(
    static_targets: dict[str, str],
    static_labels: dict[str, str],
) -> None:
    """Ergänzt Link-Fallbacks auch in geladenen Header-/Footer-Fragmenten."""
    components = ROOT / "components"
    if not components.is_dir():
        return
    for path in sorted(components.glob("*.html")):
        original = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(original, "html.parser")
        if hydrate_static_links(soup, static_targets, static_labels):
            path.write_text(str(soup).strip() + "\n", encoding="utf-8")
            print(f"Komponenten-Links ergänzt: {path.relative_to(ROOT)}")


def pin_actions() -> None:
    pattern = re.compile(r"(uses:\s*)(actions/(?:checkout|setup-python|setup-node|upload-artifact))@[^\s#]+")
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            action = match.group(2)
            return f"{match.group(1)}{action}@{ACTION_PINS[action]}"

        updated = pattern.sub(replace, text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"Action-Pins aktualisiert: {path.relative_to(ROOT)}")


def remove_legacy_files() -> None:
    for relative in ["assets/css/style.css", "assets/js/script.js"]:
        path = ROOT / relative
        if path.exists():
            path.unlink()
            print(f"Legacy-Datei entfernt: {relative}")


def main() -> int:
    copy_templates()
    # URLs zuerst normalisieren, damit die statischen HTML-Fallbacks HTTPS verwenden.
    patch_links_json()
    static_targets, static_labels = load_static_link_targets()
    patch_html_documents(static_targets, static_labels)
    patch_header_component()
    patch_component_links(static_targets, static_labels)
    pin_actions()
    remove_legacy_files()
    print("Abschlussverbesserungen wurden im Arbeitsstand angewendet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
