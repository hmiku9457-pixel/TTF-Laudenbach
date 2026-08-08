#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ["build_components.py", "build_css.py", "generate_sitemap.py"]


def main(write: bool) -> int:
    for script in SCRIPTS:
        command = [sys.executable, str(Path(__file__).with_name(script))]
        if write:
            command.append("--write")
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.write))
