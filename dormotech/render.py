"""Render a document content model into a complete, self-contained HTML file
for one page format.

The same content model renders to both formats. Where a block genuinely needs
to lay out differently — because A4 is narrower and taller than US Letter — it
carries a per-format value, e.g. "columns": {"a4": 1, "us": 2}, rather than
the renderer guessing.
"""
import base64
import html
import json
import re
from pathlib import Path

from . import tokens

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
WEIGHTS = (400, 500, 600, 700)


def esc(s):
    return html.escape("" if s is None else str(s), quote=False)


def cite(s):
    """[^1] becomes a real <sup>.

    The Instrument Sans latin subset has no superscript digits, so a literal
    ¹ silently drags a fallback font into the PDF. Authors write [^1].
    """
    return re.sub(r"\[\^(\d+)\]", r"<sup>\1</sup>", esc(s))


def pick(value, fmt):
    if isinstance(value, dict):
        return value.get(fmt, value.get("us", value.get("a4")))
    return value


def _regulatory():
    base = ROOT / "content" / "regulatory"
    return {
        "strip": json.loads((base / "strip.json").read_text(encoding="utf-8")),
        "claims": json.loads((base / "claims.json").read_text(encoding="utf-8")),
    }


def _font_faces():
    faces = []
    for w in WEIGHTS:
        data = (FONTS / f"instrument-sans-latin-{w}-normal.woff2").read_bytes()
        b64 = base64.b64encode(data).decode()
        faces.append(
            "@font-face{font-family:'Instrument Sans';font-style:normal;"
            f"font-weight:{w};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "\n".join(faces)


# ------------------------------------------------------------------ blocks --

def _grouped(items, cols):
    per = -(-len(items) // cols)
    return [items[i:i + per] for i in range(0, len(items), per)]


def _bullets(b, fmt):
    cls = "lime" if b.get("accent") == "lime" else ""
    cols = pick(b.get("columns"), fmt) or 1
    items = [f"<li>{cite(i)}</li>" for i in b["items"]]
    if cols < 2:
        return f'<ul class="{cls}">{"".join(items)}</ul>'
    groups = _grouped(items, cols)
    inner = "".join(f'<ul class="{cls}">{"".join(g)}</ul>' for g in groups)
    return f'<div class="cols2">{inner}</div>'


def _features(b, fmt):
    cols = pick(b.get("columns"), fmt) or 1
    items = [f'<div class="feat"><h3>{cite(i["head"])}</h3><p>{cite(i["body"])}</p></div>'
             for i in b["items"]]
    if cols < 2:
        return "".join(items)
    groups = _grouped(items, cols)
    inner = "".join(f'<div>{"".join(g)}</div>' for g in groups)
    return f'<div class="cols2">{inner}</div>'


def block(b, fmt):
    kind = b["kind"]
    if kind == "section":
        lead = f'<p class="lead">{cite(b["lead"])}</p>' if b.get("lead") else ""
        return f'<div><div class="section-head">{cite(b["heading"])}</div>{lead}</div>'
    if kind == "bullets":
        return _bullets(b, fmt)
    if kind == "features":
        return _features(b, fmt)
    if kind == "rule":
        return '<hr class="rule">'
    if kind == "card":
        head = f'<div class="section-head">{cite(b["heading"])}</div>' if b.get("heading") else ""
        body = f'<p class="lead">{cite(b["body"])}</p>' if b.get("body") else ""
        nested = "".join(block(x, fmt) for x in b.get("blocks", []))
        return f'<div class="card {b.get("tone", "mint")}">{head}{body}{nested}</div>'
    if kind == "refs":
        cells = "".join(f'<p><span class="n">{i}.</span> {esc(r)}</p>'
                        for i, r in enumerate(b["items"], 1))
        return f'<div class="refs"><div class="label">References</div><div class="grid">{cells}</div></div>'
    if kind == "legend":
        return f'<div class="legend">{cite(b["text"])}</div>'
    if kind == "spacer":
        return '<div class="spacer"></div>'
    raise ValueError(f"unknown block kind: {kind}")


# ------------------------------------------------------------------ chrome --

def wordmark():
    """The type part of the logo only — no symbol.

    It appears in the footer and nowhere else: documents carry no logo in the
    header. Both are brand decisions, so neither is configurable here.
    """
    return '<span class="wordmark">Dormotech</span>'


def header(h, doc):
    if not h:
        return ""
    classes = ["hdr"]
    if doc.get("theme", {}).get("header") == "dark":
        classes.append("dark")
    if h.get("variant") == "split":
        classes.append("split")
    cls = " ".join(classes)

    top = f'<div class="hdr-top"><span class="pill">{esc(h.get("eyebrow", doc.get("eyebrow")))}</span></div>'
    title = f'<h1>{cite(h["title"])}</h1>'
    sub = f'<p class="sub">{cite(h["subtitle"])}</p>' if h.get("subtitle") else ""

    if h.get("variant") == "split" and h.get("subtitle"):
        return f'<div class="{cls}">{top}<div class="hdr-cols">{title}{sub}</div></div>'
    return f'<div class="{cls}">{top}{title}{sub}</div>'


def _stat(reg, claim_id, warnings):
    """The stat callout is opt-in, and deliberately has no default.

    A clinical claim belongs to the study it came from and the population it
    describes. Rendering one just because the footer has room for it is
    exactly the mistake the compliance rules warn about, so a document that
    does not name a claim simply gets no stat.
    """
    if not claim_id:
        return ""
    claim = next((c for c in reg["claims"].get("claims", []) if c["id"] == claim_id), None)
    if not claim or claim.get("value") is None:
        # The document DID ask for this claim, so the gap is real — but it is
        # reported to whoever is building, never drawn on the page.
        warnings.append(f"footer stat '{claim_id}' has no value in content/regulatory/claims.json")
        return ""
    return (f'<div class="stat"><span class="value">{esc(claim["value"])}</span>'
            f'<span class="caption">{esc(claim.get("caption", ""))}</span></div>')


def _strip(reg, warnings):
    labels = reg["strip"].get("labels") or []
    if not labels:
        warnings.append("regulatory strip is unsourced — content/regulatory/strip.json")
        return ""
    parts = '<i class="sep"></i>'.join(f"<span>{esc(l)}</span>" for l in labels)
    return f'<div class="strip">{parts}</div>'


def footer(f, doc, reg, warnings):
    """Three groups running left to right on an even gap — wordmark, stat,
    regulatory strip. This mirrors the approved footer (Figma 2561:4917,
    52pt tall: wordmark at x=18, stat at x=175, strip at x=347). It is not a
    logo on the left with something pushed against the right edge.
    """
    f = f or {}
    theme = f.get("theme", doc.get("theme", {}).get("footer", "forest"))
    variant = f.get("variant", "standard")

    classes = ["ftr"]
    if theme != "forest":
        classes.append(theme)
    if variant in ("minimal", "legal"):
        classes.append(variant)
    cls = " ".join(classes)

    if variant == "minimal":
        return f'<div class="{cls}">{wordmark()}</div>'

    if variant == "legal":
        if f.get("indications"):
            text = f'<p class="indications">{esc(f["indications"])}</p>'
        else:
            # A legal footer exists to carry this paragraph. Missing, the
            # document is not shippable — but the page stays clean and the
            # build says so.
            warnings.append("legal footer has no indications paragraph — "
                            "content/regulatory/indications.md")
            text = ""
        return f'<div class="{cls}">{wordmark()}{text}<div class="qr"></div></div>'

    return (f'<div class="{cls}">{wordmark()}'
            f'{_stat(reg, f.get("stat"), warnings)}{_strip(reg, warnings)}</div>')


# -------------------------------------------------------------------- page --

def page(p, doc, fmt, reg, warnings):
    if p.get("role") == "outro":
        tag = f'<p class="lead">{esc(p["tagline"])}</p>' if p.get("tagline") else ""
        return f'<div class="page {fmt} outro"><div class="mark">{wordmark()}{tag}</div></div>'
    body = "".join(block(b, fmt) for b in p.get("blocks", []))
    return (f'<div class="page {fmt}">{header(p.get("header"), doc)}'
            f'<div class="body">{body}</div>{footer(p.get("footer"), doc, reg, warnings)}</div>')


def render(doc, fmt):
    """Returns (html, warnings).

    Unsourced content is never drawn on the page — no dashed boxes, no
    "pending" labels. There is no such treatment in the design system, and a
    placeholder on a page can reach a customer. Gaps are reported to whoever
    is running the build instead.
    """
    reg = _regulatory()
    warnings = []
    css = (ROOT / "styles" / "components.css").read_text(encoding="utf-8")
    pages = "\n".join(page(p, doc, fmt, reg, warnings) for p in doc["pages"])
    html_out = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>{esc(doc['title'])} — {fmt.upper()}</title>
<style>
{_font_faces()}
{tokens.build_css()}
{css}
</style>
</head><body>
{pages}
</body></html>"""
    return html_out, warnings
