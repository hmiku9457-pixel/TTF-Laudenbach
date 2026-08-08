#!/usr/bin/env python3
"""Erzeugt die wenigen abgeleiteten Dateien der Vereinswebsite.

Quellen:
- components/header.html und components/footer.html
- assets/css/main.css und dessen lokale @imports
- vorhandene, indexierbare HTML-Seiten

Erzeugt:
- eingebettete Header-/Footer-Blöcke in den HTML-Seiten
- assets/css/site.bundle.css
- sitemap.xml
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]

HEADER_START = "<!-- TTF:HEADER:START -->"
HEADER_END = "<!-- TTF:HEADER:END -->"
FOOTER_START = "<!-- TTF:FOOTER:START -->"
FOOTER_END = "<!-- TTF:FOOTER:END -->"

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


def component_block(component: str, start: str, end: str) -> str:
    return f"{start}\n{component.strip()}\n{end}"


def replace_component(
    text: str,
    element_id: str,
    block: str,
    start: str,
    end: str,
) -> tuple[str, bool]:
    marker_pattern = re.compile(
        rf'(<div\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>)'
        rf'(.*?{re.escape(start)}.*?{re.escape(end)}.*?)'
        rf"(</div>)",
        re.IGNORECASE | re.DOTALL,
    )
    match = marker_pattern.search(text)
    if match:
        updated = (
            text[: match.start()]
            + match.group(1)
            + "\n"
            + block
            + "\n"
            + match.group(3)
            + text[match.end() :]
        )
        return updated, True

    empty_pattern = re.compile(
        rf'<div\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>\s*</div>',
        re.IGNORECASE | re.DOTALL,
    )
    replacement = f'<div id="{element_id}">\n{block}\n</div>'
    updated, count = empty_pattern.subn(replacement, text, count=1)
    return updated, bool(count)


def expected_component_pages() -> tuple[dict[Path, str], list[str]]:
    header = (ROOT / "components/header.html").read_text(encoding="utf-8")
    footer = (ROOT / "components/footer.html").read_text(encoding="utf-8")
    expected: dict[Path, str] = {}
    warnings: list[str] = []

    for path in pages():
        original = path.read_text(encoding="utf-8")
        updated, header_found = replace_component(
            original,
            "header-container",
            component_block(header, HEADER_START, HEADER_END),
            HEADER_START,
            HEADER_END,
        )
        updated, footer_found = replace_component(
            updated,
            "footer-container",
            component_block(footer, FOOTER_START, FOOTER_END),
            FOOTER_START,
            FOOTER_END,
        )

        if path.name != "maintenance.html":
            if not header_found:
                warnings.append(
                    f"Kein Header-Platzhalter in {path.relative_to(ROOT)}"
                )
            if not footer_found:
                warnings.append(
                    f"Kein Footer-Platzhalter in {path.relative_to(ROOT)}"
                )

        expected[path] = updated

    return expected, warnings


def expand_css(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(
            str(item.relative_to(ROOT)) for item in (*stack, path)
        )
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
            result.append(
                expand_css(path.parent / import_value, (*stack, path))
            )

        cursor = match.end()

    result.append(text[cursor:])
    return "".join(result).strip() + "\n"


def expected_css() -> str:
    banner = (
        "/* Automatisch aus assets/css/main.css erzeugt. "
        "Nicht direkt bearbeiten. */\n"
    )
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

    entries = sorted(
        set(entries),
        key=lambda url: (url != BASE_URL + "/", url),
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in entries:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(url)}</loc>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def update_or_check(
    path: Path,
    expected: str,
    write_changes: bool,
    changed: list[Path],
) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == expected:
        return

    changed.append(path)
    if write_changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")


def build(write_changes: bool) -> int:
    changed: list[Path] = []

    component_pages, warnings = expected_component_pages()
    for warning in warnings:
        print(f"WARNUNG: {warning}")

    for path, expected in component_pages.items():
        update_or_check(path, expected, write_changes, changed)

    update_or_check(CSS_OUTPUT, expected_css(), write_changes, changed)
    update_or_check(
        SITEMAP_OUTPUT,
        expected_sitemap(),
        write_changes,
        changed,
    )

    if changed and not write_changes:
        print("Generierte Dateien sind nicht aktuell:", file=sys.stderr)
        for path in changed:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        print(
            "\nUnter GitHub Actions den Workflow "
            "'Website bauen und prüfen' mit aktivierter Option "
            "'Header, Footer, CSS-Bundle und Sitemap aktualisieren' starten.",
            file=sys.stderr,
        )
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
    parser.add_argument(
        "--write",
        action="store_true",
        help="Abgeleitete Dateien schreiben statt nur zu prüfen.",
    )
    args = parser.parse_args()
    return build(args.write)


if __name__ == "__main__":
    raise SystemExit(main())
