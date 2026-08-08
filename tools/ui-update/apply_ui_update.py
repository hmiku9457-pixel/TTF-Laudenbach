from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).with_name("payload.zip")
MAIN_CSS = ROOT / "assets/css/main.css"
BUNDLE_CSS = ROOT / "assets/css/site.bundle.css"
UI_IMPORT = '@import url("./components/ui-fixes.css");'


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise RuntimeError(f"Unsicherer Pfad im Payload: {member.filename}")
        archive.extractall(destination)


def ensure_ui_import() -> None:
    content = MAIN_CSS.read_text(encoding="utf-8")
    lines = [line for line in content.splitlines() if line.strip() != UI_IMPORT]
    while lines and not lines[-1].strip():
        lines.pop()
    lines.extend([UI_IMPORT, ""])
    MAIN_CSS.write_text("\n".join(lines), encoding="utf-8")


def patch_club_page() -> None:
    path = ROOT / "pages/unserVerein.html"
    content = path.read_text(encoding="utf-8")

    # Repariert den älteren fehlerhaften Klassenwert, falls er noch vorhanden ist.
    content = content.replace("<div class='column\"'>", '<div class="column">')
    content = content.replace('<div class="column\"">', '<div class="column">')

    caption = '<caption class="visually-hidden">Ehrenvorsitzender &amp; Ehrenmitglieder</caption>'
    pattern = re.compile(r'<table(?:\s+class="([^"]*)")?>\s*' + re.escape(caption))

    def add_class(match: re.Match[str]) -> str:
        classes = (match.group(1) or "").split()
        if "table--emphasis-first-column" not in classes:
            classes.append("table--emphasis-first-column")
        return f'<table class="{" ".join(classes)}">{caption}'

    content, replacements = pattern.subn(add_class, content, count=1)
    if replacements != 1 and "table--emphasis-first-column" not in content:
        raise RuntimeError("Tabelle 'Ehrenvorsitzender & Ehrenmitglieder' wurde nicht gefunden.")

    path.write_text(content, encoding="utf-8")


def resolve_css(path: Path, stack: tuple[Path, ...] = ()) -> str:
    resolved = path.resolve()
    if resolved in stack:
        chain = " -> ".join(item.name for item in (*stack, resolved))
        raise RuntimeError(f"Zyklischer CSS-Import: {chain}")

    text = path.read_text(encoding="utf-8")
    output: list[str] = [f"/* Quelle: {path.relative_to(ROOT).as_posix()} */"]
    import_pattern = re.compile(
        r'^\s*@import\s+url\(["\'](?P<target>[^"\']+)["\']\)\s*;\s*$',
        re.MULTILINE,
    )

    position = 0
    for match in import_pattern.finditer(text):
        output.append(text[position:match.start()].rstrip())
        target = match.group("target")
        if target.startswith(("http://", "https://")):
            output.append(match.group(0))
        else:
            imported = (path.parent / target).resolve()
            if not imported.is_file():
                raise FileNotFoundError(f"CSS-Import fehlt: {imported}")
            output.append(resolve_css(imported, (*stack, resolved)).rstrip())
        position = match.end()

    output.append(text[position:].strip())
    return "\n".join(part for part in output if part).strip() + "\n"


def build_bundle() -> None:
    bundled = "/* Automatisch aus assets/css/main.css erzeugt. Nicht direkt bearbeiten. */\n"
    bundled += resolve_css(MAIN_CSS)
    BUNDLE_CSS.write_text(bundled, encoding="utf-8")


def main() -> None:
    if not PAYLOAD.is_file():
        raise FileNotFoundError(f"Payload fehlt: {PAYLOAD}")

    safe_extract(PAYLOAD, ROOT)
    ensure_ui_import()
    patch_club_page()
    build_bundle()
    print("UI-Update wurde angewendet und site.bundle.css neu erzeugt.")


if __name__ == "__main__":
    main()
