#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER_START = "<!-- TTF:HEADER:START -->"
HEADER_END = "<!-- TTF:HEADER:END -->"
FOOTER_START = "<!-- TTF:FOOTER:START -->"
FOOTER_END = "<!-- TTF:FOOTER:END -->"


def component_block(component: str, start: str, end: str) -> str:
    return f'{start}\n{component.strip()}\n{end}'


def replace_container(text: str, element_id: str, block: str, start: str, end: str) -> tuple[str, bool]:
    marker_pattern = re.compile(
        rf'(<div\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>)(.*?{re.escape(start)}.*?{re.escape(end)}.*?)(</div>)',
        re.IGNORECASE | re.DOTALL,
    )
    match = marker_pattern.search(text)
    if match:
        return text[:match.start()] + match.group(1) + "\n" + block + "\n" + match.group(3) + text[match.end():], True

    empty_pattern = re.compile(
        rf'<div\b[^>]*\bid=["\']{re.escape(element_id)}["\'][^>]*>\s*</div>',
        re.IGNORECASE | re.DOTALL,
    )
    replacement = f'<div id="{element_id}">\n{block}\n</div>'
    updated, count = empty_pattern.subn(replacement, text, count=1)
    return updated, bool(count)


def iter_pages() -> list[Path]:
    pages = [ROOT / "index.html", ROOT / "404.html"]
    pages.extend(sorted((ROOT / "pages").rglob("*.html")))
    return [p for p in pages if p.exists()]


def build(write: bool) -> int:
    header = (ROOT / "components/header.html").read_text(encoding="utf-8")
    footer = (ROOT / "components/footer.html").read_text(encoding="utf-8")
    changed: list[Path] = []
    for page in iter_pages():
        original = page.read_text(encoding="utf-8")
        updated, header_found = replace_container(
            original, "header-container", component_block(header, HEADER_START, HEADER_END), HEADER_START, HEADER_END
        )
        updated, footer_found = replace_container(
            updated, "footer-container", component_block(footer, FOOTER_START, FOOTER_END), FOOTER_START, FOOTER_END
        )
        if not header_found and page.name != "maintenance.html":
            print(f"WARNUNG: Kein Header-Platzhalter in {page.relative_to(ROOT)}")
        if not footer_found and page.name != "maintenance.html":
            print(f"WARNUNG: Kein Footer-Platzhalter in {page.relative_to(ROOT)}")
        if updated != original:
            changed.append(page)
            if write:
                page.write_text(updated, encoding="utf-8")
    if changed and not write:
        print("Nicht erzeugte Komponenten in:")
        for page in changed:
            print(f"- {page.relative_to(ROOT)}")
        return 1
    print(f"Komponenten geprüft: {len(iter_pages())} Seiten, Änderungen: {len(changed)}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raise SystemExit(build(args.write))
