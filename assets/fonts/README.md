# Instrument Sans

The one typeface in this system. Weights 400 / 500 / 600 / 700, SIL Open Font
License.

## Why the files are committed here

`fonts.googleapis.com` is blocked by the egress policy in the sandboxes these
documents get built in — the request fails at the network boundary and
retrying changes nothing. The npm registry is not blocked, so the files came
from the `@fontsource/instrument-sans` package:

```bash
npm pack @fontsource/instrument-sans
tar xzf fontsource-instrument-sans-*.tgz
cp package/files/instrument-sans-latin-{400,500,600,700}-normal.woff2 assets/fonts/
```

`src/render.mjs` embeds them as base64 `@font-face` rules so a built document
is self-contained.

## The `.woff` file is not a duplicate

`instrument-sans-latin-400-normal.woff` is committed alongside the `.woff2`
because fontTools cannot open a `.woff2` without the brotli extension, which
is not always installed. `scripts/check-glyphs.py` reads the `.woff`.

## Missing glyphs — read this before writing a citation

The latin subset has **no `¹` (U+00B9) and no `²` (U+00B2)**. Typing them
looks correct on screen and silently pulls a fallback font into the PDF,
which breaks the single-typeface rule.

Write citation markers as `[^1]` in the content model. The renderer turns
them into real `<sup>` elements set in Instrument Sans.
`scripts/check-glyphs.py` fails the build on anything else that slips in.
