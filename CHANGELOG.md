# Changelog

Tokens and regulatory copy change rarely and matter enormously when they do.
Everything else is legible from the commit history on its own.

## [0.1.0] — 2026-09-17

### Added
- Token set audited from the Figma brand guide: eight palette colours, the
  `#D7F4F3` header chrome tint, the Instrument Sans type scale, the 6/9/18
  spacing scale.
- Both page formats as first-class: A4 595x842 and US Letter 612x792.
- Component stylesheet covering header (4 variants, light/dark), footer
  (4 heights, 5 themes), and the body patterns.
- Build pipeline emitting both formats with overflow, collapse, palette,
  glyph and embedded-font checks.
- Cached Figma component map.

### Pending
- Regulatory strip, indications paragraph and clinical claims are
  placeholders — see `content/regulatory/`.
- Logo SVGs not exported — see `assets/logo/README.md`.
