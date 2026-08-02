#!/usr/bin/env python3
"""Abhängigkeitsfreie Qualitätsprüfung für die statische Vereinswebseite."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
IGNORE_DIRS = {".git", "__pycache__", "node_modules"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.is_html_document = False
        self.title_count = 0
        self.in_title = False
        self.title_text: list[str] = []
        self.ids: list[str] = []
        self.references: list[tuple[str, str, int]] = []
        self.images_without_alt: list[int] = []
        self.meta_description_count = 0
        self.canonical_count = 0
        self.stylesheets: list[str] = []
        self.scripts: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value for name, value in attrs}
        line = self.getpos()[0]

        if tag == "html":
            self.is_html_document = True

        if tag == "title":
            self.title_count += 1
            self.in_title = True

        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        if tag == "meta" and values.get("name", "").lower() == "description":
            self.meta_description_count += 1

        link_rel = (values.get("rel") or "").lower().split()

        if tag == "link" and "canonical" in link_rel:
            self.canonical_count += 1

        if tag == "link" and "stylesheet" in link_rel and values.get("href"):
            self.stylesheets.append(values["href"] or "")

        if tag == "script" and values.get("src"):
            self.scripts.append((values["src"] or "", (values.get("type") or "").lower()))

        if tag == "img" and "alt" not in values:
            self.images_without_alt.append(line)

        attribute = None
        if tag in {"a", "link"}:
            attribute = "href"
        elif tag in {"script", "img", "iframe", "source"}:
            attribute = "src"

        if attribute and values.get(attribute):
            self.references.append((tag, values[attribute] or "", line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text.append(data)


def iter_files(pattern: str):
    for path in ROOT.rglob(pattern):
        if not any(part in IGNORE_DIRS for part in path.parts):
            yield path


def resolve_local_reference(html_file: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference.strip())

    if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc:
        return None

    if not parsed.path or parsed.path.startswith("#"):
        return None

    clean_path = unquote(parsed.path)
    if clean_path.startswith("/"):
        target = ROOT / clean_path.lstrip("/")
    else:
        target = html_file.parent / clean_path

    if clean_path.endswith("/"):
        target /= "index.html"

    return target.resolve()


def check_html(errors: list[str], warnings: list[str]) -> None:
    for path in iter_files("*.html"):
        source = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(source)
        rel = path.relative_to(ROOT)

        if re.search(r"class\s*=\s*['\"][^'\"]*\bhref\s*=", source, re.IGNORECASE):
            errors.append(f"{rel}: vermutlich fehlerhaftes href innerhalb eines class-Attributs")

        # Header und Footer sind bewusst HTML-Fragmente ohne <html>/<head>.
        # SEO-Pflichtfelder werden deshalb nur bei vollständigen Dokumenten geprüft.
        if parser.is_html_document:
            if parser.title_count != 1:
                errors.append(f"{rel}: erwartet genau einen <title>, gefunden {parser.title_count}")
            elif not "".join(parser.title_text).strip():
                errors.append(f"{rel}: leerer <title>")

            if parser.meta_description_count != 1:
                errors.append(
                    f"{rel}: erwartet genau eine Meta-Description, gefunden {parser.meta_description_count}"
                )

            if parser.canonical_count != 1:
                errors.append(f"{rel}: erwartet genau einen Canonical-Link, gefunden {parser.canonical_count}")

            main_stylesheets = [
                href for href in parser.stylesheets
                if urlsplit(href).path == "/assets/css/main.css"
            ]
            main_scripts = [
                src for src, script_type in parser.scripts
                if urlsplit(src).path == "/assets/js/main.js" and script_type == "module"
            ]
            legacy_stylesheets = [
                href for href in parser.stylesheets
                if urlsplit(href).path.endswith("/assets/css/style.css")
            ]
            legacy_scripts = [
                src for src, _ in parser.scripts
                if urlsplit(src).path.endswith("/assets/js/script.js")
            ]

            if len(main_stylesheets) != 1:
                errors.append(
                    f"{rel}: erwartet genau eine /assets/css/main.css-Referenz, "
                    f"gefunden {len(main_stylesheets)}"
                )

            if len(main_scripts) != 1:
                errors.append(
                    f"{rel}: erwartet genau ein Modul /assets/js/main.js, "
                    f"gefunden {len(main_scripts)}"
                )

            if legacy_stylesheets:
                errors.append(f"{rel}: veraltete style.css-Referenz vorhanden")

            if legacy_scripts:
                errors.append(f"{rel}: veraltete script.js-Referenz vorhanden")

        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        if duplicates:
            errors.append(f"{rel}: doppelte IDs: {', '.join(duplicates)}")

        for line in parser.images_without_alt:
            warnings.append(f"{rel}:{line}: Bild ohne alt-Attribut")

        for tag, reference, line in parser.references:
            target = resolve_local_reference(path, reference)
            if target is None:
                continue

            if target.is_dir():
                target = target / "index.html"

            if not target.exists():
                errors.append(f"{rel}:{line}: {tag}-Referenz fehlt: {reference}")


def check_json(errors: list[str]) -> None:
    for path in iter_files("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: ungültiges JSON: {exc}")


def check_css_imports(errors: list[str]) -> None:
    pattern = re.compile(r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]\)?", re.I)

    for path in iter_files("*.css"):
        text = path.read_text(encoding="utf-8")
        for import_path in pattern.findall(text):
            if urlsplit(import_path).scheme:
                continue
            target = (path.parent / import_path).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: CSS-Import fehlt: {import_path}")


def check_js_imports(errors: list[str]) -> None:
    pattern = re.compile(
        r"(?:import|export)\s+(?:[^;]*?\s+from\s+)?['\"](\.[^'\"]+)['\"]",
        re.MULTILINE,
    )

    for path in iter_files("*.js"):
        text = path.read_text(encoding="utf-8")
        for import_path in pattern.findall(text):
            target = (path.parent / import_path).resolve()
            if target.suffix == "":
                target = target.with_suffix(".js")
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: JS-Import fehlt: {import_path}")


def check_sitemap(errors: list[str]) -> None:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        errors.append("sitemap.xml fehlt")
        return

    try:
        tree = ET.parse(sitemap)
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml: ungültiges XML: {exc}")
        return

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text or "" for node in tree.findall("sm:url/sm:loc", namespace)]

    if len(locations) != len(set(locations)):
        errors.append("sitemap.xml enthält doppelte URLs")

    for location in locations:
        path = urlsplit(location).path
        target = ROOT / path.lstrip("/")
        if path.endswith("/"):
            target /= "index.html"
        if not target.exists():
            errors.append(f"sitemap.xml verweist auf fehlende Seite: {location}")


def check_asset_locations(errors: list[str]) -> None:
    css_root = ROOT / "assets" / "css"
    js_root = ROOT / "assets" / "js"

    if css_root.exists():
        for path in css_root.rglob("*.js"):
            errors.append(
                f"{path.relative_to(ROOT)}: JavaScript-Datei liegt versehentlich im CSS-Ordner"
            )

    if js_root.exists():
        for path in js_root.rglob("*.css"):
            errors.append(
                f"{path.relative_to(ROOT)}: CSS-Datei liegt versehentlich im JavaScript-Ordner"
            )


def check_repository_hygiene(errors: list[str]) -> None:
    forbidden = [*iter_files("*.pyc")]
    forbidden.extend(path for path in ROOT.rglob("__pycache__") if path.is_dir())
    for path in forbidden:
        errors.append(f"Nicht versionieren: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_html(errors, warnings)
    check_json(errors)
    check_css_imports(errors)
    check_js_imports(errors)
    check_sitemap(errors)
    check_asset_locations(errors)
    check_repository_hygiene(errors)

    for warning in warnings:
        print(f"WARNUNG: {warning}")

    if errors:
        print("\nQualitätsprüfung fehlgeschlagen:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Qualitätsprüfung erfolgreich ({len(warnings)} Warnungen).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
