#!/usr/bin/env python3
"""Vereinfacht und formatiert die HTML-Dateien der Vereinswebsite."""
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
PAYLOAD = SCRIPT_DIR / "payload"
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
        "tools/site/check.py",
        "tests/e2e/site-smoke.spec.mjs",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise RuntimeError(
            "Der vereinfachte Architekturstand wurde nicht gefunden. Fehlend: "
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
        "meta", attrs={"name": re.compile(r"^description$", re.IGNORECASE)}
    )
    description = str(description_tag.get("content", "")).strip() if description_tag else ""
    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical = str(canonical_tag.get("href", "")).strip() if canonical_tag else ""
    robots_tag = soup.find(
        "meta", attrs={"name": re.compile(r"^robots$", re.IGNORECASE)}
    )
    robots = str(robots_tag.get("content", "")).lower() if robots_tag else ""

    if not title:
        if path.name == "404.html":
            title = "Seite nicht gefunden | TTF Laudenbach"
        else:
            raise RuntimeError(f"Seitentitel fehlt: {path.relative_to(ROOT)}")
    if not description:
        description = (
            "Die angeforderte Seite wurde nicht gefunden."
            if path.name == "404.html"
            else f"Informationen der TTF Laudenbach: {title}."
        )

    canonical = canonical or canonical_for(path)
    noindex = "noindex" in robots or path.name in {"404.html", "maintenance.html"}
    return title, description, canonical, noindex


def build_head(title: str, description: str, canonical: str, noindex: bool) -> str:
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
    lines.extend(
        [
            "",
            "    <!-- Gemeinsame Gestaltung -->",
            '    <link rel="stylesheet" href="/assets/css/site.bundle.css">',
            "</head>",
        ]
    )
    return "\n".join(lines)


def remove_generated_component(text: str, start: str, end: str) -> str:
    pattern = re.compile(
        rf"\s*{re.escape(start)}.*?{re.escape(end)}\s*", re.IGNORECASE | re.DOTALL
    )
    return pattern.sub("", text)


def add_container_comments(text: str) -> str:
    header_pattern = re.compile(
        r'<div\s+id=["\']header-container["\']\s*>\s*</div>', re.IGNORECASE
    )
    footer_pattern = re.compile(
        r'<div\s+id=["\']footer-container["\']\s*>\s*</div>', re.IGNORECASE
    )
    text = header_pattern.sub(
        "<!-- Gemeinsame Navigation wird automatisch geladen. -->\n"
        '<div id="header-container"></div>',
        text,
        count=1,
    )
    text = footer_pattern.sub(
        "<!-- Gemeinsamer Footer wird automatisch geladen. -->\n"
        '<div id="footer-container"></div>',
        text,
        count=1,
    )
    return text


def simplify_pages() -> None:
    head_pattern = re.compile(r"<head\b[^>]*>.*?</head>", re.IGNORECASE | re.DOTALL)
    for path in pages():
        original = path.read_text(encoding="utf-8")
        title, description, canonical, noindex = extract_page_data(path, original)
        if not head_pattern.search(original):
            raise RuntimeError(f"Kein vollständiger <head> in {path.relative_to(ROOT)}")
        updated = head_pattern.sub(
            build_head(title, description, canonical, noindex), original, count=1
        )
        updated = remove_generated_component(updated, HEADER_START, HEADER_END)
        updated = remove_generated_component(updated, FOOTER_START, FOOTER_END)
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
        pattern = re.compile(r"(async function initializePage\(\)\s*\{\s*)", re.MULTILINE)

        def insertion(match: re.Match[str]) -> str:
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

        text, count = pattern.subn(insertion, text, count=1)
        if count != 1:
            raise RuntimeError("initializePage() konnte nicht erweitert werden.")
    path.write_text(text, encoding="utf-8")


def install_simple_build() -> None:
    source = PAYLOAD / "tools/site/build.py"
    target = ROOT / "tools/site/build.py"
    if not source.is_file():
        raise RuntimeError("Der vereinfachte Build fehlt im Paket.")
    shutil.copy2(source, target)


def update_browser_test() -> None:
    path = ROOT / "tests/e2e/site-smoke.spec.mjs"
    text = path.read_text(encoding="utf-8")
    if 'test("Hauptinhalt bleibt auch ohne JavaScript lesbar"' in text:
        return
    pattern = re.compile(
        r'test\("Header und Footer sind auch ohne JavaScript vorhanden",.*?^\}\);',
        re.MULTILINE | re.DOTALL,
    )
    replacement = '''test("Hauptinhalt bleibt auch ohne JavaScript lesbar", async ({ browser }) => {
    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();

    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.locator("main#main-content")).toBeVisible();
    await expect(page.locator("main#main-content h1")).toBeVisible();

    await context.close();
});'''
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Der bisherige No-JavaScript-Test wurde nicht gefunden.")
    path.write_text(text, encoding="utf-8")


def update_permanent_workflow_text() -> None:
    path = ROOT / ".github/workflows/website.yml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "Header, Footer, CSS-Bundle und Sitemap aktualisieren",
        "CSS-Bundle und Sitemap aktualisieren",
    )
    path.write_text(text, encoding="utf-8")


def write_editor_config() -> None:
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


def remove_obsolete_files() -> None:
    for relative in [
        "tools/apply_phase3_seo.py",
        "tools/check_phase3_seo.py",
        ".github/workflows/apply-repository-simplification.yml",
    ]:
        (ROOT / relative).unlink(missing_ok=True)
    shutil.rmtree(ROOT / "tools/repository-simplification", ignore_errors=True)


def remove_self() -> None:
    (ROOT / ".github/workflows/apply-html-readability.yml").unlink(missing_ok=True)
    shutil.rmtree(SCRIPT_DIR, ignore_errors=True)


def main() -> int:
    require_repository()
    simplify_pages()
    enable_runtime_components()
    install_simple_build()
    update_browser_test()
    update_permanent_workflow_text()
    write_editor_config()
    remove_obsolete_files()
    remove_self()
    print("HTML-Dateien wurden vereinfacht und formatiert.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        raise
