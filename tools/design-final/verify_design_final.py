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


def forbid(path: str, *tokens: str) -> None:
    content = (ROOT / path).read_text(encoding="utf-8")
    found = [token for token in tokens if token in content]

    if found:
        raise SystemExit(
            f"{path}: veraltete Inhalte gefunden: {', '.join(found)}"
        )


def main() -> None:
    require(
        "assets/js/features/tables.js",
        'new Set(["next-games", "league", "schedule"])',
        "function prepareScheduleTable",
        'ensureDualHeaderLabel(headerRow.cells[0], "Dat.")',
        "table-mobile-only--schedule-opponent",
        "table-mobile-only--schedule-venue",
    )
    require(
        "assets/js/features/animations.js",
        "function initRankingFade",
        "ranking-fade-ready",
        "--ranking-fade-delay",
    )
    forbid(
        "assets/js/features/animations.js",
        "index * 0.08",
    )
    require(
        "assets/js/features/gallery.js",
        "configureGalleryToggle(toggle)",
        'icon.textContent = "☰"',
        'label.textContent = "Galerien"',
    )
    require(
        "assets/css/components/ui-final.css",
        "table-compact-mobile--schedule",
        "rankingReverseFade",
        ".images-nav-toggle__icon",
    )
    require(
        "assets/css/main.css",
        '@import url("./components/ui-final.css");',
    )
    require(
        "assets/css/site.bundle.css",
        "Finale Designkorrekturen",
        "rankingReverseFade",
        "table-compact-mobile--schedule",
    )

    print("Finales Design-Update erfolgreich verifiziert.")


if __name__ == "__main__":
    main()
