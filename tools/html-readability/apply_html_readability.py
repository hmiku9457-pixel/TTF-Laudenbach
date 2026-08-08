#!/usr/bin/env python3
"""Vereinfacht die HTML-Dateien und entfernt technische Wiederholungen."""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
PAYLOAD_BUILD = SCRIPT_DIR / "payload/tools/site/build.py"
BASE_URL = "https://www.ttf-laudenbach.de/"

HEADER_START = "<!-- TTF:HEADER:START -->"
HEADER_END = "<!-- TTF:HEADER:END -->"
FOOTER_START = "<!-- TTF:FOOTER:START -->"
FOOTER_END = "<!-- TTF:FOOTER:END -->"


def require_repository() -> None:
    required = [
        "index.html",
        "components/header.html",
        "components/footer.html",
        "assets/js/main.js",
        "assets/js/core/components.js",
        "tools/site/build.py",
        "tools/quality/check_site.py",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise RuntimeError("Aktueller Repository-Stand fehlt: " + ", ".join(missing))


def pages() -> list[Path]:
    result = [ROOT / "index.html", ROOT / "404.html"]
    result.extend(sorted((ROOT / "pages").rglob("*.html")))
    return [path for path in result if path.is_file()]


def canonical_for(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return BASE_URL
    return urljoin(BASE_URL, relative)


def page_data(path: Path, text: str) -> tuple[str, str, str, bool]:
    soup = BeautifulSoup(text, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_tag = soup.find(
        "meta", attrs={"name": re.compile(r"^description$", re.IGNORECASE)}
    )
    canonical_tag = soup.find(
        "link", rel=lambda value: value and "canonical" in value
    )
    robots_tag = soup.find(
        "meta", attrs={"name": re.compile(r"^robots$", re.IGNORECASE)}
    )

    description = str(description_tag.get("content", "")).strip() if description_tag else ""
    canonical = str(canonical_tag.get("href", "")).strip() if canonical_tag else ""
    robots = str(robots_tag.get("content", "")).lower() if robots_tag else ""

    if not title:
        title = "Seite nicht gefunden | TTF Laudenbach" if path.name == "404.html" else path.stem
    if not description:
        description = (
            "Die angeforderte Seite wurde nicht gefunden."
            if path.name == "404.html"
            else f"Informationen der TTF Laudenbach: {title}."
        )

    noindex = "noindex" in robots or path.name in {"404.html", "maintenance.html"}
    return title, description, canonical or canonical_for(path), noindex


def compact_head(title: str, description: str, canonical: str, noindex: bool) -> str:
    lines = [
        "<head>",
        "    <!-- Technische Grundeinstellungen -->",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "",
        "    <!-- Angaben für Browser und Suchmaschinen -->",
        f"    <title>{html.escape(title)}</title>",
        f'    <meta name="description" content="{html.escape(description, quote=True)}">',
        f'    <link rel="canonical" href="{html.escape(canonical, quote=True)}">',
    ]
    if noindex:
        lines.append('    <meta name="robots" content="noindex, follow">')
    lines.extend([
        "",
        "    <!-- Gemeinsame Gestaltung -->",
        '    <link rel="stylesheet" href="/assets/css/site.bundle.css">',
        "</head>",
    ])
    return "\n".join(lines)


def remove_embedded_block(text: str, start: str, end: str) -> str:
    return re.sub(
        rf"\s*{re.escape(start)}.*?{re.escape(end)}\s*",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def ensure_empty_container(text: str, container_id: str, comment: str) -> str:
    pattern = re.compile(
        rf'<div\b[^>]*\bid=["\']{re.escape(container_id)}["\'][^>]*>.*?</div>',
        re.IGNORECASE | re.DOTALL,
    )
    replacement = f"<!-- {comment} -->\n<div id=\"{container_id}\"></div>"
    updated, count = pattern.subn(replacement, text, count=1)
    return updated if count else text


def simplify_html() -> None:
    head_pattern = re.compile(r"<head\b[^>]*>.*?</head>", re.IGNORECASE | re.DOTALL)

    for path in pages():
        original = path.read_text(encoding="utf-8")
        title, description, canonical, noindex = page_data(path, original)
        if not head_pattern.search(original):
            raise RuntimeError(f"Kein vollständiger <head> in {path.relative_to(ROOT)}")

        updated = head_pattern.sub(
            compact_head(title, description, canonical, noindex),
            original,
            count=1,
        )
        updated = remove_embedded_block(updated, HEADER_START, HEADER_END)
        updated = remove_embedded_block(updated, FOOTER_START, FOOTER_END)
        updated = ensure_empty_container(
            updated,
            "header-container",
            "Gemeinsame Navigation wird automatisch geladen.",
        )
        updated = ensure_empty_container(
            updated,
            "footer-container",
            "Gemeinsamer Footer wird automatisch geladen.",
        )
        path.write_text(updated, encoding="utf-8")


def enable_runtime_components() -> None:
    path = ROOT / "assets/js/main.js"
    text = path.read_text(encoding="utf-8")

    import_line = 'import { loadComponent } from "./core/components.js";'
    if import_line not in text:
        text = import_line + "\n" + text

    marker = "// Gemeinsame Seitenelemente laden"
    if marker not in text:
        pattern = re.compile(r"(async function initializePage\(\)\s*\{\s*)")

        def replacement(match: re.Match[str]) -> str:
            return match.group(1) + '''    // Gemeinsame Seitenelemente laden
    await Promise.all([
        loadComponent(
            "header-container",
            "/components/header.html",
            "Die Navigation konnte nicht geladen werden.",
        ),
        loadComponent(
            "footer-container",
            "/components/footer.html",
            "Der Footer konnte nicht geladen werden.",
        ),
    ]);

'''

        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise RuntimeError("initializePage() wurde in assets/js/main.js nicht gefunden.")

    path.write_text(text, encoding="utf-8")


def install_simple_build() -> None:
    if not PAYLOAD_BUILD.is_file():
        raise RuntimeError("Vereinfachtes Build-Skript fehlt im Paket.")
    shutil.copy2(PAYLOAD_BUILD, ROOT / "tools/site/build.py")


def write_editorconfig() -> None:
    (ROOT / ".editorconfig").write_text(
        """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{html,css,js,mjs,json}]
indent_style = space
indent_size = 4
""",
        encoding="utf-8",
    )


def main() -> int:
    require_repository()
    simplify_html()
    enable_runtime_components()
    install_simple_build()
    write_editorconfig()

    print("HTML-Dateien wurden vereinfacht und für Prettier vorbereitet.")
    print("Header und Footer werden künftig zentral aus components/ geladen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
