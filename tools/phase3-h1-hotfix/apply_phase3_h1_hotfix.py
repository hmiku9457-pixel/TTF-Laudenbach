#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"{path}: erwarteter Text nicht gefunden:\n{old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

generator = ROOT / "assets/python/generate_news.py"
replace_once(
    generator,
    '"p", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "img",',
    '"p", "h1", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "img",',
)
replace_once(
    generator,
    "        if level not in {2, 3}:\n"
    "            raise ValueError(\n"
    '                f"{source.name}: nur H2 und H3 sind im Artikeltext erlaubt; gefunden: H{level}."\n'
    "            )",
    "        if level not in {1, 2, 3}:\n"
    "            raise ValueError(\n"
    '                f"{source.name}: nur H1, H2 und H3 sind im Artikeltext erlaubt; gefunden: H{level}."\n'
    "            )",
)

css = ROOT / "assets/css/components/news-content.css"
replace_once(
    css,
    ".news-article__content h2,\n"
    ".news-article__content h3 {",
    ".news-article__content h1,\n"
    ".news-article__content h2,\n"
    ".news-article__content h3 {",
)

pages = ROOT / ".pages.yml"
replace_once(
    pages,
    'description: "Artikeltext. Für Zwischenüberschriften H2 oder H3 verwenden; keine zusätzliche H1."',
    'description: "Artikeltext. Als Überschriften können H1, H2 und H3 verwendet werden."',
)

docs = ROOT / "docs/news-content-format.md"
replace_once(docs, "* H2 und H3", "* H1, H2 und H3")
replace_once(
    docs,
    "Eine zusätzliche H1 ist nicht erlaubt, weil der Artikeltitel bereits die H1 der Seite ist.\n"
    "Rohes HTML ist nicht erlaubt.",
    "H1, H2 und H3 sind im Artikeltext erlaubt. Der Seitentitel bleibt unabhängig davon die Hauptüberschrift des News-Artikels.\n"
    "Rohes HTML ist nicht erlaubt.",
)

print("Phase-3-H1-Hotfix angewendet.")
