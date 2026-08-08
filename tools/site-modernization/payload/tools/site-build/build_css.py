#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "assets/css/main.css"
OUTPUT = ROOT / "assets/css/site.bundle.css"
IMPORT_RE = re.compile(r'^\s*@import\s+url\(["\'](?P<path>[^"\']+)["\']\)\s*;\s*$', re.MULTILINE)


def resolve(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(p) for p in (*stack, path))
        raise RuntimeError(f"Zirkulärer CSS-Import: {chain}")
    text = path.read_text(encoding="utf-8")
    base = path.parent
    def repl(match: re.Match[str]) -> str:
        target = (base / match.group("path")).resolve()
        if not target.is_file():
            raise FileNotFoundError(f"CSS-Import fehlt: {target}")
        rel = target.relative_to(ROOT)
        return f"\n/* ===== Quelle: {rel.as_posix()} ===== */\n{resolve(target, (*stack, path))}\n"
    return IMPORT_RE.sub(repl, text)


def build(write: bool) -> int:
    generated = "/* Automatisch erzeugt aus assets/css/main.css. Nicht direkt bearbeiten. */\n" + resolve(ENTRY)
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
    if current == generated:
        print("CSS-Bundle ist aktuell.")
        return 0
    if write:
        OUTPUT.write_text(generated, encoding="utf-8")
        print("CSS-Bundle aktualisiert.")
        return 0
    print("assets/css/site.bundle.css ist nicht aktuell.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raise SystemExit(build(args.write))
