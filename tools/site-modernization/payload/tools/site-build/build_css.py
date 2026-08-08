#!/usr/bin/env python3
"""Verwendet den bestehenden CSS-Bundler als einzige Quelle der Wahrheit."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_BUILDER = ROOT / "tools/review-upgrade/build_css.py"


def main(write: bool) -> int:
    if not CANONICAL_BUILDER.is_file():
        print(
            "Kanonischer CSS-Bundler fehlt: "
            f"{CANONICAL_BUILDER.relative_to(ROOT)}",
            file=sys.stderr,
        )
        return 1

    command = [sys.executable, str(CANONICAL_BUILDER)]
    if not write:
        command.append("--check")

    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Bundle schreiben; ohne Option wird nur geprüft.",
    )
    args = parser.parse_args()
    raise SystemExit(main(args.write))
