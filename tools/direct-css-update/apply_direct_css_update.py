#!/usr/bin/env python3
"""Kleines, einmaliges Update ohne Bundle- oder Browsertest-Abhängigkeit.

Änderungen:
1. Alle HTML-Seiten laden assets/css/main.css direkt.
2. site.bundle.css wird gelöscht.
3. Mobile Kurzbeschriftungen und Kurzwerte der Spieltabellen werden sichtbar.
4. Vorhandene Python-Prüfungen erwarten main.css statt site.bundle.css.
5. tools/site/build.py erzeugt kein CSS-Bundle mehr.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TABLE_FIX_START = "/* TTF:MOBILE-TABLE-VISIBILITY:START */"
TABLE_FIX_END = "/* TTF:MOBILE-TABLE-VISIBILITY:END */"

TABLE_FIX = f"""{TABLE_FIX_START}
/* Mobile Kurzbeschriftungen und Kurzwerte der Spieltabellen anzeigen */
@media (max-width: 768px) {{
    table.table-compact-mobile .responsive-label--desktop,
    table.table-compact-mobile .responsive-value--desktop {{
        display: none;
    }}

    table.table-compact-mobile .responsive-label--mobile,
    table.table-compact-mobile .responsive-value--mobile {{
        display: inline;
    }}
}}
{TABLE_FIX_END}
"""


def html_files() -> list[Path]:
    files = [ROOT / "index.html", ROOT / "404.html"]
    pages = ROOT / "pages"
    if pages.exists():
        files.extend(sorted(pages.rglob("*.html")))
    return [path for path in files if path.is_file()]


def update_html_stylesheets() -> int:
    changed = 0

    for path in html_files():
        original = path.read_text(encoding="utf-8")
        updated = original.replace(
            "/assets/css/site.bundle.css",
            "/assets/css/main.css",
        )
        updated = updated.replace(
            "assets/css/site.bundle.css",
            "assets/css/main.css",
        )

        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    return changed


def update_tables_css() -> None:
    path = ROOT / "assets/css/components/tables.css"
    if not path.is_file():
        raise RuntimeError(
            "assets/css/components/tables.css wurde nicht gefunden."
        )

    text = path.read_text(encoding="utf-8")
    existing = re.compile(
        re.escape(TABLE_FIX_START)
        + r".*?"
        + re.escape(TABLE_FIX_END),
        re.DOTALL,
    )
    text = existing.sub("", text).rstrip()
    path.write_text(text + "\n\n" + TABLE_FIX, encoding="utf-8")


def update_python_references() -> int:
    changed = 0
    tools = ROOT / "tools"
    if not tools.exists():
        return changed

    for path in sorted(tools.rglob("*.py")):
        if path.resolve() == Path(__file__).resolve():
            continue

        original = path.read_text(encoding="utf-8")
        updated = original.replace(
            "/assets/css/site.bundle.css",
            "/assets/css/main.css",
        )
        updated = updated.replace(
            "assets/css/site.bundle.css",
            "assets/css/main.css",
        )
        updated = updated.replace(
            "CSS-Bundle und Sitemap",
            "Sitemap",
        )
        updated = updated.replace(
            "Header, Footer, CSS-Bundle und Sitemap",
            "Header, Footer und Sitemap",
        )

        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    return changed


def disable_bundle_generation() -> bool:
    path = ROOT / "tools/site/build.py"
    if not path.is_file():
        return False

    original = path.read_text(encoding="utf-8")
    updated = original

    # Entfernt nur den tatsächlichen Schreib-/Prüfaufruf. Die nun ungenutzten
    # Hilfsfunktionen dürfen vorerst stehen bleiben; dadurch bleibt der Patch
    # klein und risikoarm.
    updated = re.sub(
        r"(?m)^[ \t]*update_or_check\("
        r"CSS_OUTPUT,\s*expected_css\(\),\s*write_changes,\s*changed"
        r"\)\s*\n",
        "",
        updated,
    )

    # Mehrzeilige Variante.
    updated = re.sub(
        r"(?ms)^[ \t]*update_or_check\(\s*"
        r"CSS_OUTPUT,\s*expected_css\(\),\s*write_changes,\s*changed\s*"
        r"\)\s*\n",
        "",
        updated,
    )

    updated = updated.replace(
        "- assets/css/main.css\n",
        "",
        1,
    )

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def remove_bundle() -> bool:
    path = ROOT / "assets/css/site.bundle.css"
    if path.exists():
        path.unlink()
        return True
    return False


def verify() -> None:
    errors: list[str] = []

    main_css = ROOT / "assets/css/main.css"
    tables_css = ROOT / "assets/css/components/tables.css"
    bundle = ROOT / "assets/css/site.bundle.css"

    if not main_css.is_file():
        errors.append("assets/css/main.css fehlt.")
    if not tables_css.is_file():
        errors.append("assets/css/components/tables.css fehlt.")
    if bundle.exists():
        errors.append("assets/css/site.bundle.css wurde nicht entfernt.")

    for path in html_files():
        text = path.read_text(encoding="utf-8")
        if "site.bundle.css" in text:
            errors.append(
                f"{path.relative_to(ROOT)} verweist noch auf site.bundle.css."
            )
        if "/assets/css/main.css" not in text:
            errors.append(
                f"{path.relative_to(ROOT)} lädt assets/css/main.css nicht."
            )

    table_text = tables_css.read_text(encoding="utf-8")
    if TABLE_FIX_START not in table_text:
        errors.append("Der mobile Tabellenfix fehlt in tables.css.")

    build_path = ROOT / "tools/site/build.py"
    if build_path.exists():
        build_text = build_path.read_text(encoding="utf-8")
        if re.search(
            r"update_or_check\(\s*CSS_OUTPUT,\s*expected_css\(\)",
            build_text,
            re.DOTALL,
        ):
            errors.append(
                "tools/site/build.py versucht weiterhin, "
                "site.bundle.css zu erzeugen."
            )

    if errors:
        raise RuntimeError(
            "Direktes CSS-Update unvollständig:\n- "
            + "\n- ".join(errors)
        )


def main() -> int:
    html_count = update_html_stylesheets()
    update_tables_css()
    python_count = update_python_references()
    build_changed = disable_bundle_generation()
    bundle_removed = remove_bundle()
    verify()

    print("Direktes CSS-Update erfolgreich angewendet.")
    print(f"- HTML-Dateien angepasst: {html_count}")
    print(f"- Python-Dateien angepasst: {python_count}")
    print(f"- Build angepasst: {'ja' if build_changed else 'nicht erforderlich'}")
    print(f"- site.bundle.css entfernt: {'ja' if bundle_removed else 'war nicht vorhanden'}")
    print("- Mobile Spieltabellen zeigen Kurztexte und Kurzwerte wieder an.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
