import sys
from pathlib import Path
import unittest
import json
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/python"))
from generate_site import web, text, render_training, load, link_groups
from generate_site_extra import pdf, page_sections
from generate_site import SOURCE
from generate_site_media import render_team_info
from generate_gallery import build_gallery_data
from generate_site_layout import reorder
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

    def test_layout_reorder_and_protection(self):
        page = '<main><!-- LAYOUT:start:a -->A<!-- LAYOUT:end:a --><!-- LAYOUT:start:b -->B<!-- LAYOUT:end:b --></main>'
        spec = {"path": "test", "keys": ["a", "b"], "inner": True}
        result = reorder(page, spec, {"order": [{"area": "custom"}, {"area": "b"}]}, "C")
        self.assertIn("C</div>\nB\nA", result)
        self.assertNotIn("LAYOUT:", result)
        with self.assertRaises(ValueError):
            reorder(page, spec, {"order": [{"area": "b"}, {"area": "b"}]}, "")

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


if __name__ == "__main__":
    unittest.main()
