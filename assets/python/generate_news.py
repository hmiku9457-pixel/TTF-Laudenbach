#!/usr/bin/env python3
"""Erzeugt News-HTML, Übersicht, Slider-JSON und News-Sitemap-Einträge aus Markdown."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, time
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import mistune
import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content/news"
ARTICLE_TEMPLATE = ROOT / "templates/news-article.html"
OVERVIEW_TEMPLATE = ROOT / "templates/news-overview.html"
OUTPUT_DIR = ROOT / "pages/news"
OVERVIEW_OUTPUT = ROOT / "pages/neuigkeiten.html"
NEWS_JSON = ROOT / "assets/data/news.json"
SITEMAP = ROOT / "sitemap.xml"

SITE_URL = "https://www.ttf-laudenbach.de"
LOCAL_TIMEZONE = ZoneInfo("Europe/Berlin")
GENERATED_MARKER = "<!-- AUTO-GENERATED NEWS PAGE: DO NOT EDIT -->"
SLIDER_LIMIT = 5

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RAW_HTML_RE = re.compile(r"<\s*/?\s*[A-Za-z][A-Za-z0-9-]*(?:\s[^>]*)?/?>")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

ALLOWED_RENDERED_TAGS = {
    "p", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td", "blockquote", "code", "pre",
    "hr", "br",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "th": {"align", "style"},
    "td": {"align", "style"},
}


@dataclass(frozen=True)
class Article:
    source: Path
    slug: str
    title: str
    publish_at: datetime
    summary: str
    image: str
    image_alt: str
    body_markdown: str
    body_html: str

    @property
    def relative_url(self) -> str:
        return f"/pages/news/{self.slug}.html"

    @property
    def canonical_url(self) -> str:
        return f"{SITE_URL}{self.relative_url}"


class RenderedHtmlValidator(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED_RENDERED_TAGS:
            raise ValueError(f"{self.source.name}: nicht erlaubtes HTML-Element nach Markdown-Rendering: <{tag}>")

        allowed = ALLOWED_ATTRIBUTES.get(tag, set())
        for name, value in attrs:
            if name not in allowed:
                raise ValueError(
                    f"{self.source.name}: nicht erlaubtes Attribut '{name}' an <{tag}>."
                )
            if tag == "a" and name == "href":
                validate_link_target(value or "", self.source)
            if tag == "img" and name == "src":
                validate_image_path(value or "", self.source)
            if tag in {"th", "td"} and name == "style":
                if (value or "") not in {
                    "text-align:left",
                    "text-align:right",
                    "text-align:center",
                }:
                    raise ValueError(
                        f"{self.source.name}: nicht erlaubter Tabellen-Style: {value}"
                    )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--now",
        help="Optionaler ISO-Zeitpunkt für reproduzierbare Tests. Ohne Angabe wird die aktuelle Europe/Berlin-Zeit verwendet.",
    )
    return parser.parse_args()


def resolve_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(LOCAL_TIMEZONE)

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)
    return parsed.astimezone(LOCAL_TIMEZONE)


def parse_frontmatter(source: Path) -> tuple[dict[str, Any], str]:
    text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError(f"{source.name}: YAML-Frontmatter muss mit '---' beginnen.")

    separator = "\n---\n"
    end = text.find(separator, 4)
    if end < 0:
        raise ValueError(f"{source.name}: abschließendes '---' des Frontmatters fehlt.")

    raw_frontmatter = text[4:end]
    body = text[end + len(separator):].strip()
    loaded = yaml.safe_load(raw_frontmatter)

    if not isinstance(loaded, dict):
        raise ValueError(f"{source.name}: Frontmatter muss ein YAML-Objekt sein.")
    if not body:
        raise ValueError(f"{source.name}: Artikeltext ist leer.")
    return loaded, body


def required_text(data: dict[str, Any], key: str, source: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source.name}: Pflichtfeld '{key}' fehlt oder ist leer.")
    return value.strip()


def parse_publish_at(value: Any, source: Path) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f"{source.name}: 'publish_at' ist kein gültiger ISO-Zeitpunkt.") from exc
    else:
        raise ValueError(f"{source.name}: Pflichtfeld 'publish_at' fehlt oder ist ungültig.")

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)
    return parsed.astimezone(LOCAL_TIMEZONE)


def validate_slug(slug: str, source: Path) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(
            f"{source.name}: Dateiname muss aus Kleinbuchstaben, Ziffern und Bindestrichen bestehen."
        )


def validate_image_path(path: str, source: Path) -> None:
    if not path.startswith("/assets/images/"):
        raise ValueError(f"{source.name}: Bildpfad muss unter /assets/images/ liegen: {path}")

    pure = PurePosixPath(path)
    if ".." in pure.parts:
        raise ValueError(f"{source.name}: Bildpfad darf kein '..' enthalten: {path}")

    local = ROOT / path.lstrip("/")
    if not local.is_file():
        raise ValueError(f"{source.name}: Bilddatei existiert nicht: {path}")


def validate_link_target(target: str, source: Path) -> None:
    target = target.strip()
    if not target:
        raise ValueError(f"{source.name}: leerer Link ist nicht erlaubt.")

    parsed = urlparse(target)
    if parsed.scheme.lower() in {"javascript", "data", "vbscript"}:
        raise ValueError(f"{source.name}: unsicheres Link-Schema: {parsed.scheme}")

    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto", "tel"}:
        raise ValueError(f"{source.name}: nicht unterstütztes Link-Schema: {parsed.scheme}")


def validate_markdown_source(body: str, source: Path) -> None:
    raw_html = RAW_HTML_RE.search(body)
    if raw_html:
        raise ValueError(
            f"{source.name}: rohes HTML ist nicht erlaubt: {raw_html.group(0)[:80]}"
        )

    for heading in HEADING_RE.finditer(body):
        level = len(heading.group(1))
        if level not in {2, 3}:
            raise ValueError(
                f"{source.name}: nur H2 und H3 sind im Artikeltext erlaubt; gefunden: H{level}."
            )

    for match in MARKDOWN_IMAGE_RE.finditer(body):
        alt = match.group(1).strip()
        path = match.group(2).strip().strip("<>")
        if not alt:
            raise ValueError(f"{source.name}: Bilder im Artikel benötigen einen Alt-Text.")
        validate_image_path(path, source)


def render_markdown(body: str, source: Path) -> str:
    renderer = mistune.create_markdown(escape=True, plugins=["table"])
    rendered = renderer(body)

    validator = RenderedHtmlValidator(source)
    validator.feed(rendered)
    validator.close()

    rendered = rendered.replace("<table>", '<div class="news-table-wrapper"><table>')
    rendered = rendered.replace("</table>", "</table></div>")
    return rendered


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self.parts.append(cleaned)


def auto_summary(body_html: str, limit: int = 240) -> str:
    parser = TextExtractor()
    parser.feed(body_html)
    text = " ".join(parser.parts)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text

    shortened = text[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return shortened + " …"


def load_article(source: Path) -> Article:
    data, body = parse_frontmatter(source)
    slug = source.stem
    validate_slug(slug, source)

    title = required_text(data, "title", source)
    image = required_text(data, "image", source)
    image_alt = required_text(data, "image_alt", source)
    publish_at = parse_publish_at(data.get("publish_at"), source)

    validate_image_path(image, source)
    validate_markdown_source(body, source)
    body_html = render_markdown(body, source)

    raw_summary = data.get("summary")
    if raw_summary is None or (isinstance(raw_summary, str) and not raw_summary.strip()):
        summary = auto_summary(body_html)
    elif isinstance(raw_summary, str):
        summary = " ".join(raw_summary.split())
    else:
        raise ValueError(f"{source.name}: 'summary' muss Text sein.")

    if not summary:
        raise ValueError(f"{source.name}: es konnte kein Teaser erzeugt werden.")

    return Article(
        source=source,
        slug=slug,
        title=title,
        publish_at=publish_at,
        summary=summary,
        image=image,
        image_alt=image_alt,
        body_markdown=body,
        body_html=body_html,
    )


def load_all_articles() -> list[Article]:
    if not CONTENT_DIR.is_dir():
        raise ValueError("content/news fehlt.")

    sources = sorted(CONTENT_DIR.glob("*.md"))
    if not sources:
        raise ValueError("content/news enthält keine Markdown-Artikel.")

    articles = [load_article(source) for source in sources]
    slugs = [article.slug for article in articles]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Mehrere Artikel erzeugen denselben Slug.")
    return articles


GERMAN_MONTHS = (
    "",
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
)


def display_date(value: datetime) -> str:
    return f"{value.day}. {GERMAN_MONTHS[value.month]} {value.year}"


def render_template(path: Path, values: dict[str, str]) -> str:
    template = path.read_text(encoding="utf-8")
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)

    unresolved = PLACEHOLDER_RE.findall(result)
    if unresolved:
        raise ValueError(f"{path.name}: nicht ersetzte Template-Platzhalter: {', '.join(sorted(set(unresolved)))}")
    return result


def article_html(article: Article) -> str:
    image_url = SITE_URL + article.image
    values = {
        "PAGE_TITLE": escape(f"{article.title} | TTF Laudenbach", quote=True),
        "DESCRIPTION": escape(article.summary, quote=True),
        "CANONICAL_URL": escape(article.canonical_url, quote=True),
        "IMAGE_URL": escape(image_url, quote=True),
        "IMAGE_PATH": escape(article.image, quote=True),
        "IMAGE_ALT": escape(article.image_alt, quote=True),
        "TITLE": escape(article.title),
        "DATETIME": escape(article.publish_at.isoformat(), quote=True),
        "DISPLAY_DATE": escape(display_date(article.publish_at)),
        "CONTENT": article.body_html,
    }
    rendered = render_template(ARTICLE_TEMPLATE, values)
    return GENERATED_MARKER + "\n" + rendered


def overview_item(article: Article) -> str:
    return f"""<article class="box news-overview-card">
<div class="news-overview-card__media">
<img src="{escape(article.image, quote=True)}" alt="{escape(article.image_alt, quote=True)}" loading="lazy" decoding="async"/>
</div>
<div class="news-overview-card__content">
<time class="news-overview__date" datetime="{escape(article.publish_at.isoformat(), quote=True)}">{escape(display_date(article.publish_at))}</time>
<h2 class="news-overview-card__title">{escape(article.title)}</h2>
<p class="news-overview-card__summary">{escape(article.summary)}</p>
<a class="button news-overview-card__link" href="{escape(article.relative_url, quote=True)}">Mehr lesen</a>
</div>
</article>"""


def overview_html(articles: list[Article]) -> str:
    items = "\n".join(overview_item(article) for article in articles)
    rendered = render_template(OVERVIEW_TEMPLATE, {"NEWS_ITEMS": items})
    return GENERATED_MARKER + "\n" + rendered


def slider_json(articles: list[Article]) -> str:
    payload = [
        {
            "title": article.title,
            "text": article.summary,
            "image": article.image,
            "imageAlt": article.image_alt,
            "link": article.relative_url,
        }
        for article in articles[:SLIDER_LIMIT]
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def sync_sitemap(existing: str, articles: list[Article]) -> str:
    block_re = re.compile(
        r"\s*<url>\s*<loc>https://www\.ttf-laudenbach\.de/pages/(?:news/[^<]+|neuigkeiten\.html)</loc>\s*</url>",
        re.MULTILINE,
    )
    cleaned = block_re.sub("", existing)

    blocks = [
        "  <url>\n    <loc>https://www.ttf-laudenbach.de/pages/neuigkeiten.html</loc>\n  </url>"
    ]
    blocks.extend(
        f"  <url>\n    <loc>{article.canonical_url}</loc>\n  </url>"
        for article in articles
    )
    insert = "\n" + "\n".join(blocks) + "\n"

    if "</urlset>" not in cleaned:
        raise ValueError("sitemap.xml: schließendes </urlset> fehlt.")

    cleaned = cleaned.replace("</urlset>", insert + "</urlset>", 1)
    return cleaned.replace("\n\n\n", "\n\n")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def cleanup_stale_pages(expected_names: set[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.glob("*.html"):
        if path.name in expected_names:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        if GENERATED_MARKER in text or path.name in {"artikel1.html", "artikel2.html"}:
            path.unlink()


def generate(now: datetime) -> None:
    all_articles = load_all_articles()
    published = sorted(
        (article for article in all_articles if article.publish_at <= now),
        key=lambda article: (article.publish_at, article.slug),
        reverse=True,
    )

    article_outputs = {
        f"{article.slug}.html": article_html(article)
        for article in published
    }
    overview = overview_html(published)
    slider = slider_json(published)
    sitemap = sync_sitemap(SITEMAP.read_text(encoding="utf-8"), published)

    # Erst nach erfolgreicher Validierung und vollständigem Rendern wird geschrieben.
    cleanup_stale_pages(set(article_outputs))

    for filename, content in article_outputs.items():
        atomic_write(OUTPUT_DIR / filename, content)

    atomic_write(OVERVIEW_OUTPUT, overview)
    atomic_write(NEWS_JSON, slider)
    atomic_write(SITEMAP, sitemap)

    print(
        f"News generiert: {len(published)} veröffentlicht, "
        f"{len(all_articles) - len(published)} geplant, "
        f"{min(len(published), SLIDER_LIMIT)} im Slider."
    )


def main() -> None:
    args = parse_args()
    generate(resolve_now(args.now))


if __name__ == "__main__":
    main()
