# Dormotech documents

Design tokens, components and a build pipeline for Dormotech document
collateral — spec sheets, clinical application sheets, front/back sell sheets,
multi-page reports.

The point of this repo is that a document gets **composed from these files**
rather than re-derived from a description each time. A document rebuilt from a
written spec drifts a little on every rebuild; one assembled from the same
partials does not.

## Quick start

Python only — three dependencies, no Node, no build step of its own.

```bash
pip install -r requirements.txt
playwright install chromium

python build.py content/documents/pediatrics.json
```

That one command renders both formats, checks them, and fails loudly if
anything is wrong. Output lands in `dist/` — two PDFs, two HTML files, and a
PNG of every page.

The token CSS is generated in memory at build time rather than committed, so
there is no generated file to keep in sync.

## Decide this first

**Which side is the source of truth — this repo, or the Figma file?**

This is not yet decided, and everything else assumes an answer. Two
independently edited sources produce two divergent truths, which is worse than
having only one. The options:

- **Figma leads** — the repo is generated from it (Variables export, Tokens
  Studio). Designers keep working as they do now; the repo can go stale
  between exports.
- **Repo leads** — Figma is assembled from code. Strongest guarantee, biggest
  change to the design workflow.
- **Code Connect bridges** — each Figma component is formally mapped to its
  code counterpart. Most setup work, least drift.

Write the answer into this section once it is made. A reader should not have
to infer it from the folder structure.

## Layout

| Path | What lives there |
|---|---|
| `tokens/` | Source of truth for colour, type, spacing and page geometry. Edit here, never in a stylesheet. |
| `styles/components.css` | The component library — header, footer, body patterns. |
| `build.py` | The only entry point: renders both formats, then checks them. |
| `dormotech/` | `tokens.py` (JSON → CSS), `render.py` (content model → HTML), `checks.py` (the four checks). |
| `content/documents/` | One JSON content model per document. |
| `content/regulatory/` | Regulatory copy. Review-gated — see `.github/CODEOWNERS`. |
| `recipes/` | Which components each document type is made of. |
| `figma/` | Cached map of the Figma library and the approved references. |
| `assets/` | The font files, committed. |

## Rules that are not obvious

**Every document ships in both A4 and US Letter.** Producing one is an
incomplete deliverable; the PDF check fails if one is missing.

**The format pair is a re-layout, not a scale.** A4 is 17pt narrower and 50pt
taller than US Letter, so content redistributes. Where a block genuinely needs
to differ it carries a per-format value — `"columns": {"a4": 1, "us": 2}` —
rather than letting the renderer guess. Check both renders: a page that fits
in US Letter can overflow in A4.

**Citation markers are written `[^1]`, never `¹`.** The Instrument Sans latin
subset has no superscript digits; a literal one silently pulls a fallback font
into the PDF. See `assets/fonts/README.md`.

**Nothing in a page body may silently collapse.** Flex children shrink by
default, and a compliance block squeezed to zero height still reports that the
page fits. `.body > * { flex: 0 0 auto }` prevents it and the build checks for
it anyway.

**Regulatory copy is never drafted here.** Status labels, the indications
paragraph and clinical claims come verbatim from the live Figma component or
from the brand owner. When they are missing the build renders a visible
placeholder — that is intended, not a bug to work around. And never carry a
clinical claim into a document just because the layout has a slot for it.

**No logo in the header, wordmark only in the footer.** Documents carry no
logo at the top, and the footer carries the type part of the logo without the
symbol. The standard footer is three groups running left to right on an even
gap — wordmark, stat callout, regulatory strip — not a wordmark with something
pushed against the right edge.

**Playwright's `page.pdf()` rejects `pt`** for width and height. `tokens/page.json`
carries the inch and millimetre equivalents for exactly this reason.

## What is still pending

- **Regulatory content** — `content/regulatory/` holds placeholders. Every
  build renders a visible "pending" block in the footer until they are filled.
- **Wordmark** — rendered as live type rather than from an SVG. That matches
  the brand rule (type only, no symbol), so it is not a gap; an exported SVG
  would only be needed if the letterforms are customised.
- The **source-of-truth decision** above.
