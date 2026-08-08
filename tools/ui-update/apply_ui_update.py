from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).with_name("payload.zip")
MAIN_CSS = ROOT / "assets/css/main.css"
UI_IMPORT = '@import url("./components/ui-fixes.css");'
CSS_BUILDER = ROOT / "tools/review-upgrade/build_css.py"


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()

    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()

            if (
                target != destination_resolved
                and destination_resolved not in target.parents
            ):
                raise RuntimeError(
                    f"Unsicherer Pfad im Payload: {member.filename}"
                )

        archive.extractall(destination)


def ensure_ui_import() -> None:
    content = MAIN_CSS.read_text(encoding="utf-8")
    lines = [
        line
        for line in content.splitlines()
        if line.strip() != UI_IMPORT
    ]

    while lines and not lines[-1].strip():
        lines.pop()

    lines.extend([UI_IMPORT, ""])
    MAIN_CSS.write_text("\n".join(lines), encoding="utf-8")


def patch_club_page() -> None:
    path = ROOT / "pages/unserVerein.html"
    content = path.read_text(encoding="utf-8")

    # Repariert ältere fehlerhafte Klassenwerte, falls noch vorhanden.
    content = content.replace(
        "<div class='column\"'>",
        '<div class="column">',
    )
    content = content.replace(
        '<div class="column\"">',
        '<div class="column">',
    )

    caption = (
        '<caption class="visually-hidden">'
        "Ehrenvorsitzender &amp; Ehrenmitglieder"
        "</caption>"
    )
    pattern = re.compile(
        r'<table(?:\s+class="([^"]*)")?>\s*'
        + re.escape(caption)
    )

    def add_class(match: re.Match[str]) -> str:
        classes = (match.group(1) or "").split()

        if "table--emphasis-first-column" not in classes:
            classes.append("table--emphasis-first-column")

        return (
            f'<table class="{" ".join(classes)}">'
            f"{caption}"
        )

    content, replacements = pattern.subn(
        add_class,
        content,
        count=1,
    )

    if (
        replacements != 1
        and "table--emphasis-first-column" not in content
    ):
        raise RuntimeError(
            "Tabelle 'Ehrenvorsitzender & Ehrenmitglieder' "
            "wurde nicht gefunden."
        )

    path.write_text(content, encoding="utf-8")


def build_bundle() -> None:
    if not CSS_BUILDER.is_file():
        raise FileNotFoundError(
            f"Zentraler CSS-Builder fehlt: {CSS_BUILDER}"
        )

    subprocess.run(
        [sys.executable, str(CSS_BUILDER)],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    if not PAYLOAD.is_file():
        raise FileNotFoundError(f"Payload fehlt: {PAYLOAD}")

    safe_extract(PAYLOAD, ROOT)
    ensure_ui_import()
    patch_club_page()
    build_bundle()

    print(
        "UI-Update wurde angewendet und site.bundle.css "
        "mit dem zentralen Builder neu erzeugt."
    )


if __name__ == "__main__":
    main()
