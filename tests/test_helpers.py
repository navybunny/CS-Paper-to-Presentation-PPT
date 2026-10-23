"""Tests use synthetic OOXML only; no paper, credential, or private template.

SPDX-License-Identifier: MIT
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "cs-paper-to-presentation-ppt"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deck_module = load_module("paper_talk_inspection", SKILL / "scripts" / "inspect_deck.py")
install_module = load_module("paper_talk_install", ROOT / "scripts" / "install.py")

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def make_fixture(path):
    # Intentionally put physical slide2 first and use an absolute relationship target.
    presentation = f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="256" r:id="rIdB"/><p:sldId id="257" r:id="rIdA"/></p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>'
    relationships = f'<Relationships xmlns="{PKG}"><Relationship Id="rIdA" Type="{R}/slide" Target="slides/slide1.xml"/><Relationship Id="rIdB" Type="{R}/slide" Target="/ppt/slides/slide2.xml"/></Relationships>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", relationships)
        for n in [1, 2]:
            label = "Later [2]" if n == 1 else "First [1]"
            footnote = "[1] Synthetic citation" if n == 2 else ""
            slide = f'<p:sld xmlns:p="{P}" xmlns:a="{A}" show="{0 if n == 1 else 1}"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="body"/></p:nvSpPr><p:txBody><a:p><a:r><a:rPr sz="2400"><a:latin typeface="Arial"/></a:rPr><a:t>{label}</a:t></a:r></a:p></p:txBody></p:sp><p:sp><p:txBody><a:p><a:r><a:t>{footnote}</a:t></a:r></a:p></p:txBody></p:sp><p:pic/></p:spTree></p:cSld></p:sld>'
            z.writestr(f"ppt/slides/slide{n}.xml", slide)
            z.writestr(f"ppt/slides/_rels/slide{n}.xml.rels", f'<Relationships xmlns="{PKG}"><Relationship Id="rIdN" Type="{R}/notesSlide" Target="../notesSlides/notesSlide{n}.xml"/></Relationships>')
            note = f'<p:notes xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:txBody><a:p><a:r><a:t>Script {n}</a:t></a:r></a:p></p:txBody></p:sp><p:sp><p:nvSpPr><p:nvPr><p:ph type="sldNum"/></p:nvPr></p:nvSpPr><p:txBody><a:p><a:r><a:t>999</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:notes>'
            z.writestr(f"ppt/notesSlides/notesSlide{n}.xml", note)


class InspectionTests(unittest.TestCase):
    def test_actual_order_notes_and_hidden_slide(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.pptx"
            make_fixture(p)
            result = deck_module.inspect(p)
            self.assertEqual(result["slide_count"], 2)
            self.assertTrue(result["slides"][0]["part"].endswith("slide2.xml"))
            self.assertIn("First [1]", result["slides"][0]["text"])
            self.assertEqual(result["slides"][0]["notes"], "Script 2")
            self.assertNotIn("999", result["slides"][0]["notes"])
            self.assertFalse(result["slides"][0]["hidden"])
            self.assertTrue(result["slides"][1]["hidden"])
            self.assertEqual(result["slides"][0]["font_counts"]["Arial"], 1)
            self.assertEqual(result["slides"][0]["images"], 1)
            self.assertEqual(result["warnings"], [{"slide": 2, "kind": "check_visible_reference_numbers", "numbers": ["2"]}])

    def test_cli_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.pptx"
            make_fixture(p)
            original = p.read_bytes()
            r = subprocess.run([sys.executable, str(SKILL / "scripts" / "inspect_deck.py"), str(p), "--output", str(p)], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(p.read_bytes(), original)

    def test_cli_refuses_to_overwrite_existing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.pptx"
            make_fixture(p)
            report = Path(tmp) / "report.json"
            report.write_text("keep", encoding="utf-8")
            r = subprocess.run([sys.executable, str(SKILL / "scripts" / "inspect_deck.py"), str(p), "--output", str(report)], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(report.read_text(encoding="utf-8"), "keep")


class InstallationTests(unittest.TestCase):
    def test_install_contains_required_files_and_no_personal_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = install_module.install(Path(tmp) / "skills")
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "references" / "workflow.md").is_file())
            self.assertTrue((target / "agents" / "openai.yaml").is_file())
            self.assertFalse(list(target.rglob("*.pptx")))
            self.assertFalse(list(target.rglob("*.pdf")))
            self.assertFalse(list(target.rglob("*.pyc")))

    def test_existing_install_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            target = install_module.install(dest)
            entry = target / "SKILL.md"
            entry.write_text("user modified", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                install_module.install(dest)
            self.assertEqual(entry.read_text(encoding="utf-8"), "user modified")

    def test_codex_home_is_honored(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"CODEX_HOME": tmp}):
            self.assertEqual(install_module.default_destination(), Path(tmp) / "skills")


if __name__ == "__main__":
    unittest.main()
