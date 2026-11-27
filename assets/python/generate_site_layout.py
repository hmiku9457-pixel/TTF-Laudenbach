"""Reorder protected sections and insert editorial blocks without losing functions."""
from __future__ import annotations

import json
import re
from generate_site import SOURCE, load, seq
from generate_site_extra import page_sections

SPECS = json.loads(r'''{"home":{"path":"index.html","keys":["news_training","games_contact"],"inner":false},"club":{"path":"pages/unserVerein.html","keys":["current","history","chair_history"],"inner":false},"training":{"path":"pages/aktiverSpielbetrieb.html","keys":["venues_training","teams"],"inner":false},"membership":{"path":"pages/vereinsmitgliedschaft.html","keys":["fees","join"],"inner":true},"sponsors":{"path":"pages/sponsoren.html","keys":["heading","sponsors"],"inner":false},"documents":{"path":"pages/dokumente.html","keys":["heading","documents"],"inner":false},"links":{"path":"pages/links.html","keys":["heading","tt","sports","other","sponsors"],"inner":true}}''')
SECTION = re.compile(r"<!-- LAYOUT:start:([a-z_]+) -->(.*?)<!-- LAYOUT:end:\1 -->", re.S)


def reorder(page, spec, layout, custom=""):
    matches = list(SECTION.finditer(page))
    keys = spec["keys"]
    if [m.group(1) for m in matches] != keys:
        raise ValueError(f'{spec["path"]}: Layout-Bereiche fehlen oder sind doppelt')
    if any(page[a.end():b.start()].strip() and re.sub(r"<!--.*?-->", "", page[a.end():b.start()], flags=re.S).strip()
           for a, b in zip(matches, matches[1:])):
        raise ValueError(f'{spec["path"]}: Inhalt zwischen Layout-Bereichen')
    parts = {m.group(1): m.group(2) for m in matches}
    width = layout.get("width") or "full"
    if width not in ("full", "narrow"):
        raise ValueError("Layout: ungültige Breite")
    css = "box full-width news-article__content" + (" cms-narrow" if width == "narrow" else "")
    def custom_block(html):
        if not html:
            return ""
        block = f'<div class="{css}">{html}</div>'
        return block if spec["inner"] else f'<div class="grid">{block}</div>'

    rendered = []
    used = set()

    if "sections" in layout:
        pending = []
        def flush():
            if pending:
                rendered.append(custom_block(page_sections(pending, SOURCE / "layouts.json")))
                pending.clear()

        for item in seq(layout.get("sections")):
            if not isinstance(item, dict):
                raise ValueError("Layout: Baustein muss ein Objekt sein")
            kind = item.get("type")
            if isinstance(kind, str) and kind.startswith("fixed_"):
                flush()
                area = kind.removeprefix("fixed_")
                if area not in parts:
                    raise ValueError(f'{spec["path"]}: unbekannter fester Bereich: {area}')
                if area not in used:
                    rendered.append(parts[area])
                    used.add(area)
            else:
                pending.append(item)
        flush()
        # The built-in sections are protected against accidental removal.
        for area in keys:
            if area not in used:
                rendered.append(parts[area])
    else:
        # Compatibility with historic layouts before the unified editor.
        parts["custom"] = custom_block(custom)
        order = []
        for row in seq(layout.get("order")):
            area = row.get("area")
            if area not in parts or area in order:
                raise ValueError(f'{spec["path"]}: unbekannter oder doppelter Layout-Bereich: {area}')
            order.append(area)
        order.extend(k for k in [*keys, "custom"] if k not in order)
        rendered.extend(parts[k] for k in order if parts[k])
    result = page[:matches[0].start()] + "\n".join(p for p in rendered if p) + page[matches[-1].end():]
    if "<!-- LAYOUT:" in result:
        raise ValueError("Nicht ersetzter Layout-Platzhalter")
    return result


def apply_layouts(output):
    layouts = load("layouts")
    blocks = None
    for key, spec in SPECS.items():
        target = output / spec["path"]
        layout = layouts.get(key) or {}
        custom = ""
        if "sections" not in layout:
            blocks = load("page_blocks") if blocks is None else blocks
            custom = page_sections(blocks.get(key), SOURCE / "page_blocks.json")
        page = reorder(target.read_text(encoding="utf-8"), spec, layout, custom)
        target.write_text(page, encoding="utf-8")
