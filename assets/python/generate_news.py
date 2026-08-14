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
IMAGE_PARAGRAPH_RE = re.compile(r"<p>\s*(<img\b[^>]*?/?>)\s*</p>", re.IGNORECASE)

ALLOWED_RENDERED_TAGS = {
    "p", "h1", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td", "blockquote", "code", "pre",
    "hr", "br",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "th": {"align", "style"},
    "td": {"align", "style"},
}
BLOCK_TYPES = {"text", "two_columns", "event", "divider", "spacer"}
ALIGNMENTS = {"left", "center"}
SPACER_SIZES = {"small", "medium", "large"}
EVENT_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


@dataclass(frozen=True)
class Article:
    source: Path
    slug: str
    title: str
    publish_at: datetime
    summary: str
    image: str
    image_alt: str
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
            raise ValueError(
                f"{self.source.name}: nicht erlaubtes HTML-Element nach Markdown-Rendering: <{tag}>"
            )

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
        help=(
            "Optionaler ISO-Zeitpunkt für reproduzierbare Tests. "
            "Ohne Angabe wird die aktuelle Europe/Berlin-Zeit verwendet."
        ),
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

    return loaded, body


def required_text(data: dict[str, Any], key: str, source: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source.name}: Pflichtfeld '{key}' fehlt oder ist leer.")
    return value.strip()


def optional_text(data: dict[str, Any], key: str, source: Path) -> str:
    value = data.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{source.name}: Feld '{key}' muss Text sein.")
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
            raise ValueError(
                f"{source.name}: 'publish_at' ist kein gültiger ISO-Zeitpunkt."
            ) from exc
    else:
        raise ValueError(
            f"{source.name}: Pflichtfeld 'publish_at' fehlt oder ist ungültig."
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)
    return parsed.astimezone(LOCAL_TIMEZONE)


def parse_event_date(value: Any, source: Path, block_number: int) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(
                f"{source.name}: Eventblock {block_number}: 'date' muss YYYY-MM-DD sein."
            ) from exc

    raise ValueError(
        f"{source.name}: Eventblock {block_number}: Pflichtfeld 'date' fehlt oder ist ungültig."
    )


def parse_event_time(value: Any, source: Path, block_number: int) -> str:
    if value is None or value == "":
        return ""

    if isinstance(value, time):
        return value.strftime("%H:%M")

    # PyYAML (YAML 1.1) interpretiert ungequotete Werte wie 20:30 als
    # Sexagesimalzahl: 20 * 60 + 30 = 1230. Pages CMS kann Uhrzeiten genau
    # in dieser Form serialisieren. Solche Werte werden wieder zuverlässig
    # in HH:MM zurückgeführt.
    if isinstance(value, int) and not isinstance(value, bool):
        if 0 <= value < 24 * 60:
            hours, minutes = divmod(value, 60)
            return f"{hours:02d}:{minutes:02d}"

        raise ValueError(
            f"{source.name}: Eventblock {block_number}: 'time' liegt außerhalb eines gültigen Tages."
        )

    if not isinstance(value, str) or not EVENT_TIME_RE.fullmatch(value.strip()):
        raise ValueError(
            f"{source.name}: Eventblock {block_number}: 'time' muss leer oder im Format HH:MM sein."
        )

    return value.strip()


def validate_slug(slug: str, source: Path) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(
            f"{source.name}: Dateiname muss aus Kleinbuchstaben, Ziffern und Bindestrichen bestehen."
        )


def validate_image_path(path: str, source: Path) -> None:
    if not path.startswith("/assets/images/"):
        raise ValueError(
            f"{source.name}: Bildpfad muss unter /assets/images/ liegen: {path}"
        )

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
        raise ValueError(
            f"{source.name}: unsicheres Link-Schema: {parsed.scheme}"
        )

    if parsed.scheme and parsed.scheme.lower() not in {
        "http", "https", "mailto", "tel"
    }:
        raise ValueError(
            f"{source.name}: nicht unterstütztes Link-Schema: {parsed.scheme}"
        )


def validate_markdown_source(body: str, source: Path) -> None:
    raw_html = RAW_HTML_RE.search(body)
    if raw_html:
        raise ValueError(
            f"{source.name}: rohes HTML ist nicht erlaubt: {raw_html.group(0)[:80]}"
        )

    for heading in HEADING_RE.finditer(body):
        level = len(heading.group(1))
        if level not in {1, 2, 3}:
            raise ValueError(
                f"{source.name}: nur H1, H2 und H3 sind im Artikeltext erlaubt; "
                f"gefunden: H{level}."
            )

    for match in MARKDOWN_IMAGE_RE.finditer(body):
        path = match.group(2).strip().strip("<>")
        # Pages CMS kann Inline-Bilder ohne Alt-Text serialisieren.
        # alt="" bleibt als gültiger dekorativer Alt-Text erhalten.
        validate_image_path(path, source)


def render_markdown(body: str, source: Path, *, required: bool = True) -> str:
    body = body.strip()
    if not body:
        if required:
            raise ValueError(f"{source.name}: Rich-Text-Inhalt ist leer.")
        return ""

    validate_markdown_source(body, source)

    renderer = mistune.create_markdown(escape=True, plugins=["table"])
    rendered = renderer(body)

    validator = RenderedHtmlValidator(source)
    validator.feed(rendered)
    validator.close()

    rendered = IMAGE_PARAGRAPH_RE.sub(
        r'<div class="news-rich-image">\1</div>',
        rendered,
    )
    rendered = rendered.replace(
        "<table>",
        '<div class="news-table-wrapper"><table>',
    )
    rendered = rendered.replace(
        "</table>",
        "</table></div>",
    )
    return rendered


def render_text_block(
    block: dict[str, Any],
    source: Path,
    block_number: int,
) -> str:
    alignment = block.get("alignment", "left")
    if alignment not in ALIGNMENTS:
        raise ValueError(
            f"{source.name}: Textblock {block_number}: ungültige Ausrichtung '{alignment}'."
        )

    body = required_text(block, "body", source)
    html = render_markdown(body, source)
    return (
        f'<section class="news-block news-block--text news-block--text-{alignment}">\n'
        f"{html}\n"
        "</section>"
    )


def render_two_columns_block(
    block: dict[str, Any],
    source: Path,
    block_number: int,
) -> str:
    left = required_text(block, "left", source)
    right = required_text(block, "right", source)

    left_html = render_markdown(left, source)
    right_html = render_markdown(right, source)

    return (
        '<section class="news-block news-block--columns">\n'
        '<div class="news-block__column">\n'
        f"{left_html}\n"
        "</div>\n"
        '<div class="news-block__column">\n'
        f"{right_html}\n"
        "</div>\n"
        "</section>"
    )


def render_event_block(
    block: dict[str, Any],
    source: Path,
    block_number: int,
) -> str:
    title = required_text(block, "title", source)
    event_date = parse_event_date(block.get("date"), source, block_number)
    event_time = parse_event_time(block.get("time"), source, block_number)
    location = optional_text(block, "location", source)
    description = optional_text(block, "description", source)
    description_html = render_markdown(
        description,
        source,
        required=False,
    )

    meta_parts = [
        (
            '<div class="news-event__meta-item">'
            "<dt>Datum</dt>"
            f'<dd><time datetime="{escape(event_date.isoformat(), quote=True)}">'
            f"{escape(display_calendar_date(event_date))}"
            "</time></dd>"
            "</div>"
        )
    ]

    if event_time:
        meta_parts.append(
            '<div class="news-event__meta-item">'
            "<dt>Uhrzeit</dt>"
            f'<dd><time datetime="{escape(event_time, quote=True)}">'
            f"{escape(event_time)} Uhr"
            "</time></dd>"
            "</div>"
        )

    if location:
        meta_parts.append(
            '<div class="news-event__meta-item">'
            "<dt>Ort</dt>"
            f"<dd>{escape(location)}</dd>"
            "</div>"
        )

    description_part = ""
    if description_html:
        description_part = (
            '\n<div class="news-event__description">\n'
            f"{description_html}\n"
            "</div>"
        )

    return (
        '<section class="news-block news-event" aria-label="Eventankündigung">\n'
        '<p class="news-event__label">Eventankündigung</p>\n'
        f'<h2 class="news-event__title">{escape(title)}</h2>\n'
        '<dl class="news-event__meta">\n'
        + "\n".join(meta_parts)
        + "\n</dl>"
        + description_part
        + "\n</section>"
    )


def render_divider_block() -> str:
    return '<hr class="news-block news-block--divider"/>'


def render_spacer_block(
    block: dict[str, Any],
    source: Path,
    block_number: int,
) -> str:
    size = block.get("size", "medium")
    if size not in SPACER_SIZES:
        raise ValueError(
            f"{source.name}: Abstandsblock {block_number}: ungültige Größe '{size}'."
        )

    return (
        f'<div class="news-block news-block--spacer news-block--spacer-{size}" '
        'aria-hidden="true"></div>'
    )


def render_sections(
    sections: Any,
    source: Path,
) -> str:
    if not isinstance(sections, list) or not sections:
        raise ValueError(
            f"{source.name}: 'sections' muss mindestens einen Inhaltsblock enthalten."
        )

    rendered: list[str] = []
    has_content = False

    for index, block in enumerate(sections, start=1):
        if not isinstance(block, dict):
            raise ValueError(
                f"{source.name}: Block {index} muss ein YAML-Objekt sein."
            )

        block_type = block.get("type")
        if block_type not in BLOCK_TYPES:
            raise ValueError(
                f"{source.name}: Block {index} hat unbekannten Typ '{block_type}'."
            )

        if block_type == "text":
            rendered.append(render_text_block(block, source, index))
            has_content = True
        elif block_type == "two_columns":
            rendered.append(render_two_columns_block(block, source, index))
            has_content = True
        elif block_type == "event":
            rendered.append(render_event_block(block, source, index))
            has_content = True
        elif block_type == "divider":
            rendered.append(render_divider_block())
        elif block_type == "spacer":
            rendered.append(render_spacer_block(block, source, index))

    if not has_content:
        raise ValueError(
            f"{source.name}: Artikel benötigt mindestens einen Text-, Zwei-Spalten- "
            "oder Eventblock."
        )

    return "\n".join(rendered)


def render_article_content(
    data: dict[str, Any],
    legacy_body: str,
    source: Path,
) -> str:
    sections = data.get("sections")

    if sections is not None:
        if legacy_body:
            raise ValueError(
                f"{source.name}: 'sections' und alter Markdown-Body dürfen nicht gleichzeitig verwendet werden."
            )
        return render_sections(sections, source)

    # Rückwärtskompatibilität: alte Artikel mit Markdown-Body bleiben gültig.
    if not legacy_body:
        raise ValueError(
            f"{source.name}: Artikel enthält weder 'sections' noch einen Markdown-Body."
        )

    legacy_html = render_markdown(legacy_body, source)
    return (
        '<section class="news-block news-block--text news-block--text-left">\n'
        f"{legacy_html}\n"
        "</section>"
    )


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
    data, legacy_body = parse_frontmatter(source)
    slug = source.stem
    validate_slug(slug, source)

    title = required_text(data, "title", source)
    image = required_text(data, "image", source)
    image_alt = required_text(data, "image_alt", source)
    publish_at = parse_publish_at(data.get("publish_at"), source)

    validate_image_path(image, source)
    body_html = render_article_content(data, legacy_body, source)

    raw_summary = data.get("summary")
    if raw_summary is None or (
        isinstance(raw_summary, str) and not raw_summary.strip()
    ):
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


def display_calendar_date(value: date) -> str:
    return f"{value.day}. {GERMAN_MONTHS[value.month]} {value.year}"


def display_date(value: datetime) -> str:
    return display_calendar_date(value.date())


def render_template(path: Path, values: dict[str, str]) -> str:
    template = path.read_text(encoding="utf-8")
    result = template

    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)

    unresolved = PLACEHOLDER_RE.findall(result)
    if unresolved:
        raise ValueError(
            f"{path.name}: nicht ersetzte Template-Platzhalter: "
            f"{', '.join(sorted(set(unresolved)))}"
        )

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
        r"\s*<url>\s*<loc>https://www\.ttf-laudenbach\.de/pages/"
        r"(?:news/[^<]+|neuigkeiten\.html)</loc>\s*</url>",
        re.MULTILINE,
    )
    cleaned = block_re.sub("", existing)

    blocks = [
        "  <url>\n"
        "    <loc>https://www.ttf-laudenbach.de/pages/neuigkeiten.html</loc>\n"
        "  </url>"
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
        if GENERATED_MARKER in text:
            path.unlink()


def generate(now: datetime) -> None:
    all_articles = load_all_articles()
    published = sorted(
        (
            article
            for article in all_articles
            if article.publish_at <= now
        ),
        key=lambda article: (article.publish_at, article.slug),
        reverse=True,
    )

    article_outputs = {
        f"{article.slug}.html": article_html(article)
        for article in published
    }
    overview = overview_html(published)
    slider = slider_json(published)
    sitemap = sync_sitemap(
        SITEMAP.read_text(encoding="utf-8"),
        published,
    )

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
