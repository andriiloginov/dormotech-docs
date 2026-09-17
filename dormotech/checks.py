"""The four checks. Each exists because that exact failure already shipped once.

  palette  — a colour that is not a token
  glyphs   — a character Instrument Sans cannot render, which silently pulls
             a fallback font into the PDF
  pdf      — wrong page box, a non-brand embedded font, or a missing format
  overflow — content past the page edge, or a block collapsed to nothing
             (run inside the browser during the build, see build.py)
"""
import json
import re
from pathlib import Path

from fontTools.ttLib import TTFont
import pypdf

from . import tokens

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
# .woff, not .woff2: fontTools cannot open woff2 without the brotli extension.
FONT = ROOT / "assets" / "fonts" / "instrument-sans-latin-400-normal.woff"


def check_palette():
    color = tokens.load("color.json")
    allowed_hex = {v["hex"].upper() for v in color["palette"].values()}
    allowed_hex |= {v["hex"].upper() for v in color["chrome"].values()}
    allowed_hex.add("#17514E")  # header gradient mid stop, declared in components.css

    allowed_rgba = {v.replace(" ", "") for k, v in color["derived"].items()
                    if not k.startswith("$")}
    allowed_rgba |= {f"rgba(255,255,255,{a})" for a in (".5", ".7", ".85")}

    problems = []
    for f in sorted(DIST.glob("*.html")):
        css = f.read_text(encoding="utf-8").split("</style>")[0]
        for h in {m.upper() for m in re.findall(r"#[0-9a-fA-F]{6}\b", css)}:
            if h not in allowed_hex:
                problems.append(f"{f.name}: off-palette hex {h}")
        for r in {m.replace(" ", "") for m in re.findall(r"rgba\([^)]+\)", css)}:
            if r not in allowed_rgba:
                problems.append(f"{f.name}: undocumented tint {r}")
    return problems, "palette: only tokens used"


def check_glyphs():
    cmap = set(TTFont(FONT).getBestCmap().keys())
    problems = []
    for f in sorted(DIST.glob("*.html")):
        body = f.read_text(encoding="utf-8").split("</style>", 1)[-1]
        text = re.sub(r"<[^>]+>", "", body)
        missing = sorted({c for c in text if not c.isspace() and ord(c) not in cmap})
        for c in missing:
            problems.append(f"{f.name}: U+{ord(c):04X} {c!r} not in Instrument Sans")
    return problems, "glyphs: every character covered by Instrument Sans"


def check_pdf():
    expected = {k: (v["width"], v["height"]) for k, v in tokens.formats().items()}
    problems, seen = [], set()

    for f in sorted(DIST.glob("*.pdf")):
        fmt = f.stem.rsplit("-", 1)[-1]
        seen.add(fmt)
        reader = pypdf.PdfReader(str(f))

        if fmt in expected:
            want_w, want_h = expected[fmt]
            for i, p in enumerate(reader.pages, 1):
                w, h = float(p.mediabox.width), float(p.mediabox.height)
                if abs(w - want_w) > 1 or abs(h - want_h) > 1:
                    problems.append(
                        f"{f.name} page {i}: {w:.0f}x{h:.0f}pt, expected {want_w}x{want_h}pt")

        fonts = set()
        for p in reader.pages:
            for obj in (p.get("/Resources", {}).get("/Font", {}) or {}).values():
                base = obj.get_object().get("/BaseFont")
                if base:
                    fonts.add(str(base).split("+")[-1])
        stray = {x for x in fonts if not x.startswith("InstrumentSans")}
        if stray:
            problems.append(f"{f.name}: non-brand font embedded: {', '.join(sorted(stray))}")

    for missing in set(expected) - seen:
        problems.append(f"missing format {missing} — every document ships in both")

    return problems, "pdf: page boxes correct, only Instrument Sans embedded, both formats present"


def pending_tokens():
    """Token values that are standing in for a real one nobody has supplied.

    Any key named `$<something>Pending` in a token file is surfaced by the
    build, so a provisional value cannot quietly become permanent just
    because the page renders.
    """
    found = []
    for path in sorted((ROOT / "tokens").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))

        def walk(node, trail):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k.startswith("$") and k.endswith("Pending"):
                        found.append(f"{path.name}: {v}")
                    else:
                        walk(v, trail + [k])
            elif isinstance(node, list):
                for v in node:
                    walk(v, trail)

        walk(data, [])
    return found


def run_all():
    failed = 0
    for fn in (check_palette, check_glyphs, check_pdf):
        problems, ok_message = fn()
        if problems:
            failed += len(problems)
            for p in problems:
                print(f"  FAIL {p}")
        else:
            print(f"  {ok_message}")
    return failed
