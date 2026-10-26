import json
import struct
import zlib
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import Sandbox  # noqa: E402

from godmode import creative, profiles  # noqa: E402

def _png_1x1() -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixel = bytes([0, 255, 128, 0])  # filter byte + one RGB pixel
    return bytes([0x89]) + b"PNG" + bytes([13, 10, 26, 10]) + chunk(b"IHDR", ihdr) \
        + chunk(b"IDAT", zlib.compress(pixel)) + chunk(b"IEND", b"")


PNG = _png_1x1()


class Creative(Sandbox):
    def setUp(self):
        super().setUp()
        self.img = os.path.join(self.tmp, "p.png")
        with open(self.img, "wb") as fh:
            fh.write(PNG)
        self.brand = {"colors": {"primary": "#1f3a5f", "secondary": "#f4efe6", "accent": "#e07a2e"}, "font_family": "Arial"}

    def variants(self):
        return [
            {"id": "A", "template": "offer-card", "badge": "Free", "headline": "Your new kitchen, planned for free",
             "subhead": "Design consult in York County", "cta": "Book now"},
            {"id": "B", "template": "photo-overlay", "headline": "Built around how you cook", "cta": "Get a quote",
             "image": self.img},
            {"id": "C", "template": "quote", "headline": "Finished early & spotless <3", "subhead": "Sarah K."},
            {"id": "D", "template": "split", "headline": "Six weeks later", "image": self.img, "image2": self.img},
        ]

    def test_every_template_and_format_is_valid_svg(self):
        for v in self.variants():
            for fmt, (w, h) in creative.FORMATS.items():
                svg = creative.render_svg(v, fmt, self.brand, "Alpha & Co")
                root = ET.fromstring(svg)  # well-formed, text escaped
                self.assertEqual((root.get("width"), root.get("height")), (str(w), str(h)), (v["id"], fmt))

    def test_text_is_escaped(self):
        svg = creative.render_svg(self.variants()[2], "1x1", self.brand, "Alpha")
        self.assertIn("&amp;", svg)
        self.assertIn("&lt;3", svg)

    def test_contrast_picks_readable_ink(self):
        self.assertEqual(creative.ink("#1f3a5f"), "#ffffff")
        self.assertEqual(creative.ink("#f4efe6"), "#111827")
        self.assertEqual(creative.ink("#1f3a5f", "#ffcc00"), "#ffcc00")   # brand text kept when readable
        self.assertEqual(creative.ink("#f4efe6", "#ffffff"), "#111827")   # unreadable brand text replaced

    def test_fit_box_respects_height(self):
        size, lines = creative.fit_box("Your new kitchen planned for free in York County", 600, 200, 120, 20, 4)
        self.assertLessEqual(size + size * 1.15 * (len(lines) - 1), 200)

    def test_prohibited_claim_blocks_variant(self):
        p = profiles.load("alpha-remodeling")
        chk = creative.check_variant({"headline": "Guaranteed lowest price in town", "template": "offer-card"}, p)
        self.assertTrue(chk["errors"])

    def test_missing_image_errors(self):
        with self.assertRaises(creative.CreativeError):
            creative.render_svg({"id": "B", "template": "photo-overlay", "headline": "x"}, "1x1", self.brand, "A")
        with self.assertRaises(creative.CreativeError):
            creative.render_svg({"id": "B", "template": "photo-overlay", "headline": "x", "image": "/nope.jpg"},
                                "1x1", self.brand, "A")

    def test_render_brief_writes_files_and_sheet(self):
        brief = {"client": "alpha-remodeling", "concept": "Test concept", "formats": ["1x1", "9x16"],
                 "variants": self.variants() + [{"id": "E", "headline": "Guaranteed lowest price"}]}
        m = creative.render_brief(brief, png=False, out_dir=os.path.join(self.tmp, "out"))
        by = {v["id"]: v for v in m["variants"]}
        self.assertEqual(len(by["A"]["files"]), 2)
        self.assertTrue(by["E"]["errors"])
        self.assertEqual(by["E"]["files"], [])
        self.assertTrue(os.path.exists(os.path.join(m["dir"], "index.html")))
        with open(os.path.join(m["dir"], "manifest.json"), encoding="utf-8") as fh:
            self.assertIn("PAUSED", json.load(fh)["next"])

    def test_unknown_format_rejected(self):
        with self.assertRaises(creative.CreativeError):
            creative.render_brief({"client": "alpha-remodeling", "formats": ["2x3"], "variants": self.variants()},
                                  png=False, out_dir=self.tmp)
