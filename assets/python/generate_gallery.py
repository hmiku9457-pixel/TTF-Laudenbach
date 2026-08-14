#!/usr/bin/env python3
"""Erzeugt assets/data/gallerie.json aus assets/images/."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = ROOT / "assets/images"
OUTPUT_FILE = ROOT / "assets/data/gallerie.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
EXCLUDED_DIRECTORIES = {"seo", "news"}


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


def build_gallery_data() -> dict[str, object]:
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
