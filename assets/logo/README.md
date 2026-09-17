# Logo

**There is no logo file here, and that is correct — not a gap.**

Two brand rules govern how the mark appears in a document:

1. **No logo in the header.** Documents carry the eyebrow pill and the title
   at the top, nothing else.
2. **The footer carries the wordmark only — the type part, without the
   symbol.**

Because the footer needs type rather than a mark, `dormotech/render.py`
sets the wordmark live in Instrument Sans instead of placing an asset. That
is the intended output, so no SVG is required to ship a correct document.

## When you would add a file here

Only if the wordmark's letterforms are customised — custom tracking, a
modified glyph, anything that is not simply Instrument Sans Bold. In that case
export it as `wordmark.svg`, drop it in this folder, and change `wordmark()`
in `dormotech/render.py` to place the asset.

The full lockup with the symbol (139.3 x 33.9 in Figma) is not used by any
document in this pipeline.

Never redraw a brand mark by hand and present it as the logo.
