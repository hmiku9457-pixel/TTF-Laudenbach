from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def require(path: str, *tokens: str) -> None:
    file_path = ROOT / path

    if not file_path.is_file():
        raise SystemExit(f"Datei fehlt: {path}")

    content = file_path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in content]

    if missing:
        raise SystemExit(
            f"{path}: erwartete Inhalte fehlen: {', '.join(missing)}"
        )


def main() -> None:
    require(
        "assets/css/components/table-header-fix.css",
        "display: table-header-group !important",
        "display: table-row-group !important",
        ".table-scroll--compact > table.table-compact-mobile",
    )
    require(
        "assets/css/main.css",
        '@import url("./components/table-header-fix.css");',
    )
    require(
        "assets/css/site.bundle.css",
        "Korrektur der kompakten Tabellenköpfe",
        "display: table-header-group !important",
    )

    print("Tabellenkopf-Korrektur erfolgreich verifiziert.")


if __name__ == "__main__":
    main()
