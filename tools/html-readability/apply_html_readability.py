#!/usr/bin/env python3
"""Vereinfacht und bereinigt die HTML-Dateien der Vereinswebsite.

Die Migration:
- reduziert den <head> auf die wirklich gepflegten Angaben,
- entfernt duplizierte Social-Media-Metadaten und das große JSON-LD,
- entfernt eingebettete Header-/Footer-Kopien,
- aktiviert wieder die zentralen Komponenten aus components/,
- beendet die automatische HTML-Umschreibung im Build,
- passt den No-JavaScript-Browsertest an,
- löscht sich nach der Anwendung selbst.
"""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
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
        "tools/site-build/build_site.py",
        "tests/e2e/site-smoke.spec.mjs",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise RuntimeError(
            "Der aktuelle Architekturstand wurde nicht gefunden. Fehlend: "
            + ", ".join(missing)
        )


def pages() -> list[Path]:
    result = [ROOT / "index.html", ROOT / "404.html"]
    result.extend(sorted((ROOT / "pages").rglob("*.html")))
    return [path for path in result if path.is_file()]


def canonical_for(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return BASE_URL
    return urljoin(BASE_URL, relative)


def extract_page_data(path: Path, text: str) -> tuple[str, str, str, bool]:
    soup = BeautifulSoup(text, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_tag = soup.find(
        "meta",
        attrs={"name": re.compile(r"^description$", re.IGNORECASE)},
    )
    description = (
        str(description_tag.get("content", "")).strip()
        if description_tag
        else ""
    )
    canonical_tag = soup.find(
        "link",
        rel=lambda value: value and "canonical" in value,
    )
    canonical = (
        str(canonical_tag.get("href", "")).strip()
        if canonical_tag
        else ""
    )
    robots_tag = soup.find(
        "meta",
        attrs={"name": re.compile(r"^robots$", re.IGNORECASE)},
    )
    robots = (
        str(robots_tag.get("content", "")).lower()
        if robots_tag
        else ""
    )

    if not title:
        if path.name == "404.html":
            title = "Seite nicht gefunden | TTF Laudenbach"
        else:
            raise RuntimeError(f"Seitentitel fehlt: {path.relative_to(ROOT)}")

    if not description:
        if path.name == "404.html":
            description = "Die angeforderte Seite wurde nicht gefunden."
        else:
            description = f"Informationen der TTF Laudenbach: {title}."

    canonical = canonical or canonical_for(path)
    noindex = (
        "noindex" in robots
        or path.name == "404.html"
        or path.name == "maintenance.html"
    )
    return title, description, canonical, noindex


def build_head(
    title: str,
    description: str,
    canonical: str,
    noindex: bool,
) -> str:
    lines = [
        "<head>",
        "    <!-- Technische Grundeinstellungen -->",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "",
        "    <!-- Angaben für Browser und Suchmaschinen -->",
        f"    <title>{html.escape(title)}</title>",
        (
            '    <meta name="description" '
            f'content="{html.escape(description, quote=True)}">'
        ),
        (
            '    <link rel="canonical" '
            f'href="{html.escape(canonical, quote=True)}">'
        ),
    ]

    if noindex:
        lines.append('    <meta name="robots" content="noindex, follow">')

    lines.extend(
        [
            "",
            "    <!-- Gemeinsame Gestaltung -->",
            '    <link rel="stylesheet" href="/assets/css/site.bundle.css">',
            "</head>",
        ]
    )
    return "\n".join(lines)


def remove_generated_component(
    text: str,
    start: str,
    end: str,
) -> str:
    pattern = re.compile(
        rf"\s*{re.escape(start)}.*?{re.escape(end)}\s*",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub("", text)


def add_container_comments(text: str) -> str:
    header_pattern = re.compile(
        r'(?<!Navigation wird automatisch geladen -->\s)'
        r'<div\s+id=["\']header-container["\']\s*>\s*</div>',
        re.IGNORECASE,
    )
    footer_pattern = re.compile(
        r'(?<!Footer wird automatisch geladen -->\s)'
        r'<div\s+id=["\']footer-container["\']\s*>\s*</div>',
        re.IGNORECASE,
    )

    text = header_pattern.sub(
        "<!-- Gemeinsame Navigation wird automatisch geladen. -->\n"
        '<div id="header-container"></div>',
        text,
    )
    text = footer_pattern.sub(
        "<!-- Gemeinsamer Footer wird automatisch geladen. -->\n"
        '<div id="footer-container"></div>',
        text,
    )
    return text


def simplify_pages() -> None:
    head_pattern = re.compile(
        r"<head\b[^>]*>.*?</head>",
        re.IGNORECASE | re.DOTALL,
    )

    for path in pages():
        original = path.read_text(encoding="utf-8")
        title, description, canonical, noindex = extract_page_data(
            path,
            original,
        )

        if not head_pattern.search(original):
            raise RuntimeError(
                f"Kein vollständiger <head> in {path.relative_to(ROOT)}"
            )

        updated = head_pattern.sub(
            build_head(title, description, canonical, noindex),
            original,
            count=1,
        )
        updated = remove_generated_component(
            updated,
            HEADER_START,
            HEADER_END,
        )
        updated = remove_generated_component(
            updated,
            FOOTER_START,
            FOOTER_END,
        )
        updated = add_container_comments(updated)

        path.write_text(updated, encoding="utf-8")


def enable_runtime_components() -> None:
    path = ROOT / "assets/js/main.js"
    text = path.read_text(encoding="utf-8")

    import_line = 'import { loadComponent } from "./core/components.js";'
    if import_line not in text:
        text = import_line + "\n" + text

    marker = "// Gemeinsame Seitenelemente laden"
    if marker not in text:
        pattern = re.compile(
            r"(async function initializePage\(\)\s*\{\s*)",
            re.MULTILINE,
        )
        insertion = """\\1    // Gemeinsame Seitenelemente laden
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

"""
        text, count = pattern.subn(insertion, text, count=1)
        if count != 1:
            raise RuntimeError(
                "initializePage() konnte in assets/js/main.js "
                "nicht erweitert werden."
            )

    path.write_text(text, encoding="utf-8")


def stop_html_generation() -> None:
    build_site = ROOT / "tools/site-build/build_site.py"
    text = build_site.read_text(encoding="utf-8")

    pattern = re.compile(
        r'SCRIPTS\s*=\s*\[\s*'
        r'["\']build_components\.py["\']\s*,\s*'
        r'["\']build_css\.py["\']\s*,\s*'
        r'["\']generate_sitemap\.py["\']\s*'
        r'\]',
        re.MULTILINE,
    )
    replacement = 'SCRIPTS = ["build_css.py", "generate_sitemap.py"]'
    text, count = pattern.subn(replacement, text, count=1)

    if count == 0 and "build_components.py" in text:
        raise RuntimeError(
            "Die Komponenten-Erzeugung konnte in build_site.py "
            "nicht entfernt werden."
        )

    build_site.write_text(text, encoding="utf-8")
    (ROOT / "tools/site-build/build_components.py").unlink(missing_ok=True)


def update_browser_test() -> None:
    path = ROOT / "tests/e2e/site-smoke.spec.mjs"
    text = path.read_text(encoding="utf-8")

    if 'test("Hauptinhalt bleibt auch ohne JavaScript lesbar"' in text:
        return

    pattern = re.compile(
        r'test\("Header und Footer sind auch ohne JavaScript vorhanden",'
        r".*?^\}\);",
        re.MULTILINE | re.DOTALL,
    )
    replacement = """test("Hauptinhalt bleibt auch ohne JavaScript lesbar", async ({ browser }) => {
    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();

    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.locator("main#main-content")).toBeVisible();
    await expect(page.locator("main#main-content h1")).toBeVisible();

    await context.close();
});"""

    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(
            "Der bisherige No-JavaScript-Test wurde nicht gefunden."
        )

    path.write_text(text, encoding="utf-8")


def remove_obsolete_migrations() -> None:
    for relative in [
        "tools/apply_phase3_seo.py",
        "tools/check_phase3_seo.py",
        ".github/workflows/apply-repository-simplification.yml",
    ]:
        (ROOT / relative).unlink(missing_ok=True)

    shutil.rmtree(
        ROOT / "tools/repository-simplification",
        ignore_errors=True,
    )


def write_editor_config() -> None:
    path = ROOT / ".editorconfig"
    path.write_text(
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


def remove_self() -> None:
    workflow = ROOT / ".github/workflows/apply-html-readability.yml"
    workflow.unlink(missing_ok=True)
    shutil.rmtree(SCRIPT_DIR, ignore_errors=True)


def main() -> int:
    require_repository()
    simplify_pages()
    enable_runtime_components()
    stop_html_generation()
    update_browser_test()
    remove_obsolete_migrations()
    write_editor_config()
    remove_self()

    print("HTML-Dateien wurden vereinfacht.")
    print("- wenige, verständliche Meta-Angaben")
    print("- Header und Footer nur noch in components/")
    print("- automatische Einbettung in jede HTML-Datei beendet")
    print("- einheitliche Formatierung wird anschließend angewendet")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        raise
