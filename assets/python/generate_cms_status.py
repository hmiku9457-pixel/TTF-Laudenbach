"""Generate a verifiable build marker into an artifact, never a claimed live status in source."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess


def build_status(output, mode, sha, ref, run_url, built_at=None):
    if mode not in ("preview", "production") or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Ungültiger Buildstand")
    stamp = built_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = {"mode":mode,"commit":sha,"branch":ref,"built_at_utc":stamp,"workflow_run":run_url}
    (output / "cms-stand.json").write_text(json.dumps(status, ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    title = "Vorschau – nicht veröffentlicht" if mode == "preview" else "Stand des bereitgestellten Website-Artefakts"
    explanation = ("Diese Dateien dienen ausschließlich zur Prüfung. Eine Vorschau bestätigt keine Live-Veröffentlichung." if mode == "preview" else
        "Wenn diese Seite über www.ttf-laudenbach.de aufgerufen wird, gehört sie zum derzeit ausgelieferten Website-Artefakt. Der Zeitpunkt ist der Buildzeitpunkt, nicht der exakte Veröffentlichungszeitpunkt.")
    html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow"><title>TTF – Veröffentlichungsstand</title>
<style>body{{font:16px system-ui,sans-serif;color:#172638;background:#eef2f6;padding:24px;max-width:850px;margin:auto}}main{{background:white;padding:24px;border-radius:12px}}h1{{font-size:1.5rem}}dt{{font-weight:bold;margin-top:18px}}dd{{margin:5px 0;overflow-wrap:anywhere}}a{{color:#195a96}}code{{font-size:.95rem}}</style></head><body><main><h1>{title}</h1><p>{explanation}</p>
<dl><dt>Stand (UTC)</dt><dd>{escape(stamp)}</dd><dt>Branch</dt><dd>{escape(ref)}</dd><dt>Git-Commit</dt><dd><a href="https://github.com/hmiku9457-pixel/TTF-Laudenbach/commit/{sha}"><code>{sha}</code></a></dd><dt>Prüfung und Veröffentlichung</dt><dd><a href="{escape(run_url,quote=True)}">Zugehörigen GitHub-Actions-Lauf öffnen</a></dd></dl>
<p>Eine gespeicherte Änderung kann noch in Prüfung sein oder bei einem Fehler nicht veröffentlicht worden sein. Aktuellen Workflow prüfen, bevor der Inhalt erneut bearbeitet wird.</p></main></body></html>"""
    (output / "redaktionsstatus.html").write_text(html, encoding="utf-8")
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--mode",choices=("preview","production"),required=True)
    parser.add_argument("--ref",required=True)
    args = parser.parse_args()
    sha = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    run_url = os.environ["GITHUB_SERVER_URL"]+"/"+os.environ["GITHUB_REPOSITORY"]+"/actions/runs/"+os.environ["GITHUB_RUN_ID"]
    build_status(args.output,args.mode,sha,args.ref,run_url)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a",encoding="utf-8") as f:
            f.write(f"built_sha={sha}\n")


if __name__ == "__main__":
    main()
