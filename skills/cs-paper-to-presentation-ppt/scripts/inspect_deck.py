"""Read-only PPTX extraction in presentation order; Python 3.10+, standard library only.

SPDX-License-Identifier: MIT
"""
import argparse
import collections
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def resolve(base, target):
    return target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def relations(z, part):
    name = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
    return list(ET.fromstring(z.read(name))) if name in z.namelist() else []


def paragraphs(element):
    return "\n".join("".join(t.text or "" for t in p.findall(".//a:t", NS)) for p in element.findall(".//a:p", NS))


def inspect(path):
    slides, warnings = [], []
    with zipfile.ZipFile(path) as z:
        pres_part = "ppt/presentation.xml"
        pres = ET.fromstring(z.read(pres_part))
        mapping = {r.get("Id"): resolve(pres_part, r.get("Target")) for r in relations(z, pres_part)}
        size = pres.find("p:sldSz", NS)
        for index, node in enumerate(pres.findall("p:sldIdLst/p:sldId", NS), 1):
            part = mapping[node.get("{" + NS["r"] + "}id")]
            root = ET.fromstring(z.read(part))
            text = paragraphs(root)
            note = ""
            for rel in relations(z, part):
                if rel.get("Type", "").endswith("/notesSlide"):
                    nr = ET.fromstring(z.read(resolve(part, rel.get("Target"))))
                    for sp in nr.findall(".//p:sp", NS):
                        ph = sp.find(".//p:ph", NS)
                        if ph is not None and ph.get("type") == "body":
                            note = paragraphs(sp)
            shapes = []
            cited, supplied = set(), set()
            for sp in root.findall(".//p:sp", NS):
                value = paragraphs(sp)
                ids = set(re.findall(r"\[(\d+)\]", value))
                if re.match(r"^\s*\[\d+\]", value):
                    supplied.update(ids)
                else:
                    cited.update(ids)
                name = sp.find(".//p:cNvPr", NS)
                xf = sp.find("p:spPr/a:xfrm", NS)
                shapes.append({"name": name.get("name") if name is not None else "", "text": value, "geometry_xml": ET.tostring(xf, encoding="unicode") if xf is not None else None})
            missing = sorted(cited - supplied, key=int)
            if missing:
                warnings.append({"slide": index, "kind": "check_visible_reference_numbers", "numbers": missing})
            if not note.strip():
                warnings.append({"slide": index, "kind": "empty_notes_may_be_intentional"})
            fonts = collections.Counter(x.get("typeface") for x in root.findall(".//a:latin", NS) if x.get("typeface"))
            sizes = collections.Counter(x.get("sz") for x in root.findall(".//a:rPr", NS) if x.get("sz"))
            slides.append({"number": index, "part": part, "hidden": root.get("show", "1") in {"0", "false"}, "text": text, "notes": note, "images": len(root.findall(".//p:pic", NS)), "font_counts": dict(fonts), "font_size_hundredth_pt_counts": dict(sizes), "shapes": shapes})
    return {"source": str(path.resolve()), "slide_count": len(slides), "slide_size_emu": size.attrib if size is not None else None, "slides": slides, "warnings": warnings, "limits": "Basic text/package inspection only; no factual, rendering, timing or citation-metadata validation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    skill_root = Path(__file__).resolve().parent.parent
    if output == source or output.is_relative_to(skill_root):
        parser.error("Output must not overwrite the input or write inside the skill package; use the task work directory.")
    if output.exists():
        parser.error("Output already exists; select a new task output path.")
    result = inspect(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"slide_count": result["slide_count"], "warning_count": len(result["warnings"]), "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
