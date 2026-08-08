#!/usr/bin/env python3
from __future__ import annotations
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
PAYLOAD = SCRIPT_DIR / "payload"

OLD_CSS = [
    "./components/ui-fixes.css",
    "./components/ui-polish.css",
    "./components/ui-final.css",
    "./components/table-header-fix.css",
]
NEW_CSS = [
    "./consolidated/foundation.css",
    "./consolidated/navigation.css",
    "./consolidated/contact.css",
    "./consolidated/news.css",
    "./consolidated/gallery.css",
    "./consolidated/tables.css",
]


def require_repo() -> None:
    required = ["index.html", "components/header.html", "components/footer.html", "assets/css/main.css", "assets/js/main.js"]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise RuntimeError("Das Skript muss im TTF-Laudenbach-Repository laufen. Fehlend: " + ", ".join(missing))


def copy_payload() -> None:
    for source in PAYLOAD.rglob("*"):
        if source.is_dir():
            continue
        relative = source.relative_to(PAYLOAD)
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def update_css_entry() -> None:
    path = ROOT / "assets/css/main.css"
    text = path.read_text(encoding="utf-8")
    for import_path in OLD_CSS:
        text = re.sub(rf'^\s*@import\s+url\(["\']{re.escape(import_path)}["\']\)\s*;\s*\n?', "", text, flags=re.M)
    for import_path in NEW_CSS:
        text = re.sub(rf'^\s*@import\s+url\(["\']{re.escape(import_path)}["\']\)\s*;\s*\n?', "", text, flags=re.M)
    anchor = '@import url("./components/accessibility.css");'
    additions = "\n".join(f'@import url("{item}");' for item in NEW_CSS)
    if anchor not in text:
        raise RuntimeError("Erwarteter Accessibility-Import in assets/css/main.css fehlt.")
    text = text.replace(anchor, anchor + "\n" + additions)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    for name in ["ui-fixes.css", "ui-polish.css", "ui-final.css", "table-header-fix.css"]:
        (ROOT / "assets/css/components" / name).unlink(missing_ok=True)


def update_home_grid() -> None:
    path = ROOT / "assets/css/layout/grid-boxes.css"
    text = path.read_text(encoding="utf-8")
    text, first = re.subn(
        r'(\.grid-home-firstLine\s*\{.*?grid-template-columns:)\s*[^;]+;',
        r'\1 minmax(18rem, 0.9fr) minmax(34rem, 1.35fr);', text, count=1, flags=re.S
    )
    text, second = re.subn(
        r'(\.grid-home-secondLine\s*\{.*?grid-template-columns:)\s*[^;]+;',
        r'\1 minmax(28rem, 1.35fr) minmax(20rem, 0.85fr);', text, count=1, flags=re.S
    )
    if not first or not second:
        raise RuntimeError("Die Startseitenraster konnten nicht eindeutig aktualisiert werden.")
    text = re.sub(
        r'/\* Hover-Effekt \*/\s*\.box:hover,\s*\.team-box:hover\s*\{.*?\}',
        '/* Reine Inhaltsboxen bleiben ruhig; Interaktion wird nur an Links und Buttons signalisiert. */\n.box:hover,\n.team-box:hover {\n    transform: none;\n    box-shadow: var(--shadow-light);\n}',
        text, count=1, flags=re.S
    )
    marker = "/* TTF: fließender Startseiten-Breakpoint */"
    if marker not in text:
        text += f'''\n\n{marker}\n@media (max-width: 1180px) {{\n    .grid-home-firstLine,\n    .grid-home-secondLine {{\n        grid-template-columns: minmax(0, 1fr);\n    }}\n}}\n'''
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def title_for_page(text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", text, flags=re.I | re.S)
    title = re.sub(r"\s+", " ", match.group(1)).strip() if match else "TTF Laudenbach"
    title = re.sub(r"\s*[|–-]\s*TTF Laudenbach\s*$", "", title, flags=re.I).strip()
    return title or "TTF Laudenbach"


def normalize_headings() -> None:
    pages = [ROOT / "index.html", ROOT / "404.html", *sorted((ROOT / "pages").rglob("*.html"))]
    for path in pages:
        if not path.exists() or path.name == "maintenance.html":
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r'(<h1\b[^>]*class=["\'][^"\']*)\bvisually-hidden\s*([^"\']*["\'][^>]*>)',
            lambda m: m.group(1) + m.group(2), text, flags=re.I
        )
        main_match = re.search(r"(<main\b[^>]*>)(.*?)(</main>)", text, flags=re.I | re.S)
        if not main_match:
            continue
        main_content = main_match.group(2)
        h1_count = len(re.findall(r"<h1\b", main_content, flags=re.I))
        if h1_count == 0:
            heading = title_for_page(text)
            main_content = f'\n<h1 class="page-heading">{heading}</h1>' + main_content
        elif h1_count > 1:
            raise RuntimeError(f"Mehr als eine H1 in {path.relative_to(ROOT)}")
        text = text[:main_match.start(2)] + main_content + text[main_match.end(2):]
        path.write_text(text, encoding="utf-8")


def update_home_intro() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    hero = '''<section class="home-intro" aria-labelledby="home-heading">
    <h1 id="home-heading" class="page-heading">Tischtennis bei den TTF Laudenbach</h1>
    <p class="home-intro__lead">Training, Mannschaftssport und Vereinsleben für Jugendliche und Erwachsene in Laudenbach und Weikersheim.</p>
    <div class="home-intro__actions">
        <a class="button" href="#trainingszeiten">Trainingszeiten ansehen</a>
        <a class="button" href="#contactForm">Probetraining anfragen</a>
    </div>
</section>'''
    hidden = re.compile(r'<h1\b[^>]*class=["\'][^"\']*(?:visually-hidden|page-heading)[^"\']*["\'][^>]*>.*?</h1>', re.I | re.S)
    if 'class="home-intro"' not in text:
        text, count = hidden.subn(hero, text, count=1)
        if not count:
            main = re.search(r"<main\b[^>]*>", text, re.I)
            if not main:
                raise RuntimeError("Kein main-Element auf der Startseite gefunden.")
            text = text[:main.end()] + "\n" + hero + text[main.end():]
    if not re.search(r'id=["\']trainingszeiten["\']', text, re.I):
        text = re.sub(r'(<h[23]\b[^>]*)(>\s*Trainingszeiten\s*</h[23]>)', r'\1 id="trainingszeiten"\2', text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")


def validate_headings() -> None:
    errors = []
    for path in [ROOT / "index.html", *sorted((ROOT / "pages").rglob("*.html"))]:
        if path.name == "maintenance.html":
            continue
        text = path.read_text(encoding="utf-8")
        main = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.I | re.S)
        if not main:
            continue
        count = len(re.findall(r"<h1\b", main.group(1), re.I))
        if count != 1:
            errors.append(f"{path.relative_to(ROOT)}: {count} H1 im main")
        header_blocks = re.findall(r"<header\b[^>]*>(.*?)</header>", text, re.I | re.S)
        if any(re.search(r"<h1\b", block, re.I) for block in header_blocks):
            errors.append(f"{path.relative_to(ROOT)}: H1 im Header")
    if errors:
        raise RuntimeError("Überschriftenprüfung fehlgeschlagen:\n" + "\n".join(errors))


def run_build() -> None:
    subprocess.run([sys.executable, "tools/site-build/build_site.py", "--write"], cwd=ROOT, check=True)


def main() -> int:
    require_repo()
    copy_payload()
    update_css_entry()
    update_home_grid()
    normalize_headings()
    update_home_intro()
    run_build()
    validate_headings()
    print("Architektur-Update erfolgreich angewendet.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        raise
