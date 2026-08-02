#!/usr/bin/env python3
"""Schaltet die TTF-Laudenbach-Webseite auf die modularen Phase-4-Dateien um.

Das Skript verändert ausschließlich HTML-Dateien. Die alten produktiven Dateien
assets/css/style.css und assets/js/script.js bleiben als Rückfall erhalten.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {".git", "__pycache__", "node_modules"}

MAIN_STYLESHEET = '<link rel="stylesheet" href="/assets/css/main.css">'
MAIN_SCRIPT = '<script type="module" src="/assets/js/main.js"></script>'

STYLESHEET_PATTERN = re.compile(
    r"<link\b(?=[^>]*\brel\s*=\s*['\"][^'\"]*stylesheet[^'\"]*['\"])[^>]*"
    r"\bhref\s*=\s*['\"][^'\"]*assets/css/(?:style|main)\.css['\"][^>]*>",
    re.IGNORECASE,
)
SCRIPT_PATTERN = re.compile(
    r"<script\b[^>]*\bsrc\s*=\s*['\"][^'\"]*assets/js/(?:script|main)\.js['\"][^>]*>"
    r"\s*</script>",
    re.IGNORECASE,
)
HTML_DOCUMENT_PATTERN = re.compile(r"<html\b", re.IGNORECASE)


def iter_html_files():
    for path in ROOT.rglob("*.html"):
        if not any(part in IGNORE_DIRS for part in path.parts):
            yield path


def replace_first_and_remove_duplicates(source: str, pattern: re.Pattern[str], replacement: str) -> tuple[str, int]:
    matches = list(pattern.finditer(source))

    if not matches:
        return source, 0

    pieces: list[str] = []
    cursor = 0

    for index, match in enumerate(matches):
        pieces.append(source[cursor:match.start()])
        if index == 0:
            pieces.append(replacement)
        cursor = match.end()

    pieces.append(source[cursor:])
    return "".join(pieces), len(matches)


def insert_before_closing_tag(source: str, closing_tag: str, content: str) -> str:
    match = re.search(re.escape(closing_tag), source, re.IGNORECASE)
    if not match:
        raise ValueError(f"{closing_tag} fehlt")

    before = source[:match.start()].rstrip()
    after = source[match.start():]
    return f"{before}\n\t\t{content}\n{after}"


def normalize_assets(source: str) -> str:
    updated, stylesheet_count = replace_first_and_remove_duplicates(
        source,
        STYLESHEET_PATTERN,
        MAIN_STYLESHEET,
    )

    if stylesheet_count == 0:
        updated = insert_before_closing_tag(updated, "</head>", MAIN_STYLESHEET)

    updated, script_count = replace_first_and_remove_duplicates(
        updated,
        SCRIPT_PATTERN,
        MAIN_SCRIPT,
    )

    if script_count == 0:
        updated = insert_before_closing_tag(updated, "</body>", MAIN_SCRIPT)

    return updated


def fix_known_links(source: str, relative_path: str) -> str:
    updated = source.replace("/TTF-Laudenbach/", "/")
    updated = updated.replace('href="/assets/startpage.html"', 'href="/"')
    updated = updated.replace("href='/assets/startpage.html'", "href='/'")

    updated = re.sub(
        r"href\s*=\s*(['\"])www\.vierelemente2018\.de/?\1",
        'href="https://vierelemente2018.de/" target="_blank" rel="noopener noreferrer"',
        updated,
        flags=re.IGNORECASE,
    )

    # Repariert den aktuell fehlerhaft gesetzten Zurück-Link in artikel1.html.
    updated = updated.replace(
        '<a class="button button--card href="/index.html">Zurück</a>',
        '<a class="button button--card" href="/">Zurück</a>',
    )

    if relative_path == "pages/news/artikel2.html":
        if 'id="header-container"' not in updated:
            updated = re.sub(
                r"(<body\b[^>]*>)",
                lambda match: match.group(1) + '\n\t\t<div id="header-container"></div>\n',
                updated,
                count=1,
                flags=re.IGNORECASE,
            )

        if 'id="footer-container"' not in updated:
            module_match = re.search(
                r"<script\b[^>]*\bsrc\s*=\s*['\"]/assets/js/main\.js['\"][^>]*>\s*</script>",
                updated,
                re.IGNORECASE,
            )
            footer = '\n\t\t<div id="footer-container"></div>\n\n\t\t'

            if module_match:
                updated = updated[:module_match.start()] + footer + updated[module_match.start():]
            else:
                updated = insert_before_closing_tag(
                    updated,
                    "</body>",
                    '<div id="footer-container"></div>',
                )

        updated = re.sub(
            r'<a\s+href=["\']/["\']>Zurück</a>',
            '<a class="button button--card" href="/">Zurück</a>',
            updated,
            count=1,
            flags=re.IGNORECASE,
        )

    return updated


def validate_document(source: str, relative_path: str) -> list[str]:
    errors: list[str] = []

    stylesheet_matches = re.findall(
        r"<link\b(?=[^>]*\brel\s*=\s*['\"][^'\"]*stylesheet[^'\"]*['\"])[^>]*"
        r"\bhref\s*=\s*['\"](/assets/css/main\.css)['\"][^>]*>",
        source,
        re.IGNORECASE,
    )
    module_matches = re.findall(
        r"<script\b(?=[^>]*\btype\s*=\s*['\"]module['\"])[^>]*"
        r"\bsrc\s*=\s*['\"](/assets/js/main\.js)['\"][^>]*>\s*</script>",
        source,
        re.IGNORECASE,
    )

    if len(stylesheet_matches) != 1:
        errors.append(f"{relative_path}: main.css nicht genau einmal eingebunden")
    if len(module_matches) != 1:
        errors.append(f"{relative_path}: main.js nicht genau einmal als Modul eingebunden")
    if re.search(r"assets/css/style\.css", source, re.IGNORECASE):
        errors.append(f"{relative_path}: alte style.css-Referenz vorhanden")
    if re.search(r"assets/js/script\.js", source, re.IGNORECASE):
        errors.append(f"{relative_path}: alte script.js-Referenz vorhanden")

    return errors


def preflight() -> None:
    required = [
        ROOT / "assets/css/main.css",
        ROOT / "assets/js/main.js",
        ROOT / "assets/css/style.css",
        ROOT / "assets/js/script.js",
    ]
    missing = [path.relative_to(ROOT) for path in required if not path.exists()]

    if missing:
        formatted = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Benötigte Phase-4-Dateien fehlen: {formatted}")


def main() -> int:
    preflight()
    changed: list[Path] = []
    validation_errors: list[str] = []

    for path in iter_html_files():
        relative_path = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        updated = fix_known_links(source, relative_path)

        if HTML_DOCUMENT_PATTERN.search(updated):
            updated = normalize_assets(updated)
            validation_errors.extend(validate_document(updated, relative_path))

        if updated != source:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))

    remaining_patterns = {
        "/TTF-Laudenbach/": "alter Repository-Präfix",
        "/assets/startpage.html": "falscher Startseitenpfad",
        'href="www.vierelemente2018.de': "externer Link ohne Protokoll",
        "href='www.vierelemente2018.de": "externer Link ohne Protokoll",
    }

    for path in iter_html_files():
        source = path.read_text(encoding="utf-8")
        relative_path = path.relative_to(ROOT).as_posix()

        for pattern, description in remaining_patterns.items():
            if pattern in source:
                validation_errors.append(f"{relative_path}: {description} weiterhin vorhanden")

    if validation_errors:
        print("Phase-4-Migration fehlgeschlagen:", file=sys.stderr)
        for error in validation_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if changed:
        print("Geänderte HTML-Dateien:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Keine Änderungen erforderlich. Phase 4 Schritt 2 ist bereits angewendet.")

    print(f"Phase-4-Migration erfolgreich ({len(changed)} geänderte Dateien).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
