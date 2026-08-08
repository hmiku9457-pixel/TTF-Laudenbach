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
        "assets/js/features/tables.js",
        "table-compact-mobile--next-games",
        "table-compact-mobile--league",
        "table-mobile-only--record",
        "venue-badge",
        "abbreviateTeam"
    )
    require(
        "assets/css/components/ui-polish.css",
        "table.table--emphasis-first-column tbody th",
        ".images-event-list.animate.is-open",
        "table.table-compact-mobile--league",
        "table.table-compact-mobile--next-games",
        ".venue-tooltip"
    )
    require(
        "assets/css/main.css",
        '@import url("./components/ui-polish.css");'
    )
    require(
        "assets/css/site.bundle.css",
        "UI-Feinschliff: Tabellen und Galerie",
        "table-compact-mobile--next-games"
    )

    print("UI-Feinschliff erfolgreich verifiziert.")


if __name__ == "__main__":
    main()
