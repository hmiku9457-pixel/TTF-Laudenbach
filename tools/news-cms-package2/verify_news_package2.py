#!/usr/bin/env python3
"""Prüft die dauerhafte News-Automatisierung aus Paket 2."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/generate-news.yml"
README = ROOT / "README.md"
DOCS = ROOT / "docs/news-content-format.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    require(WORKFLOW.is_file(), ".github/workflows/generate-news.yml fehlt.")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    required_fragments = (
        "name: News generieren",
        'branches: [main]',
        '"content/news/**"',
        '"assets/images/news/**"',
        '"assets/python/generate_news.py"',
        '"assets/python/news_requirements.txt"',
        '"templates/news-article.html"',
        '"templates/news-overview.html"',
        'cron: "17,47 * * * *"',
        'timezone: "Europe/Berlin"',
        "workflow_dispatch:",
        "contents: write",
        "pages: write",
        "group: repository-writer",
        'PYTHONDONTWRITEBYTECODE: "1"',
        "python assets/python/generate_news.py",
        "git reset --hard origin/main",
        "git add -A --",
        "pages/neuigkeiten.html",
        "pages/news",
        "assets/data/news.json",
        "sitemap.xml",
        "git push origin HEAD:main",
        "https://api.github.com/repos/${GITHUB_REPOSITORY}/pages/builds",
        "github.event_name == 'workflow_dispatch'",
    )
    for fragment in required_fragments:
        require(fragment in workflow, f"Workflow-Prüfung fehlgeschlagen: {fragment}")

    require(
        "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in workflow,
        "checkout ist nicht auf den im Repository verwendeten SHA gepinnt.",
    )
    require(
        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in workflow,
        "setup-python ist nicht auf den im Repository verwendeten SHA gepinnt.",
    )

    readme = README.read_text(encoding="utf-8")
    require("Der Workflow **News generieren** synchronisiert diese Ausgaben dauerhaft." in readme,
            "README beschreibt den dauerhaften News-Workflow nicht.")
    require("| `news.json` | automatisch durch **News generieren**" in readme,
            "README markiert news.json nicht als automatisch erzeugt.")
    require("aktuell manuell gepflegt" not in readme,
            "README enthält noch die veraltete manuelle news.json-Pflege.")

    docs = DOCS.read_text(encoding="utf-8")
    require("## Automatisierung" in docs, "Automatisierungsabschnitt in news-content-format.md fehlt.")
    require("Actions → News generieren → Run workflow" in docs,
            "Manueller Rebuild ist nicht dokumentiert.")

    print("News CMS Paket 2 erfolgreich validiert.")


if __name__ == "__main__":
    main()
