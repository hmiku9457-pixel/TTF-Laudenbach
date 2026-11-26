import sys
from pathlib import Path
import unittest
import json
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/python"))
from generate_site import web, text, render_training, load, link_groups
from generate_site_extra import pdf, page_sections
from generate_site import SOURCE
from generate_site_media import render_team_info
from generate_gallery import build_gallery_data, build_manifest_gallery
from generate_site_layout import reorder
from generate_cms_status import build_status
from generate_site_legal import imprint_html
from generate_site_navigation import render_custom_pages, render_menu, render_footer, sync_sitemap


class CmsSiteTests(unittest.TestCase):
    def test_unsafe_url(self):
        for value in ("javascript:alert(1)", "https://user@example.com", "https://a.example/\n"):
            with self.assertRaises(ValueError):
                web(value)

    def test_escaping(self):
        self.assertEqual(text("<script>"), "&lt;script&gt;")

    def test_training(self):
        data = load("training")
        result = render_training(data)
        self.assertIn(data["times"][0]["time"], result)
        data["times"][0]["time"] = "99:99"
        with self.assertRaises(ValueError):
            render_training(data)

    def test_documents(self):
        self.assertTrue(pdf(load("documents")["statutes"]).endswith(".pdf"))
        with self.assertRaises(ValueError):
            pdf("/pages/dokumente/../unserVerein.html")

    def test_sponsors_variable_count(self):
        groups = link_groups(load("links"), {"items": [{"name": "Test", "url": "https://example.org"}] * 6})
        self.assertEqual(len(groups[-1]["links"]), 6)

    def test_page_blocks(self):
        html = page_sections([
            {"type": "text", "alignment": "left", "body": "Hallo **Verein**"},
            {"type": "button", "label": "Test", "url": "https://example.org"},
            {"type": "notice", "title": "Achtung", "body": "Testhinweis"},
            {"type": "divider"},
            {"type": "spacer", "size": "small"},
        ], SOURCE / "page_blocks.json")
        self.assertIn("<strong>Verein</strong>", html)
        self.assertIn("https://example.org", html)
        self.assertIn("Testhinweis", html)
        with self.assertRaises(ValueError):
            page_sections([{"type": "button", "label": "Test", "url": "javascript:alert(1)"}], SOURCE / "page_blocks.json")

    def test_optional_team_fields_removed_by_cms(self):
        self.assertEqual(render_team_info(None), "")
        self.assertEqual(render_team_info({}), "")
        self.assertIn("Testname", render_team_info({"captain": "Testname"}))
        with self.assertRaises(ValueError):
            render_team_info("invalid")

    def test_gallery_manifest(self):
        result = build_gallery_data()
        albums = load("albums").get("albums") or []
        self.assertEqual([a["title"] for a in albums], [a["title"] for a in result["galleries"]])
        self.assertEqual(sum(len(a.get("images") or []) for a in albums),
                         sum(len(a["images"]) for a in result["galleries"]))

    def test_gallery_multiple_images(self):
        existing = load("albums")["albums"][0]["images"]
        paths = [e["src"] if isinstance(e, dict) else e for e in existing]
        self.assertGreaterEqual(len(paths), 2)
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "albums.json"
            album = {"title":"Mehrfachupload", "images": [paths[1], paths[0]], "image_descriptions":[{"src":paths[0],"alt":"Individuelle Beschreibung"}]}
            source.write_text(json.dumps({"albums":[album]}), encoding="utf-8")
            images = build_manifest_gallery(source)["galleries"][0]["images"]
            self.assertEqual([x["src"] for x in images], [paths[1],paths[0]])
            self.assertEqual(images[0]["alt"],"Mehrfachupload – Foto 1")
            self.assertEqual(images[1]["alt"],"Individuelle Beschreibung")
            album["images"] = [paths[1]]
            source.write_text(json.dumps({"albums":[album]}), encoding="utf-8")
            self.assertEqual(len(build_manifest_gallery(source)["galleries"][0]["images"]),1)
            album["images"] = [{"src":paths[0],"alt":"Alter Alt-Text"}]
            album.pop("image_descriptions")
            source.write_text(json.dumps({"albums":[album]}), encoding="utf-8")
            self.assertEqual(build_manifest_gallery(source)["galleries"][0]["images"][0]["alt"],"Alter Alt-Text")
            for invalid in ([paths[0],paths[0]],["/assets/images/gallery/../test.jpg"]):
                album["images"] = invalid
                source.write_text(json.dumps({"albums":[album]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    build_manifest_gallery(source)

    def test_layout_reorder_and_protection(self):
        page = '<main><!-- LAYOUT:start:a -->A<!-- LAYOUT:end:a --><!-- LAYOUT:start:b -->B<!-- LAYOUT:end:b --></main>'
        spec = {"path": "test", "keys": ["a", "b"], "inner": True}
        result = reorder(page, spec, {"order": [{"area": "custom"}, {"area": "b"}]}, "C")
        self.assertIn("C</div>\nB\nA", result)
        self.assertNotIn("LAYOUT:", result)
        with self.assertRaises(ValueError):
            reorder(page, spec, {"order": [{"area": "b"}, {"area": "b"}]}, "")

    def test_additional_page_blocks(self):
        with patch("generate_site_extra.local", return_value="/assets/images/site/test.png"):
            html = page_sections([
                {"type":"heading","title":"Überschrift & mehr"},
                {"type":"three_columns","left":"**Links**","middle":"Mitte","right":"Rechts"},
                {"type":"gallery","images":[{"src":"/assets/images/site/test.png","alt":"Testbild"}]},
            ], SOURCE / "page_blocks.json")
        self.assertIn("Überschrift &amp; mehr", html)
        self.assertIn("news-block--three", html)
        self.assertEqual(html.count('class="news-block__column"'),3)
        self.assertIn("<strong>Links</strong>", html)
        self.assertIn('alt="Testbild"', html)
        self.assertIn("cms-image-row", html)

    def test_custom_page_publish_delete_and_navigation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "src"
            source.mkdir()
            output = root / "out"
            output.mkdir()
            data = {"title": "Test & Verein", "published": True, "auto_menu": True,
                    "sections": [{"type": "heading", "title": "Willkommen"}]}
            (source / "test.json").write_text(json.dumps(data), encoding="utf-8")
            (source / "draft.json").write_text(json.dumps({"title": "Entwurf", "published": False}), encoding="utf-8")
            pages = render_custom_pages(output, source)
            self.assertTrue((output / "pages/individuell/test.html").is_file())
            self.assertFalse((output / "pages/individuell/draft.html").exists())
            drafts = render_custom_pages(output, source, drafts_only=True)
            self.assertTrue((output / "pages/individuell/draft.html").exists())
            self.assertEqual(set(drafts), {"content/custom-pages/draft.json"})
            self.assertFalse(drafts["content/custom-pages/draft.json"]["auto_menu"])
            self.assertIn("Test &amp; Verein", (output / "pages/individuell/test.html").read_text())
            ref = {"target": "custom", "custom_page": "content/custom-pages/test.json"}
            menu = render_menu([ref], pages, {})
            self.assertEqual(menu.count("/pages/individuell/test.html"), 1)
            self.assertNotIn("test.html", render_menu([ref], {}, {}))
            sitemap = output / "sitemap.xml"
            sitemap.write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
            sync_sitemap(sitemap, pages)
            self.assertIn("/pages/individuell/test.html", sitemap.read_text())
            sync_sitemap(sitemap, {})
            self.assertNotIn("test.html", sitemap.read_text())
            footer = render_footer({"footer": [], "show_sponsors": False}, pages, {}, {"items": []})
            for name in ("kontakt", "impressum", "datenschutz"):
                self.assertIn(f"/pages/footer/{name}.html", footer)

    def test_build_status_distinguishes_preview_and_production(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sha = "a"*40
            preview = build_status(root,"preview",sha,"cms-gesamtumbau","https://github.com/example/run", "2026-11-26T12:00:00+00:00")
            self.assertEqual(preview["mode"],"preview")
            self.assertIn("nicht veröffentlicht", (root/"redaktionsstatus.html").read_text())
            production = build_status(root,"production",sha,"main","https://github.com/example/run")
            self.assertEqual(production["commit"],sha)
            self.assertEqual(json.loads((root/"cms-stand.json").read_text())["mode"],"production")
            with self.assertRaises(ValueError):
                build_status(root,"production","invalid","main","https://github.com/example/run")

    def test_legal_fields(self):
        legal = load("legal")
        html = imprint_html(legal["imprint"])
        self.assertIn("mailto:", html)
        self.assertNotIn("[[", html)
        if not legal["imprint"].get("register_number"):
            self.assertNotIn("<h2>Vereinsregister</h2>", html)
        invalid = dict(legal["imprint"], register_court="Test", register_number="")
        with self.assertRaises(ValueError):
            imprint_html(invalid)


if __name__ == "__main__":
    unittest.main()
