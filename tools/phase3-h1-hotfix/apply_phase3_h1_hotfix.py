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

# H1–H3 entsprechen den Überschriftsebenen des Pages-CMS-Rich-Text-Editors.
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

# Pages CMS kann Inline-Bilder als ![](/pfad/bild.jpg) speichern.
# Ein leerer Alt-Text ist für dekorative Inline-Bilder gültig.
# Der Pfad wird weiterhin strikt validiert.
replace_once(
    generator,
    "        if not alt:\n"
    '            raise ValueError(f"{source.name}: Bilder im Artikel benötigen einen Alt-Text.")\n'
    "        validate_image_path(path, source)",
    "        # Pages CMS kann Inline-Bilder ohne Alt-Text serialisieren.\n"
    "        # alt=\"\" ist für dekorative Bilder gültig; der Bildpfad bleibt Pflicht und wird validiert.\n"
    "        validate_image_path(path, source)",
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
replace_once(
    docs,
    "Bilder im Artikel benötigen einen nicht-leeren Alt-Text.",
    "Das Titelbild benötigt weiterhin das Pflichtfeld `image_alt`. Inline-Bilder können einen Alt-Text besitzen; Pages CMS kann sie jedoch auch mit leerem `alt=\"\"` speichern. Solche Inline-Bilder werden als dekorativ behandelt.",
)

print("Phase-3-Editor-Hotfix angewendet.")
