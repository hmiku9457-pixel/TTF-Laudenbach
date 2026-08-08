#!/usr/bin/env python3
"""Einmalige Bereinigung der TTF-Laudenbach-Repositorystruktur."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
PAYLOAD = SCRIPT_DIR / "payload"

WORKFLOWS_TO_REMOVE = [
    ".github/workflows/apply-design-final.yml",
    ".github/workflows/apply-table-header-fix.yml",
    ".github/workflows/apply-ui-polish.yml",
    ".github/workflows/apply-ui-update.yml",
    ".github/workflows/apply-site-modernization.yml",
    ".github/workflows/site-build.yml",
    ".github/workflows/site-browser-quality.yml",
    ".github/workflows/site-quality-manual.yml",
]

TOOLS_TO_REMOVE = [
    "tools/design-final",
    "tools/review-upgrade",
    "tools/table-header-fix",
    "tools/ui-polish",
    "tools/ui-update",
    "tools/site-modernization",
    "tools/site-build",
    "tools/quality",
    "tools/apply_phase3_seo.py",
    "tools/apply_phase4_step2.py",
    "tools/check_phase3_seo.py",
]

CSS_MERGES = [
    (
        "assets/css/consolidated/navigation.css",
        "assets/css/layout/header-navigation.css",
        "navigation",
    ),
    (
        "assets/css/consolidated/contact.css",
        "assets/css/components/contact-form.css",
        "contact",
    ),
    (
        "assets/css/consolidated/news.css",
        "assets/css/components/news-slider.css",
        "news",
    ),
    (
        "assets/css/consolidated/gallery.css",
        "assets/css/components/gallery.css",
        "gallery",
    ),
    (
        "assets/css/consolidated/tables.css",
        "assets/css/components/tables.css",
        "tables",
    ),
]

OLD_CORRECTION_FILES = [
    "assets/css/components/ui-fixes.css",
    "assets/css/components/ui-polish.css",
    "assets/css/components/ui-final.css",
    "assets/css/components/table-header-fix.css",
]

MAIN_CSS = """/*
 * Zentraler Einstiegspunkt für die Website-Gestaltung.
 * Die Produktionsdatei site.bundle.css wird daraus automatisch erzeugt.
 */
@import url("./base/reset.css");
@import url("./base/theme.css");
@import url("./layout/header-navigation.css");
@import url("./layout/grid-boxes.css");
@import url("./components/page-content.css");
@import url("./components/animations.css");
@import url("./components/news-slider.css");
@import url("./components/teams.css");
@import url("./components/tables.css");
@import url("./components/ui-buttons.css");
@import url("./components/maps-consent.css");
@import url("./layout/footer.css");
@import url("./components/contact-form.css");
@import url("./responsive.css");
@import url("./components/gallery.css");
@import url("./components/robustness.css");
@import url("./components/accessibility.css");
"""


def require_repository() -> None:
    required = [
        "index.html",
        "components/header.html",
        "components/footer.html",
        "assets/css/main.css",
        "assets/js/main.js",
    ]
    missing = [
        item for item in required if not (ROOT / item).exists()
    ]
    if missing:
        raise RuntimeError(
            "Kein vollständiges TTF-Laudenbach-Repository. Fehlend: "
            + ", ".join(missing)
        )


def copy_payload() -> None:
    for source in PAYLOAD.rglob("*"):
        if source.is_dir():
            continue
        relative = source.relative_to(PAYLOAD)
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def clean_css_source(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("/* Konsolidierte "):
            continue
        if stripped.startswith("/* Quelle: "):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def replace_integrated_block(
    target_text: str,
    content: str,
    name: str,
) -> str:
    start = f"/* TTF:INTEGRATED:{name}:START */"
    end = f"/* TTF:INTEGRATED:{name}:END */"
    block = f"{start}\n{content.rstrip()}\n{end}"

    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    if pattern.search(target_text):
        return pattern.sub(block, target_text)

    return target_text.rstrip() + "\n\n" + block + "\n"


def integrate_css() -> None:
    foundation_source = ROOT / "assets/css/consolidated/foundation.css"
    page_content = ROOT / "assets/css/components/page-content.css"

    if foundation_source.exists():
        content = clean_css_source(
            foundation_source.read_text(encoding="utf-8")
        )
        page_content.write_text(
            "/* Seitenüberschriften, Seiteneinstieg und allgemeine "
            "Inhaltsregeln. */\n\n"
            + content,
            encoding="utf-8",
        )
    elif not page_content.exists():
        raise RuntimeError(
            "Weder foundation.css noch page-content.css vorhanden."
        )

    for source_name, target_name, marker in CSS_MERGES:
        source = ROOT / source_name
        target = ROOT / target_name

        if not source.exists():
            # Wiederholungslauf oder bereits manuell integrierter Stand.
            target_text = (
                target.read_text(encoding="utf-8")
                if target.exists()
                else ""
            )
            if f"/* TTF:INTEGRATED:{marker}:START */" in target_text:
                continue
            raise RuntimeError(
                f"CSS-Quelle fehlt und ist nicht integriert: {source_name}"
            )

        content = clean_css_source(
            source.read_text(encoding="utf-8")
        )
        target_text = (
            target.read_text(encoding="utf-8")
            if target.exists()
            else ""
        )
        target.write_text(
            replace_integrated_block(target_text, content, marker),
            encoding="utf-8",
        )

    (ROOT / "assets/css/main.css").write_text(
        MAIN_CSS,
        encoding="utf-8",
    )

    shutil.rmtree(
        ROOT / "assets/css/consolidated",
        ignore_errors=True,
    )
    for relative in OLD_CORRECTION_FILES:
        (ROOT / relative).unlink(missing_ok=True)


def remove_obsolete_paths() -> None:
    for relative in WORKFLOWS_TO_REMOVE + TOOLS_TO_REMOVE:
        path = ROOT / relative
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)


def remove_python_cache() -> None:
    for cache in sorted(
        ROOT.rglob("__pycache__"),
        reverse=True,
    ):
        if cache.is_dir():
            shutil.rmtree(cache, ignore_errors=True)
    for file in ROOT.rglob("*.pyc"):
        file.unlink(missing_ok=True)


def remove_self() -> None:
    # Die laufende Python-Datei kann unter Linux gelöscht werden.
    workflow = (
        ROOT
        / ".github/workflows/apply-repository-simplification.yml"
    )
    workflow.unlink(missing_ok=True)
    shutil.rmtree(SCRIPT_DIR, ignore_errors=True)


def main() -> int:
    require_repository()
    copy_payload()
    integrate_css()
    remove_obsolete_paths()
    remove_python_cache()
    remove_self()

    print("Repositorystruktur erfolgreich vereinfacht.")
    print("Dauerhaft bleiben:")
    print("- .github/workflows/website.yml")
    print("- .github/workflows/generate-gallery-json.yml")
    print("- .github/workflows/scraper.yml")
    print("- tools/site/build.py")
    print("- tools/site/check.py")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        raise
