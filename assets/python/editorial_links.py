"""Redaktionelle Links für CMS-Deployment und manuellen Alt-Scraper."""
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "content/site"


def load_editorial_links():
    links = json.loads((SOURCE / "links.json").read_text(encoding="utf-8"))
    sponsors = json.loads((SOURCE / "sponsors.json").read_text(encoding="utf-8"))
    result = []
    for key, items in (
        ("tt-links", links.get("tt")),
        ("sport_allgemein", links.get("sports")),
        ("dies_und_das", links.get("other")),
        ("sponsoren", sponsors.get("items")),
    ):
        result.append({"gruppe": key, "links": [
            {"id": f"{key}-{i+1}", "name": item["name"], "url": item["url"]}
            for i, item in enumerate(items or [])
        ]})
    return result
