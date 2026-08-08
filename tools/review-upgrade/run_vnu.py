#!/usr/bin/env python3
"""Ruft den Nu HTML Checker nur für vollständige HTML-Dokumente auf."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = Path(__file__).resolve().parent / "node_modules/.bin/vnu"


def is_full_document(path: Path) -> bool:
    head = path.read_text(encoding="utf-8", errors="replace")[:2000].lower()
    return "<html" in head and "<!doctype" in head


def main() -> int:
    files = [
        str(path.relative_to(ROOT))
        for path in sorted(ROOT.rglob("*.html"))
        if ".git" not in path.parts
        and "node_modules" not in path.parts
        and is_full_document(path)
    ]
    if not files:
        print("Keine vollständigen HTML-Dokumente gefunden.", file=sys.stderr)
        return 1
    if not BIN.exists():
        print(f"Nu HTML Checker fehlt: {BIN}", file=sys.stderr)
        return 1

    result = subprocess.run([str(BIN), "--errors-only", *files], cwd=ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
