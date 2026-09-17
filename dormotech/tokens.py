"""Turn tokens/*.json into CSS custom properties.

tokens/ is the source of truth. The CSS is generated at build time rather
than committed, so there is no stale-artifact problem and nothing to keep in
sync by hand.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "tokens"


def load(name):
    return json.loads((TOKENS / name).read_text(encoding="utf-8"))


def _kebab(s):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


def _pt(n):
    return f"{n}pt"


# Which type role feeds which CSS variable prefix.
TYPE_ROLES = {
    "eyebrow": "eyebrow",
    "h1": "h1",
    "subheader": "subheader",
    "sectionHead": "section",
    "body": "body",
    "dense": "dense",
    "featureHead": "feature",
    "caption": "caption",
    "reference": "reference",
    "display": "display",
}


def build_css():
    color, type_, space, page = (load(f) for f in
                                 ("color.json", "type.json", "space.json", "page.json"))
    out = ["/* generated from tokens/*.json — edit the JSON, not this */", ":root {"]

    for key, v in color["palette"].items():
        out.append(f"  --color-{key}: {v['hex']};")
    for key, v in color["chrome"].items():
        out.append(f"  --color-{_kebab(key)}: {v['hex']};")
    out.append("  --color-ink: var(--color-forest);")
    for key, v in color["derived"].items():
        if key.startswith("$"):
            continue
        out.append(f"  --color-{_kebab(key)}: {v};")

    fam = type_["family"]
    out.append(f"  --font-family: '{fam['name']}', {fam['fallback']};")
    for key, name in TYPE_ROLES.items():
        t = type_["scale"].get(key)
        if not t:
            continue
        if "weight" in t:
            out.append(f"  --type-{name}-weight: {t['weight']};")
        out.append(f"  --type-{name}-size: {_pt(t['size'])};")
        if "lineHeight" in t:
            out.append(f"  --type-{name}-line: {_pt(t['lineHeight'])};")
        if "tracking" in t:
            out.append(f"  --type-{name}-tracking: {_pt(t['tracking'])};")
        if "opacity" in t:
            out.append(f"  --type-{name}-opacity: {t['opacity']};")

    for key, v in space["scale"].items():
        out.append(f"  --space-{key}: {_pt(v)};")
    for key, v in space["radius"].items():
        out.append(f"  --radius-{key}: {_pt(v)};")
    out.append(f"  --rule-hairline: {_pt(space['rules']['hairline'])};")
    for key in ("inset", "dot", "gap", "indent"):
        out.append(f"  --bullet-{key}: {_pt(space['bullet'][key])};")

    for key, f in page["formats"].items():
        out.append(f"  --page-{key}-width: {_pt(f['width'])};")
        out.append(f"  --page-{key}-height: {_pt(f['height'])};")
        out.append(f"  --page-{key}-margin: {_pt(f['margin'])};")
    fh = page["chrome"]["footerHeights"]
    out.append(f"  --footer-minimal: {_pt(fh['minimal'])};")
    out.append(f"  --footer-standard: {_pt(fh['standard'])};")
    out.append(f"  --footer-legal: {_pt(fh['legal'])};")
    out.append(f"  --footer-legal-image: {_pt(fh['legalImage'])};")

    out.append("}")
    return "\n".join(out)


def formats():
    return load("page.json")["formats"]
