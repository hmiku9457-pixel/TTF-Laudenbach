#!/usr/bin/env python3
"""Render real pages locally with Chromium and export a double-clickable visual review.
This is intentionally a screenshot report, not a live or interactive staging site.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from generate_site_navigation import render_custom_pages
from generate_news import load_all_articles, article_html, resolve_now

SIZES = {"desktop": (1440, 900), "mobil": (390, 844)}
MAX_HEIGHT = 14000


@contextmanager
def local_site(root):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def preview_only_pages(root):
    drafts = render_custom_pages(root, drafts_only=True)
    status = {entry["url"].lstrip("/"): "Entwurf – nur Vorschau" for entry in drafts.values()}
    now = resolve_now(None)
    for article in load_all_articles():
        if article.publish_at > now:
            path = root / "pages/news" / (article.slug + ".html")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(article_html(article), encoding="utf-8")
            status[path.relative_to(root).as_posix()] = "Geplante News – nur Vorschau"
    return status


def render_report(root, output, sha, ref, run_url):
    output.mkdir(parents=True, exist_ok=True)
    (output / "bilder").mkdir(exist_ok=True)
    status = preview_only_pages(root)
    paths = [root / "index.html", *sorted((root / "pages").rglob("*.html"))]
    rows = []
    with local_site(root) as origin, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for i, path in enumerate(paths):
                rel = path.relative_to(root).as_posix()
                record = {"path": rel, "title": rel, "status": status.get(rel, "Im Website-Build enthalten"), "views": {}}
                for name, (width, height) in SIZES.items():
                    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1, reduced_motion="reduce")
                    context.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin + "/") else route.abort())
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    response = page.goto(origin + "/" + quote(rel, safe="/"), wait_until="networkidle", timeout=30000)
                    if response is None or not response.ok:
                        raise RuntimeError(f"Vorschau nicht ladbar: {rel}")
                    if page.locator("#header-container").count():
                        page.locator("#header-container[data-component-loaded=true]").wait_for(timeout=10000)
                    if page.locator("#footer-container").count():
                        page.locator("#footer-container[data-component-loaded=true]").wait_for(timeout=10000)
                    page.add_style_tag(content="*,*::before,*::after { animation-duration:0s!important; animation-delay:0s!important; transition:none!important; }")
                    page.evaluate("""async () => {
                        document.querySelectorAll('img[loading=lazy]').forEach(img => img.loading='eager');
                        await Promise.race([Promise.all([...document.images].map(img => img.decode().catch(() => {}))),new Promise(resolve=>setTimeout(resolve,3000))]);
                        await document.fonts.ready;
                    }""")
                    record["title"] = page.title() or rel
                    extent = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                    file = f"bilder/{i:03d}-{name}.jpg"
                    # Very long ranking pages remain readable by using a bounded capture.
                    if extent > MAX_HEIGHT:
                        page.screenshot(path=str(output / file), type="jpeg", quality=82, clip={"x":0,"y":0,"width":width,"height":min(MAX_HEIGHT, extent)}, animations="disabled", timeout=30000)
                    else:
                        page.screenshot(path=str(output / file), type="jpeg", quality=82, full_page=True, animations="disabled", timeout=30000)
                    record["views"][name] = {"file":file,"clipped":extent>MAX_HEIGHT,"errors":errors}
                    context.close()
                rows.append(record)
                print(f"Vorschau: {rel} (Desktop/Mobil)", flush=True)
        finally:
            browser.close()

    def item(index, row):
        badges = escape(row["status"])
        figures = []
        for name, view in row["views"].items():
            caption = "Desktop · 1440 px" if name == "desktop" else "Mobil · 390 px"
            if view["clipped"]:
                caption += " · oberer Ausschnitt"
            if view["errors"]:
                caption += " · JavaScript-Hinweis (siehe Bericht)"
            src = escape(view["file"], quote=True)
            figures.append(f'<figure data-size="{name}"><figcaption>{caption}</figcaption><a href="{src}" target="_blank"><img loading="lazy" src="{src}" alt="{escape(row["title"],quote=True)} – {name}"/></a></figure>')
        return f'<section id="seite-{index}" data-title="{escape(row["title"]+" "+row["path"],quote=True)}"><h2>{escape(row["title"])}</h2><p>{badges} · <code>{escape(row["path"])}</code></p><div class="views">{"".join(figures)}</div></section>'

    options = "".join(f'<option value="seite-{i}">{escape(row["title"])} · {escape(row["path"])}</option>' for i,row in enumerate(rows))
    content = "".join(item(i,row) for i,row in enumerate(rows))
    html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TTF – CMS-Vorschau</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font:16px system-ui,sans-serif;background:#eef2f6;color:#172638}}header{{background:#fff;padding:18px max(18px,calc((100% - 1250px)/2));position:sticky;top:0;z-index:2;border-bottom:1px solid #c8d1dc}}h1{{margin:0 0 6px;font-size:1.35rem}}h2{{font-size:1.12rem;margin:0}}p{{margin:8px 0;overflow-wrap:anywhere}}main{{max-width:1250px;margin:auto;padding:18px}}.toolbar{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px;align-items:center}}select,button{{font:inherit;padding:8px;border:1px solid #aebdcb;background:white;color:inherit;border-radius:6px;max-width:100%}}section{{background:white;border-radius:10px;padding:16px;margin-bottom:20px;scroll-margin-top:220px}}.views{{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:16px}}figure{{margin:0;min-width:0}}figcaption{{font-size:.9rem;color:#42576d;margin:8px 0}}img{{display:block;width:100%;height:auto;border:1px solid #aebdcb}}body[data-mode=desktop] .views,body[data-mode=mobil] .views{{display:block}}body[data-mode=desktop] figure[data-size=mobil],body[data-mode=mobil] figure[data-size=desktop]{{display:none}}body[data-mode=mobil] figure{{max-width:390px;margin:auto}}a{{color:#195a96}}@media(max-width:700px){{header{{position:static}}.views{{grid-template-columns:1fr}}}}</style></head>
<body data-mode="both"><header><h1>TTF Laudenbach – visuelle CMS-Vorschau</h1><p>Gespeicherter Stand · {escape(ref)} · <code>{escape(sha[:12])}</code> · {len(rows)} Seiten · <a href="{escape(run_url,quote=True)}">GitHub-Prüflauf</a></p><p>Keine Live-Veröffentlichung. Statische Bildschirmaufnahmen; externe Dienste sind deaktiviert. Bild anklicken für Originalgröße.</p><div class="toolbar"><label for="page">Seite:</label><select id="page">{options}</select><label for="mode">Ansicht:</label><select id="mode"><option value="both">Desktop und Mobil</option><option value="desktop">Desktop</option><option value="mobil">Mobil</option></select></div></header><main>{content}</main>
<script>document.getElementById('page').addEventListener('change',e=>document.getElementById(e.target.value).scrollIntoView());document.getElementById('mode').addEventListener('change',e=>document.body.dataset.mode=e.target.value);</script></body></html>"""
    (output / "Vorschau.html").write_text(html, encoding="utf-8")
    (output / "bericht.json").write_text(json.dumps({"sha":sha,"ref":ref,"pages":rows}, ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = render_report(args.site.resolve(), args.output.resolve(), os.environ.get("GITHUB_SHA","lokal"), os.environ.get("GITHUB_REF_NAME","lokal"), os.environ.get("GITHUB_SERVER_URL","https://github.com")+"/"+os.environ.get("GITHUB_REPOSITORY","hmiku9457-pixel/TTF-Laudenbach")+"/actions/runs/"+os.environ.get("GITHUB_RUN_ID",""))
    warnings = sum(bool(v["errors"]) for row in rows for v in row["views"].values())
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write(f"## Visuelle Vorschau\n\n{len(rows)} Seiten, jeweils Desktop und Mobil. Artefakt **cms-visuelle-vorschau** herunterladen, entpacken und **Vorschau.html** öffnen. {warnings} Ansichten mit JavaScript-Hinweisen (Details in bericht.json).\n")


if __name__ == "__main__":
    main()
