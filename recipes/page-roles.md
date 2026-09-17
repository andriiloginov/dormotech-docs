# Page roles

The Figma file names document pages by role, and the build follows the same
vocabulary. A role determines which header and footer a page gets, not what it
says.

| Role | What it is | Header | Footer |
|---|---|---|---|
| `intro` | Cover page. Dense, bespoke — the approved ones carry ~26 elements. | bespoke | none or minimal |
| `01`, `02`, `03` | Content pages. | standard or split | standard (52pt) |
| `front` / `back` | The two sides of a single sheet. `front` = `01`, `back` = `02`. | standard | standard |
| `outro` | Closing page. | none | none |

## Outro is deliberately near-empty

The approved Outro is a large ellipse with the logo-and-tagline lockup over
it and nothing else. Do not fill it with content, a summary, or contact
details unless the brand owner asks for them.

## Intro is not generated

Cover pages in the approved set are hand-composed, not assembled from body
patterns. Treat `intro` as a template to duplicate and retype, not as
something the renderer builds from blocks.
