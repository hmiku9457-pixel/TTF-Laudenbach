#!/usr/bin/env python3
"""Entfernt Playwright- und Browser-Testinfrastruktur vollständig.

Die schnelle statische Qualitätsprüfung sowie `node --check` bleiben erhalten.
Das Skript ist tolerant gegenüber mehreren zwischenzeitlich verwendeten
Workflow-Strukturen.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]

FILES_TO_REMOVE = [
    "playwright.config.mjs",
    "package.json",
    "package-lock.json",
]

DIRECTORIES_TO_REMOVE = [
    "tests/e2e",
    "playwright-report",
    "test-results",
]

STANDALONE_WORKFLOWS_TO_REMOVE = [
    ".github/workflows/site-browser-quality.yml",
    ".github/workflows/browser-quality.yml",
    ".github/workflows/playwright.yml",
]

BLOCK_MARKERS = (
    "playwright",
    "browser- und layouttest",
    "browsertest",
    "browser test",
    "chromium installieren",
    "test:e2e",
    "playwright-report",
    "test-results/",
    "website-testbericht",
    "html-bereinigung-testbericht",
    "bereinigung-testbericht",
)

TRIGGER_PATH_PATTERNS = (
    "tests/e2e",
    "playwright.config",
    "package.json",
    "package-lock.json",
)

NPM_ONLY_LINES = (
    "npm install",
    "npm ci",
)


def remove_known_paths() -> None:
    for relative in FILES_TO_REMOVE:
        (ROOT / relative).unlink(missing_ok=True)

    for relative in DIRECTORIES_TO_REMOVE:
        shutil.rmtree(ROOT / relative, ignore_errors=True)

    for relative in STANDALONE_WORKFLOWS_TO_REMOVE:
        (ROOT / relative).unlink(missing_ok=True)


def split_step_blocks(lines: list[str]) -> list[list[str]]:
    """Teilt eine Workflowdatei in normale Textbereiche und Schrittblöcke.

    GitHub-Actions-Schritte beginnen in den verwendeten Workflows mit sechs
    Leerzeichen und `- name:` oder `- uses:`.
    """
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        is_step_start = bool(
            re.match(r"^ {6}- (?:name|uses):", line)
        )
        if is_step_start and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)
    return blocks


def is_browser_block(block: list[str]) -> bool:
    text = "\n".join(block).lower()
    return any(marker in text for marker in BLOCK_MARKERS)


def clean_mixed_dependency_block(block: list[str]) -> list[str]:
    """Entfernt npm-Installationen, erhält aber beispielsweise pip-Befehle."""
    cleaned = []
    for line in block:
        lowered = line.lower()
        if any(command in lowered for command in NPM_ONLY_LINES):
            continue
        cleaned.append(line)

    # Ein mehrzeiliger run-Block darf nicht leer zurückbleiben.
    meaningful = [
        line.strip()
        for line in cleaned
        if line.strip()
        and not line.lstrip().startswith("- name:")
        and line.strip() != "run: |"
    ]
    if not meaningful and any("run: |" in line for line in cleaned):
        return []
    return cleaned


def clean_workflow(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    blocks = split_step_blocks(lines)
    output: list[str] = []

    for block in blocks:
        if is_browser_block(block):
            continue

        cleaned = clean_mixed_dependency_block(block)
        for line in cleaned:
            if any(
                pattern in line.lower()
                for pattern in TRIGGER_PATH_PATTERNS
            ):
                continue
            output.append(line)

    # Überzählige Leerzeilen reduzieren, ohne die YAML-Struktur umzuschreiben.
    compact: list[str] = []
    previous_blank = False
    for line in output:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = blank

    result = "\n".join(compact).rstrip() + "\n"
    if result != original:
        path.write_text(result, encoding="utf-8")


def clean_all_workflows() -> None:
    workflow_dir = ROOT / ".github/workflows"
    if not workflow_dir.exists():
        return

    own_workflow = workflow_dir / "remove-browser-tests.yml"
    for path in sorted(workflow_dir.iterdir()):
        if path == own_workflow or path.suffix not in {".yml", ".yaml"}:
            continue
        clean_workflow(path)


def update_gitignore() -> None:
    path = ROOT / ".gitignore"
    if not path.exists():
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    markers = {
        "playwright-report/",
        "test-results/",
        "node_modules/",
    }
    cleaned = [line for line in lines if line.strip() not in markers]
    path.write_text("\n".join(cleaned).rstrip() + "\n", encoding="utf-8")


def remove_self() -> None:
    (ROOT / ".github/workflows/remove-browser-tests.yml").unlink(
        missing_ok=True
    )
    shutil.rmtree(SCRIPT_DIR, ignore_errors=True)


def main() -> int:
    remove_known_paths()
    clean_all_workflows()
    update_gitignore()
    remove_self()

    print("Browser- und Layouttests wurden vollständig entfernt.")
    print("Beibehalten wurden:")
    print("- statische HTML-, JSON-, Link- und Importprüfung")
    print("- JavaScript-Syntaxprüfung mit node --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
