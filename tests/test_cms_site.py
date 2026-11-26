import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/python"))
from generate_site import web, text, render_training, load, link_groups
from generate_site_extra import pdf, page_sections
from generate_site import SOURCE


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


if __name__ == "__main__":
    unittest.main()
