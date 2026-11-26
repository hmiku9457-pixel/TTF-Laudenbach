#!/usr/bin/env python3
"""Erzeugt assets/data/gallerie.json aus assets/images/."""
from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import date
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = ROOT / "assets/images"
OUTPUT_FILE = ROOT / "assets/data/gallerie.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
EXCLUDED_DIRECTORIES = {"seo", "news", "gallery", "site"}


def slugify(text: str) -> str:
    value = (
        text.lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def url_for(path: Path) -> str:
    relative = path.relative_to(ROOT)
    return "/" + quote(str(relative).replace("\\", "/"))


def alt_for(path: Path, gallery_title: str) -> str:
    name = re.sub(r"[-_]+", " ", path.stem).strip()
    return f"{gallery_title}: {name}" if name else gallery_title


def image_entry(path: Path, gallery_title: str) -> dict[str, str]:
    return {
        "src": url_for(path),
        "alt": alt_for(path, gallery_title),
    }


def build_manifest_gallery(source: Path) -> dict[str, object]:
    """CMS manifest is authoritative; original images remain for existing URLs."""
    data = json.loads(source.read_text(encoding="utf-8"))
    galleries = []
    ids = set()
    for album in data.get("albums") or []:
        title = album.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Galerie: Albumtitel fehlt")
        id_ = album.get("id") or "cms-" + slugify(title)
        if not isinstance(id_, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", id_) or id_ == "cms-" or id_ in ids:
            raise ValueError("Galerie: eindeutige gültige Album-ID erforderlich")
        ids.add(id_)
        event_date = album.get("date") or ""
        if event_date:
            date.fromisoformat(event_date)
        description = album.get("description") or ""
        if not isinstance(description, str):
            raise ValueError("Galerie: Beschreibung muss Text sein")
        images = []
        for entry in album.get("images") or []:
            value, alt = entry.get("src"), entry.get("alt")
            if not isinstance(value, str) or not isinstance(alt, str) or not alt.strip():
                raise ValueError("Galerie: Bild und Bildbeschreibung erforderlich")
            value = unquote(value)
            if not value.startswith("/assets/images/gallery/") or "\\" in value or any(ord(c) < 32 for c in value):
                raise ValueError("Galerie: ungültiger Bildpfad")
            path = ROOT / value.lstrip("/")
            base = ROOT / "assets/images/gallery"
            if not path.resolve().is_relative_to(base.resolve()) or path.suffix.lower() not in IMAGE_EXTENSIONS or not path.is_file():
                raise ValueError(f"Galerie: Bild fehlt: {value}")
            images.append({"src": quote(value, safe="/-._~"), "alt": alt})
        galleries.append({"id": id_, "title": title, "date": event_date, "description": description, "images": images})
    result = {"defaultGallery": galleries[0]["id"] if galleries else "", "galleries": galleries}
    validate_gallery_data(result)
    return result


def build_gallery_data() -> dict[str, object]:
    manifest = ROOT / 'content/site/albums.json'
    if manifest.is_file():
        return build_manifest_gallery(manifest)
    if not IMAGES_DIR.is_dir():
        raise FileNotFoundError(f"Bilderordner fehlt: {IMAGES_DIR.relative_to(ROOT)}")

    galleries: list[dict[str, object]] = []

    general_title = "Generelle Bilder"
    general_images = sorted(
        (
            file
            for file in IMAGES_DIR.iterdir()
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: path.name.lower(),
    )
    galleries.append(
        {
            "id": "general",
            "title": general_title,
            "images": [image_entry(file, general_title) for file in general_images],
        }
    )

    folders = sorted(
        (
            folder
            for folder in IMAGES_DIR.iterdir()
            if folder.is_dir()
            and folder.name.lower() not in EXCLUDED_DIRECTORIES
            and not folder.name.startswith((".", "_"))
        ),
        key=lambda path: path.name.lower(),
    )

    for folder in folders:
        images = sorted(
            (
                file
                for file in folder.iterdir()
                if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
            ),
            key=lambda path: path.name.lower(),
        )

        if images:
            galleries.append(
                {
                    "id": slugify(folder.name),
                    "title": folder.name,
                    "images": [image_entry(file, folder.name) for file in images],
                }
            )

    ids = [str(gallery["id"]) for gallery in galleries]
    if len(ids) != len(set(ids)):
        raise ValueError("Doppelte Galerie-IDs erkannt.")

    data: dict[str, object] = {
        "defaultGallery": "general",
        "galleries": galleries,
    }
    validate_gallery_data(data)
    return data


def validate_gallery_data(data: dict[str, object]) -> None:
    galleries = data.get("galleries")
    if not isinstance(galleries, list):
        raise ValueError("galleries muss eine Liste sein.")

    for gallery in galleries:
        if not isinstance(gallery, dict):
            raise ValueError("Ungültiger Galerie-Eintrag.")

        images = gallery.get("images")
        if not isinstance(images, list):
            raise ValueError("images muss eine Liste sein.")

        for image in images:
            if not isinstance(image, dict):
                raise ValueError("Ungültiger Bild-Eintrag.")

            src = str(image.get("src", ""))
            alt = str(image.get("alt", ""))
            image_path = ROOT / Path(unquote(src.lstrip("/")))

            if not image_path.is_file():
                raise FileNotFoundError(
                    f"Galeriebild fehlt: {image_path.relative_to(ROOT)}"
                )

            if not alt.strip():
                raise ValueError(
                    f"Leerer Alt-Text: {image_path.relative_to(ROOT)}"
                )


def main() -> int:
    data = build_gallery_data()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"{OUTPUT_FILE.relative_to(ROOT)} erzeugt: "
        f"{len(data['galleries'])} Galerien"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
