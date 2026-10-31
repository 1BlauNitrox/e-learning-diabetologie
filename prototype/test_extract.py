"""Tests for the extraction prototype.

Run from the repository root: python -m unittest discover prototype
The tests on the module are skipped if the raw data is not in data/raw/.
"""

import re
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import extract

EXPORT = Path(__file__).resolve().parent.parent / "data" / "raw" / "2026 E-Learning Diabetologie" / "Ketonkörper"


class CleanTest(unittest.TestCase):
    def test_percent_encoding(self):
        self.assertEqual(extract.clean("Acetoacetat (Anteil etwa 20^%^)"), "Acetoacetat (Anteil etwa 20%)")

    def test_line_breaks_and_tabs(self):
        self.assertEqual(extract.clean("Bis 0,6 mmol/l\t\tNormalbefund\r\n\rÜber 3 mmol/l"), "Bis 0,6 mmol/l\tNormalbefund\nÜber 3 mmol/l")

    def test_click_hint(self):
        self.assertEqual(extract.clean("Nutzung - Hier klicken -"), "Nutzung")

    def test_boilerplate(self):
        for text in ["Diabetologie online lernen | Ketonkörper", "Diabetologie online lernen l Ketonkörper", "Weiter", "Beide Bilder © articulate"]:
            self.assertEqual(extract.clean(text), "", text)

    def test_email_and_player_variables(self):
        self.assertEqual(extract.clean("eine Mail: autor@example.org"), "eine Mail:")
        self.assertEqual(extract.clean("%_player.5X8JOp5iKWb.$PercentScore% %"), "")

    def test_umlauts_kept(self):
        self.assertEqual(extract.clean("Ketonkörper – Maßnahmen, ß-OHB"), "Ketonkörper – Maßnahmen, ß-OHB")


class LoadJsTest(unittest.TestCase):
    def test_unescapes_javascript_string(self):
        content = "﻿window.globalProvideData('slide', '{\"t\":\"it\\'s \\u00df \\\\\"x\\\\\"\"}');"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "slide.js"
            path.write_text(content, encoding="utf-8")
            self.assertEqual(extract.load_js(path), {"t": "it's ß \"x\""})


class ReadingOrderTest(unittest.TestCase):
    def test_rows_top_to_bottom_then_left_to_right(self):
        def box(obj_id, x, y):
            return {"id": obj_id, "xPos": x, "yPos": y, "textLib": [{"vartext": {"blocks": [{"spans": [{"text": obj_id}]}]}}]}

        layer = {"objects": [box("bottom", 0, 300), box("right", 600, 90), box("left", 0, 95)]}
        self.assertEqual([t["text"] for t in extract.layer_texts(layer)], ["left", "right", "bottom"])


@unittest.skipUnless(EXPORT.is_dir(), "raw data not available")
class KetonkoerperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = extract.extract(EXPORT)
        cls.slides = {s["slide_id"]: s for scene in cls.result["scenes"] for s in scene["slides"]}
        cls.texts = [t["text"] for s in cls.slides.values() for layer in s["layers"] for t in layer["texts"]]

    def test_structure(self):
        # 44 slides minus the unreachable scene 11 (docs/0003-data-analysis.md, 3.1 and 3.7).
        self.assertEqual(len(self.result["scenes"]), 10)
        self.assertEqual(len(self.slides), 43)
        self.assertEqual(self.result["excluded"]["scenes"], ["5kgPiZDizLV"])

    def test_layers(self):
        kinds = Counter(layer["kind"] for s in self.slides.values() for layer in s["layers"])
        self.assertEqual(kinds, {"base": 43, "popup": 29, "feedback": 27})
        hidden = {layer["slide_id"] for layer in self.result["excluded"]["layers"]}
        self.assertEqual(hidden, {"5wCsNDPjQg7", "5h1vmZbo2CA", "5ybdvscaQS3"})

    def test_questions(self):
        questions = self.result["questions"]
        self.assertEqual(sum(q["in_quiz"] for q in questions), 10)
        self.assertEqual(Counter(q["type"] for q in questions if q["in_quiz"]), {"multipleresponse": 5, "matching": 4, "sequence": 1})
        check = next(q for q in questions if not q["in_quiz"])
        self.assertEqual(check["slide_id"], "5ovCLr88si4")
        self.assertEqual(len(check["correct"]), 5)

    def test_question_details(self):
        by_slide = {q["slide_id"]: q for q in self.result["questions"]}
        self.assertEqual(by_slide["5aEzTIHzw13"]["correct"], ["ß-Hydroxybutyrat", "Acetoacetat", "Aceton"])
        self.assertIn("Welche der Begriffe bezeichnen Ketonkörper?", by_slide["5aEzTIHzw13"]["prompt"])
        self.assertEqual(by_slide["6IQ11Yd93fa"]["correct_order"][:2], ["Niedrige Glukosespiegel", "Niedrige Spiegel von Oxalacetat"])
        pairs = by_slide["5xxIIRpI1Lg"]["correct_pairs"]
        self.assertIn({"item": "Nachweis im Urin", "target": "Acetoacetat"}, pairs)
        self.assertTrue(all(p["target"] is None for p in by_slide["6l9ql5Y9GLc"]["correct_pairs"]))

    def test_reading_order(self):
        base = [t["text"] for t in self.slides["5cxhcjlTRsl"]["layers"][0]["texts"]]
        self.assertEqual(base[:3], ["Bewertung der Ketonkörpermessung", "Acetoacetat (Messung im Urin)", "ß-Hydroxybutyrat (Messung im Serum)"])

    def test_clean_text(self):
        joined = "\n".join(self.texts)
        self.assertNotIn("^%^", joined)
        self.assertNotIn("Diabetologie online lernen", joined)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.", joined))
        self.assertIn("Ketonkörper", joined)

    def test_every_text_has_provenance(self):
        for slide_id, slide in self.slides.items():
            for layer in slide["layers"]:
                self.assertTrue(layer["kind"] == "base" or layer["layer_id"])
                for text in layer["texts"]:
                    self.assertTrue(text["object_id"], slide_id)


if __name__ == "__main__":
    unittest.main()
