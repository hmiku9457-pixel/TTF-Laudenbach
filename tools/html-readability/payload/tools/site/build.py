#!/usr/bin/env python3
"""Erzeugt CSS-Bundle und Sitemap.

Header und Footer werden nicht mehr in jede HTML-Datei kopiert. Sie werden
zur Laufzeit aus components/header.html und components/footer.html geladen.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]

CSS_ENTRY = ROOT / "assets/css/main.css"
CSS_OUTPUT = ROOT / "assets/css/site.bundle.css"
CSS_IMPORT_RE = re.compile(
    r"^\s*@import\s+(?:url\()?['\"]([^'\"]+)['\"]\)?\s*;\s*$",
    re.IGNORECASE | re.MULTILINE,
)

SITEMAP_OUTPUT = ROOT / "sitemap.xml"
BASE_URL = "https://www.ttf-laudenbach.de"
SITEMAP_EXCLUDED = {
    "404.html",
    "pages/index.html",
    "pages/startpage.html",
    "pages/maintenance.html",
}
CANONICAL_RE = re.compile(
    r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',
    re.IGNORECASE,
)
ROBOTS_RE = re.compile(
    r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)',
    re.IGNORECASE,
)


def pages(include_404: bool = True) -> list[Path]:
    result = [ROOT / "index.html"]
    if include_404:
        result.append(ROOT / "404.html")
    result.extend(sorted((ROOT / "pages").rglob("*.html")))
    return [path for path in result if path.is_file()]


def expand_css(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(item.relative_to(ROOT)) for item in (*stack, path))
        raise RuntimeError(f"Zirkulärer CSS-Import: {chain}")
    if not path.is_file():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")
    result = [f"/* Quelle: {path.relative_to(ROOT).as_posix()} */\n"]
    cursor = 0

    for match in CSS_IMPORT_RE.finditer(text):
        result.append(text[cursor : match.start()])
        import_value = match.group(1)
        parsed = urlsplit(import_value)

        if parsed.scheme or import_value.startswith("data:"):
            result.append(match.group(0))
        else:
            result.append(expand_css(path.parent / import_value, (*stack, path)))

        cursor = match.end()

    result.append(text[cursor:])
    return "".join(result).strip() + "\n"


def expected_css() -> str:
    banner = "/* Automatisch aus assets/css/main.css erzeugt. Nicht direkt bearbeiten. */\n"
    return banner + expand_css(CSS_ENTRY)


def page_url(path: Path, text: str) -> str:
    canonical = CANONICAL_RE.search(text)
    if canonical:
        return canonical.group(1).strip()

    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return BASE_URL + "/"
    return BASE_URL + "/" + relative


def expected_sitemap() -> str:
    entries: list[str] = []

    for path in pages(include_404=False):
        relative = path.relative_to(ROOT).as_posix()
        if relative in SITEMAP_EXCLUDED:
            continue

        text = path.read_text(encoding="utf-8")
        robots = ROBOTS_RE.search(text)
        if robots and "noindex" in robots.group(1).lower():
            continue

        entries.append(page_url(path, text))

    entries = sorted(set(entries), key=lambda url: (url != BASE_URL + "/", url))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in entries:
        lines.extend([
            "  <url>",
            f"    <loc>{html.escape(url)}</loc>",
            "  </url>",
        ])
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def update_or_check(path: Path, expected: str, write_changes: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == expected:
        return

    changed.append(path)
    if write_changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")


def build(write_changes: bool) -> int:
    changed: list[Path] = []
    update_or_check(CSS_OUTPUT, expected_css(), write_changes, changed)
    update_or_check(SITEMAP_OUTPUT, expected_sitemap(), write_changes, changed)

    if changed and not write_changes:
        print("Generierte Dateien sind nicht aktuell:", file=sys.stderr)
        for path in changed:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if changed:
        print("Generierte Dateien aktualisiert:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Alle generierten Dateien sind aktuell.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    return build(args.write)


if __name__ == "__main__":
    raise SystemExit(main())
