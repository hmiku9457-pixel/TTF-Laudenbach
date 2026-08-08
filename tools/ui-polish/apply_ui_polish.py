from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).with_name("payload.zip")
MAIN_CSS = ROOT / "assets/css/main.css"
CSS_BUILDER = ROOT / "tools/review-upgrade/build_css.py"
POLISH_IMPORT = '@import url("./components/ui-polish.css");'


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


def ensure_css_import() -> None:
    content = MAIN_CSS.read_text(encoding="utf-8")
    lines = [
        line
        for line in content.splitlines()
        if line.strip() != POLISH_IMPORT
    ]

    while lines and not lines[-1].strip():
        lines.pop()

    lines.extend([POLISH_IMPORT, ""])
    MAIN_CSS.write_text("\n".join(lines), encoding="utf-8")


def build_css_bundle() -> None:
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
    ensure_css_import()
    build_css_bundle()

    print(
        "UI-Feinschliff angewendet und site.bundle.css "
        "mit dem zentralen Builder neu erzeugt."
    )


if __name__ == "__main__":
    main()
