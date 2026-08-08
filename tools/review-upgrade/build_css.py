#!/usr/bin/env python3
"""Bündelt die modularen CSS-Quellen ohne aggressive Minifizierung."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "assets/css/main.css"
OUTPUT = ROOT / "assets/css/site.bundle.css"
IMPORT_RE = re.compile(r"^\s*@import\s+(?:url\()?['\"]([^'\"]+)['\"]\)?\s*;\s*$", re.I | re.M)


def expand(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(item.relative_to(ROOT)) for item in (*stack, path))
        raise RuntimeError(f"Zirkulärer CSS-Import: {chain}")
    if not path.is_file():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")
    result: list[str] = [f"/* Quelle: {path.relative_to(ROOT).as_posix()} */\n"]
    cursor = 0

    for match in IMPORT_RE.finditer(text):
        result.append(text[cursor:match.start()])
        import_value = match.group(1)
        if "://" in import_value or import_value.startswith("data:"):
            result.append(match.group(0))
        else:
            result.append(expand(path.parent / import_value, (*stack, path)))
        cursor = match.end()

    result.append(text[cursor:])
    return "".join(result).strip() + "\n"


def build() -> str:
    banner = "/* Automatisch aus assets/css/main.css erzeugt. Nicht direkt bearbeiten. */\n"
    return banner + expand(ENTRY)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Nur prüfen, nicht schreiben")
    args = parser.parse_args()
    expected = build()

    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("assets/css/site.bundle.css ist nicht aktuell.", file=sys.stderr)
            return 1
        print("CSS-Bundle ist aktuell.")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"{OUTPUT.relative_to(ROOT)} erzeugt ({len(expected)} Zeichen).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
