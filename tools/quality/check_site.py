#!/usr/bin/env python3
"""Qualitätsprüfung für Struktur, Assets, Links, JSON und Semantik."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
IGNORE_PARTS = {".git", "__pycache__", "node_modules"}
IGNORE_PREFIXES = {("tools", "review-upgrade", "templates")}
ALLOWED_EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}
INLINE_EVENT_RE = re.compile(r"^on[a-z]+$", re.I)


def ignored(path: Path) -> bool:
    relative = path.relative_to(ROOT).parts
    if any(part in IGNORE_PARTS for part in relative):
        return True
    return any(relative[: len(prefix)] == prefix for prefix in IGNORE_PREFIXES)


def iter_files(pattern: str):
    for path in ROOT.rglob(pattern):
        if not ignored(path):
            yield path


def is_full_document(soup: BeautifulSoup) -> bool:
    return soup.html is not None and soup.head is not None and soup.body is not None


def resolve_local_reference(source: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference.strip())
    scheme = parsed.scheme.lower()
    if scheme == "javascript":
        raise ValueError("javascript:-URL ist nicht erlaubt")
    if scheme in ALLOWED_EXTERNAL_SCHEMES or parsed.netloc:
        return None
    if not parsed.path or parsed.path.startswith("#"):
        return None

    clean_path = unquote(parsed.path)
    target = ROOT / clean_path.lstrip("/") if clean_path.startswith("/") else source.parent / clean_path
    if clean_path.endswith("/"):
        target /= "index.html"
    return target.resolve()


def check_html(errors: list[str], warnings: list[str]) -> None:
    ref_attributes = {
        "a": "href",
        "link": "href",
        "script": "src",
        "img": "src",
        "iframe": "src",
        "source": "src",
    }

    for path in iter_files("*.html"):
        text = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(text, "html.parser")
        rel = path.relative_to(ROOT)
        full = is_full_document(soup)

        ids = [tag.get("id") for tag in soup.find_all(attrs={"id": True})]
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        if duplicates:
            errors.append(f"{rel}: doppelte IDs: {', '.join(duplicates)}")

        for image in soup.find_all("img"):
            if not image.has_attr("alt"):
                warnings.append(f"{rel}: Bild ohne alt-Attribut")

        for element in soup.find_all(True):
            for attribute in element.attrs:
                if INLINE_EVENT_RE.match(attribute):
                    errors.append(f"{rel}: Inline-Event-Handler nicht erlaubt: {attribute}")

            attribute = ref_attributes.get(element.name)
            reference = element.get(attribute) if attribute else None
            if reference:
                try:
                    target = resolve_local_reference(path, str(reference))
                except ValueError as exc:
                    errors.append(f"{rel}: {element.name}-Referenz: {exc}")
                    continue
                if target and not target.exists():
                    errors.append(f"{rel}: {element.name}-Referenz fehlt: {reference}")

        if not full:
            continue

        if len(soup.find_all("title")) != 1 or not soup.title.get_text(strip=True):
            errors.append(f"{rel}: erwartet genau einen nichtleeren <title>")
        if len(soup.find_all("meta", attrs={"name": re.compile(r"^description$", re.I)})) != 1:
            errors.append(f"{rel}: erwartet genau eine Meta-Description")
        if len(soup.find_all("link", rel=lambda value: value and "canonical" in value)) != 1:
            errors.append(f"{rel}: erwartet genau einen Canonical-Link")

        mains = soup.find_all("main")
        if len(mains) != 1 or mains[0].get("id") != "main-content":
            errors.append(f"{rel}: erwartet genau ein <main id=\"main-content\">")
        elif len(mains[0].find_all("h1")) != 1:
            errors.append(f"{rel}: im Hauptinhalt wird genau eine H1 erwartet")

        skip_links = soup.select('a.skip-link[href="#main-content"]')
        if len(skip_links) != 1:
            errors.append(f"{rel}: Skip-Link zum Hauptinhalt fehlt oder ist doppelt")

        styles = [link.get("href") for link in soup.find_all("link", rel=lambda value: value and "stylesheet" in value)]
        if styles.count("/assets/css/site.bundle.css") != 1:
            errors.append(f"{rel}: erwartet genau eine Referenz auf /assets/css/site.bundle.css")
        if any(value and (value.endswith("/style.css") or value.endswith("/main.css")) for value in styles):
            errors.append(f"{rel}: veraltete oder ungebündelte CSS-Referenz")

        scripts = [script.get("src") for script in soup.find_all("script") if script.get("src")]
        if scripts.count("/assets/js/main.js") != 1:
            errors.append(f"{rel}: erwartet genau eine Referenz auf /assets/js/main.js")
        main_script = soup.find("script", src="/assets/js/main.js")
        if main_script and main_script.get("type") != "module":
            errors.append(f"{rel}: main.js muss als ES-Modul geladen werden")
        if any(value and value.endswith("/script.js") for value in scripts):
            errors.append(f"{rel}: Legacy-script.js wird noch geladen")

        for index, table in enumerate(soup.find_all("table"), start=1):
            if not table.find("caption"):
                errors.append(f"{rel}: Tabelle {index} hat keine Beschriftung (<caption>)")
            thead = table.find("thead")
            if thead:
                for header in thead.find_all("th"):
                    if header.get("scope") != "col":
                        errors.append(f"{rel}: Tabellenkopf ohne scope=\"col\"")
                if thead.find("td"):
                    errors.append(f"{rel}: <td> im <thead> gefunden")


def check_json(errors: list[str]) -> None:
    for path in iter_files("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: ungültiges JSON: {exc}")


def check_css_imports(errors: list[str]) -> None:
    pattern = re.compile(r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]\)?", re.I)
    for path in iter_files("*.css"):
        for import_path in pattern.findall(path.read_text(encoding="utf-8")):
            if urlsplit(import_path).scheme:
                continue
            if not (path.parent / import_path).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}: CSS-Import fehlt: {import_path}")


def check_js_imports(errors: list[str]) -> None:
    pattern = re.compile(r"(?:import|export)\s+(?:[^;]*?\s+from\s+)?['\"](\.[^'\"]+)['\"]", re.M)
    for path in iter_files("*.js"):
        for import_path in pattern.findall(path.read_text(encoding="utf-8")):
            target = (path.parent / import_path).resolve()
            if not target.suffix:
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
        url_path = urlsplit(location).path
        target = ROOT / url_path.lstrip("/")
        if url_path.endswith("/"):
            target /= "index.html"
        if not target.exists():
            errors.append(f"sitemap.xml verweist auf fehlende Seite: {location}")


def check_repository_hygiene(errors: list[str]) -> None:
    for relative in ["assets/css/style.css", "assets/js/script.js"]:
        if (ROOT / relative).exists():
            errors.append(f"Legacy-Datei muss entfernt werden: {relative}")
    forbidden = [*iter_files("*.pyc")]
    forbidden.extend(path for path in ROOT.rglob("__pycache__") if path.is_dir() and not ignored(path))
    for path in forbidden:
        errors.append(f"Nicht versionieren: {path.relative_to(ROOT)}")


def check_bundle(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "tools/review-upgrade/build_css.py", "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        errors.append(result.stderr.strip() or result.stdout.strip() or "CSS-Bundle ist nicht aktuell")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    check_html(errors, warnings)
    check_json(errors)
    check_css_imports(errors)
    check_js_imports(errors)
    check_sitemap(errors)
    check_repository_hygiene(errors)
    check_bundle(errors)

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
