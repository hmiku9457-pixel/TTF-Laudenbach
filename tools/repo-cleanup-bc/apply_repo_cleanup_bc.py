#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF_DIR = Path("tools/repo-cleanup-bc")
TEXT_SUFFIXES = {".html", ".js", ".css", ".md", ".txt", ".json", ".py", ".yml", ".yaml", ".xml"}
PRODUCTION_REF_SUFFIXES = {".html", ".js", ".css"}


def rel(path: Path) -> Path:
    return path.resolve().relative_to(ROOT.resolve())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str) -> bool:
    old = read(path)
    if old == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"GEÄNDERT: {rel(path)}")
    return True


def iter_text_files(suffixes: set[str] = TEXT_SUFFIXES):
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative = rel(path)
        if ".git" in relative.parts:
            continue
        if relative == SELF_DIR or SELF_DIR in relative.parents:
            continue
        yield path


def references(tokens: tuple[str, ...], excluded: set[Path]) -> list[Path]:
    hits: list[Path] = []
    excluded_resolved = {path.resolve() for path in excluded}
    for path in iter_text_files(PRODUCTION_REF_SUFFIXES):
        if path.resolve() in excluded_resolved:
            continue
        try:
            content = read(path)
        except UnicodeDecodeError:
            continue
        if any(token in content for token in tokens):
            hits.append(rel(path))
    return sorted(hits)


def preflight() -> None:
    main_js = ROOT / "assets/js/main.js"
    theme_js = ROOT / "assets/js/features/theme-switcher.js"
    page_css = ROOT / "assets/css/components/page-content.css"

    theme_hits = references(
        ("themeSwitcher", "theme-switcher.js", "theme-red", "theme-dark"),
        {main_js, theme_js},
    )
    if theme_hits:
        raise RuntimeError(
            "Der Theme-Switcher wird außerhalb seiner bisherigen Initialisierung noch verwendet. "
            "Cleanup wird sicherheitshalber nicht gestartet:\n- " + "\n- ".join(map(str, theme_hits))
        )

    home_hits = references(
        ("home-intro", "home-intro__lead", "home-intro__actions"),
        {page_css},
    )
    if home_hits:
        raise RuntimeError(
            "Die alte .home-intro-Struktur wird noch außerhalb von page-content.css verwendet. "
            "Cleanup wird sicherheitshalber nicht gestartet:\n- " + "\n- ".join(map(str, home_hits))
        )


def update_readme() -> bool:
    path = ROOT / "README.md"
    content = read(path)

    old_data = "- **`assets/data/`** – dynamisch erzeugte JSON-Daten"
    new_data = "- **`assets/data/`** – JSON-Daten für dynamische Inhalte; teils automatisch erzeugt, teils manuell gepflegt"
    if old_data in content:
        content = content.replace(old_data, new_data, 1)
    elif new_data not in content:
        raise RuntimeError("README: Beschreibung von assets/data konnte nicht eindeutig gefunden werden.")

    old_css = "`main.css` importiert die getrennten Base-, Layout-, Komponenten- und Responsive-Dateien. Es ist kein Build-Schritt notwendig."
    new_css = (
        "`main.css` importiert die getrennten Base-, Layout- und Komponenten-Dateien. "
        "Responsive-Regeln liegen direkt bei der jeweiligen Komponente. Es ist kein Build-Schritt notwendig."
    )
    if old_css in content:
        content = content.replace(old_css, new_css, 1)
    elif new_css not in content:
        raise RuntimeError("README: CSS-Beschreibung konnte nicht eindeutig gefunden werden.")

    if "## Datenpflege" not in content:
        marker = "## Typische Änderungen"
        if marker not in content:
            raise RuntimeError("README: Einfügeposition vor 'Typische Änderungen' wurde nicht gefunden.")
        section = """## Datenpflege

Unter `assets/data/` liegen sowohl automatisch erzeugte als auch manuell gepflegte JSON-Dateien. Für die Wartung gilt:

| Datei | Pflege |
|---|---|
| `news.json` | aktuell manuell gepflegt; die geplante CMS-Anbindung soll diese Pflege später übernehmen |
| `gallerie.json` | automatisch durch **Generate Gallery JSON** / `assets/python/generate_gallery.py` |
| `links.json` | automatisch aus `assets/python/config.py` durch den Scraper |
| `spiele*.json` | automatisch durch den Scraper |
| `tabelle*.json` | automatisch durch den Scraper |
| `spieler*.json` | automatisch durch den Scraper |

Automatisch erzeugte Dateien sollten nicht dauerhaft manuell korrigiert werden. Änderungen gehören stattdessen in die jeweilige Quelle oder Konfiguration, damit sie beim nächsten Workflow-Lauf nicht überschrieben werden.

"""
        content = content.replace(marker, section + marker, 1)

    return write_if_changed(path, content)


def remove_theme_switcher() -> bool:
    main_path = ROOT / "assets/js/main.js"
    feature_path = ROOT / "assets/js/features/theme-switcher.js"
    changed = False

    content = read(main_path)
    pattern = re.compile(
        r'\n[ \t]*if \(has\("#themeSwitcher"\)\) \{[ \t]*\n'
        r'[ \t]*tasks\.push\(loadFeature\("\./features/theme-switcher\.js", "initThemeSwitcher"\)\);[ \t]*\n'
        r'[ \t]*\}[ \t]*\n',
        re.MULTILINE,
    )
    if "#themeSwitcher" in content or "theme-switcher.js" in content:
        updated, count = pattern.subn("\n", content, count=1)
        if count != 1:
            raise RuntimeError("main.js: Theme-Switcher-Initialisierung hat einen unbekannten Stand.")
        changed |= write_if_changed(main_path, updated)

    if feature_path.exists():
        feature_path.unlink()
        print(f"GELÖSCHT: {rel(feature_path)}")
        changed = True

    return changed


def remove_unused_home_intro() -> bool:
    path = ROOT / "assets/css/components/page-content.css"
    content = read(path)
    if "home-intro" not in content:
        return False

    patterns = [
        re.compile(r"\n\.home-intro \{.*?\}\s*", re.DOTALL),
        re.compile(r"\n\.home-intro \.page-heading \{.*?\}\s*", re.DOTALL),
        re.compile(r"\n\.home-intro__lead \{.*?\}\s*", re.DOTALL),
        re.compile(r"\n\.home-intro__actions \{.*?\}\s*", re.DOTALL),
        re.compile(
            r"\n@media \(max-width: 768px\) \{\s*"
            r"\.home-intro \{.*?\}\s*"
            r"\.home-intro__actions > \* \{.*?\}\s*"
            r"\}\s*",
            re.DOTALL,
        ),
    ]

    updated = content
    total = 0
    for pattern in patterns:
        updated, count = pattern.subn("\n", updated, count=1)
        total += count

    if "home-intro" in updated:
        raise RuntimeError("page-content.css: .home-intro konnte nicht vollständig und eindeutig entfernt werden.")
    if total < 4:
        raise RuntimeError("page-content.css: Erwartete .home-intro-Regeln wurden nicht vollständig gefunden.")

    updated = re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"
    return write_if_changed(path, updated)


def clean_css_migration_comments() -> bool:
    changed = False
    marker_comment = re.compile(r"/\*\s*TTF:[^*]*?\*/\s*", re.IGNORECASE | re.DOTALL)

    for path in iter_text_files({".css"}):
        content = read(path)
        updated = content

        # Historische Hinweise auf die frühere monolithische style.css entfernen,
        # die keine Information über den heutigen Aufbau mehr liefern.
        updated = updated.replace(" Aus style.css unverändert ausgelagert.", "")
        updated = updated.replace(" Aus der style.css unverändert ausgelagert.", "")
        updated = marker_comment.sub("", updated)

        if updated != content:
            updated = re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"
            changed |= write_if_changed(path, updated)

    return changed


def update_page_structure_comment() -> bool:
    path = ROOT / "assets/js/core/page-structure.js"
    content = read(path)
    old = "// Ungültige Links werden von der Qualitätsprüfung abgefangen."
    new = "// Ungültige oder nicht auflösbare Links werden hier ignoriert."
    if old in content:
        content = content.replace(old, new, 1)
    elif new not in content:
        raise RuntimeError("page-structure.js: Erwarteter Kommentar wurde nicht gefunden.")
    return write_if_changed(path, content)


def verify() -> None:
    main_js = read(ROOT / "assets/js/main.js")
    if "themeSwitcher" in main_js or "theme-switcher.js" in main_js:
        raise RuntimeError("Verifikation fehlgeschlagen: main.js enthält noch Theme-Switcher-Logik.")
    if (ROOT / "assets/js/features/theme-switcher.js").exists():
        raise RuntimeError("Verifikation fehlgeschlagen: theme-switcher.js existiert noch.")

    page_css = read(ROOT / "assets/css/components/page-content.css")
    if "home-intro" in page_css or "--space-xxl" in page_css:
        raise RuntimeError("Verifikation fehlgeschlagen: alte home-intro-Regeln sind noch vorhanden.")

    readme = read(ROOT / "README.md")
    if "## Datenpflege" not in readme:
        raise RuntimeError("Verifikation fehlgeschlagen: README enthält keine Datenpflege-Dokumentation.")
    if "Komponenten- und Responsive-Dateien" in readme:
        raise RuntimeError("Verifikation fehlgeschlagen: README beschreibt noch die alte responsive.css-Struktur.")

    page_structure = read(ROOT / "assets/js/core/page-structure.js")
    if "von der Qualitätsprüfung abgefangen" in page_structure:
        raise RuntimeError("Verifikation fehlgeschlagen: veralteter Qualitätsprüfungs-Kommentar ist noch vorhanden.")

    for path in iter_text_files({".css"}):
        css = read(path)
        if "TTF:INTEGRATED" in css or "TTF:MOBILE-TABLE-VISIBILITY" in css:
            raise RuntimeError(f"Verifikation fehlgeschlagen: historischer Migrationsmarker in {rel(path)}")


def main() -> None:
    print("TTF Laudenbach – Repo-Cleanup B+C")
    print("==================================")
    print("Preflight: tatsächliche Nutzung alter Features prüfen ...")
    preflight()

    changes = []
    if update_readme():
        changes.append("README / Datenpflege")
    if remove_theme_switcher():
        changes.append("ungenutzter Theme-Switcher")
    if remove_unused_home_intro():
        changes.append("ungenutztes home-intro-CSS")
    if clean_css_migration_comments():
        changes.append("historische CSS-Migrationskommentare")
    if update_page_structure_comment():
        changes.append("page-structure-Kommentar")

    verify()
    print("\nVerifikation erfolgreich.")
    if changes:
        print("Geändert: " + ", ".join(changes))
    else:
        print("Keine Änderungen notwendig; Zielzustand ist bereits erreicht.")


if __name__ == "__main__":
    main()
