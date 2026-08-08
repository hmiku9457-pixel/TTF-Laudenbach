#!/usr/bin/env python3
"""Statische Qualitätsprüfung für die Vereinswebsite."""
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

IGNORE_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
    "playwright-report",
    "test-results",
}
ALLOWED_EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}
INLINE_EVENT_RE = re.compile(r"^on[a-z]+$", re.IGNORECASE)

OBSOLETE_PATHS = [
    ".github/workflows/apply-design-final.yml",
    ".github/workflows/apply-table-header-fix.yml",
    ".github/workflows/apply-ui-polish.yml",
    ".github/workflows/apply-ui-update.yml",
    ".github/workflows/apply-site-modernization.yml",
    ".github/workflows/site-build.yml",
    ".github/workflows/site-browser-quality.yml",
    ".github/workflows/site-quality-manual.yml",
    "tools/design-final",
    "tools/review-upgrade",
    "tools/table-header-fix",
    "tools/ui-polish",
    "tools/ui-update",
    "tools/site-modernization",
    "tools/site-build",
    "tools/quality",
    "tools/apply_phase3_seo.py",
    "tools/apply_phase4_step2.py",
    "tools/check_phase3_seo.py",
    "assets/css/consolidated",
    "assets/css/components/ui-fixes.css",
    "assets/css/components/ui-polish.css",
    "assets/css/components/ui-final.css",
    "assets/css/components/table-header-fix.css",
    "assets/css/style.css",
    "assets/js/script.js",
]


def ignored(path: Path) -> bool:
    relative = path.relative_to(ROOT).parts
    return any(part in IGNORE_PARTS for part in relative)


def iter_files(pattern: str):
    for path in ROOT.rglob(pattern):
        if not ignored(path):
            yield path


def is_full_document(soup: BeautifulSoup) -> bool:
    return (
        soup.html is not None
        and soup.head is not None
        and soup.body is not None
    )


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
    target = (
        ROOT / clean_path.lstrip("/")
        if clean_path.startswith("/")
        else source.parent / clean_path
    )
    if clean_path.endswith("/"):
        target /= "index.html"
    return target.resolve()


def check_html(errors: list[str], warnings: list[str]) -> None:
    reference_attributes = {
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
        relative = path.relative_to(ROOT)

        ids = [
            tag.get("id")
            for tag in soup.find_all(attrs={"id": True})
        ]
        duplicates = sorted(
            {item for item in ids if ids.count(item) > 1}
        )
        if duplicates:
            errors.append(
                f"{relative}: doppelte IDs: {', '.join(duplicates)}"
            )

        for image in soup.find_all("img"):
            if not image.has_attr("alt"):
                warnings.append(f"{relative}: Bild ohne alt-Attribut")

        for element in soup.find_all(True):
            for attribute in element.attrs:
                if INLINE_EVENT_RE.match(attribute):
                    errors.append(
                        f"{relative}: Inline-Event-Handler nicht erlaubt: "
                        f"{attribute}"
                    )

            attribute = reference_attributes.get(element.name)
            reference = element.get(attribute) if attribute else None
            if not reference:
                continue

            try:
                target = resolve_local_reference(path, str(reference))
            except ValueError as exc:
                errors.append(
                    f"{relative}: {element.name}-Referenz: {exc}"
                )
                continue

            if target and not target.exists():
                errors.append(
                    f"{relative}: {element.name}-Referenz fehlt: "
                    f"{reference}"
                )

        if not is_full_document(soup):
            continue

        titles = soup.find_all("title")
        if len(titles) != 1 or not titles[0].get_text(strip=True):
            errors.append(
                f"{relative}: erwartet genau einen nichtleeren <title>"
            )

        descriptions = soup.find_all(
            "meta",
            attrs={"name": re.compile(r"^description$", re.IGNORECASE)},
        )
        if len(descriptions) != 1:
            errors.append(
                f"{relative}: erwartet genau eine Meta-Description"
            )

        canonicals = soup.find_all(
            "link",
            rel=lambda value: value and "canonical" in value,
        )
        if len(canonicals) != 1:
            errors.append(
                f"{relative}: erwartet genau einen Canonical-Link"
            )

        mains = soup.find_all("main")
        if len(mains) != 1 or mains[0].get("id") != "main-content":
            errors.append(
                f'{relative}: erwartet genau ein <main id="main-content">'
            )
        elif len(mains[0].find_all("h1")) != 1:
            errors.append(
                f"{relative}: im Hauptinhalt wird genau eine H1 erwartet"
            )

        if soup.select("header h1"):
            errors.append(f"{relative}: H1 im Header gefunden")

        skip_links = soup.select(
            'a.skip-link[href="#main-content"]'
        )
        if len(skip_links) != 1:
            errors.append(
                f"{relative}: Skip-Link fehlt oder ist doppelt"
            )

        styles = [
            link.get("href")
            for link in soup.find_all(
                "link",
                rel=lambda value: value and "stylesheet" in value,
            )
        ]
        if styles.count("/assets/css/site.bundle.css") != 1:
            errors.append(
                f"{relative}: erwartet genau eine Referenz auf "
                "/assets/css/site.bundle.css"
            )

        scripts = [
            script.get("src")
            for script in soup.find_all("script")
            if script.get("src")
        ]
        if scripts.count("/assets/js/main.js") != 1:
            errors.append(
                f"{relative}: erwartet genau eine Referenz auf "
                "/assets/js/main.js"
            )
        main_script = soup.find(
            "script",
            src="/assets/js/main.js",
        )
        if main_script and main_script.get("type") != "module":
            errors.append(
                f"{relative}: main.js muss als ES-Modul geladen werden"
            )

        for index, table in enumerate(
            soup.find_all("table"),
            start=1,
        ):
            if not table.find("caption"):
                errors.append(
                    f"{relative}: Tabelle {index} hat kein <caption>"
                )
            thead = table.find("thead")
            if thead:
                if thead.find("td"):
                    errors.append(
                        f"{relative}: <td> im <thead> gefunden"
                    )
                for header in thead.find_all("th"):
                    if header.get("scope") != "col":
                        errors.append(
                            f'{relative}: Tabellenkopf ohne scope="col"'
                        )


def check_json(errors: list[str]) -> None:
    for path in iter_files("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(
                f"{path.relative_to(ROOT)}: ungültiges JSON: {exc}"
            )


def check_css_imports(errors: list[str]) -> None:
    pattern = re.compile(
        r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]\)?",
        re.IGNORECASE,
    )
    for path in iter_files("*.css"):
        for import_path in pattern.findall(
            path.read_text(encoding="utf-8")
        ):
            parsed = urlsplit(import_path)
            if parsed.scheme or parsed.netloc:
                continue
            if not (path.parent / import_path).resolve().exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: "
                    f"CSS-Import fehlt: {import_path}"
                )


def check_js_imports(errors: list[str]) -> None:
    pattern = re.compile(
        r"(?:import|export)\s+"
        r"(?:[^;]*?\s+from\s+)?"
        r"['\"](\.[^'\"]+)['\"]",
        re.MULTILINE,
    )
    for path in iter_files("*.js"):
        for import_path in pattern.findall(
            path.read_text(encoding="utf-8")
        ):
            target = (path.parent / import_path).resolve()
            if not target.suffix:
                target = target.with_suffix(".js")
            if not target.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: "
                    f"JS-Import fehlt: {import_path}"
                )


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

    namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }
    locations = [
        node.text or ""
        for node in tree.findall("sm:url/sm:loc", namespace)
    ]
    if len(locations) != len(set(locations)):
        errors.append("sitemap.xml enthält doppelte URLs")

    for location in locations:
        url_path = urlsplit(location).path
        target = ROOT / url_path.lstrip("/")
        if url_path.endswith("/"):
            target /= "index.html"
        if not target.exists():
            errors.append(
                "sitemap.xml verweist auf fehlende Seite: "
                f"{location}"
            )


def check_repository_hygiene(errors: list[str]) -> None:
    for relative in OBSOLETE_PATHS:
        if (ROOT / relative).exists():
            errors.append(
                f"Veralteter Pfad muss entfernt bleiben: {relative}"
            )

    for path in iter_files("*.pyc"):
        errors.append(
            f"Nicht versionieren: {path.relative_to(ROOT)}"
        )

    for path in ROOT.rglob("__pycache__"):
        if path.is_dir() and not ignored(path):
            errors.append(
                f"Nicht versionieren: {path.relative_to(ROOT)}"
            )


def check_generated_files(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "tools/site/build.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        errors.append(
            result.stderr.strip()
            or result.stdout.strip()
            or "Generierte Dateien sind nicht aktuell"
        )


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_html(errors, warnings)
    check_json(errors)
    check_css_imports(errors)
    check_js_imports(errors)
    check_sitemap(errors)
    check_repository_hygiene(errors)
    check_generated_files(errors)

    for warning in warnings:
        print(f"WARNUNG: {warning}")

    if errors:
        print("\nQualitätsprüfung fehlgeschlagen:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Qualitätsprüfung erfolgreich "
        f"({len(warnings)} Warnungen)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
