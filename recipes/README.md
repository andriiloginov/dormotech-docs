# Recipes

A recipe says which components a document type is made of, so a new document
is an assembly rather than an act of interpretation.

## The dual-format rule

**Every document ships in both A4 and US Letter.** Producing one is an
incomplete deliverable. `scripts/build.mjs` always emits both and
`scripts/check-pdf.py` fails if one is missing.

The pair is a **re-layout, not a scale**. A4 is 17pt narrower and 50pt taller
than US Letter, so content redistributes between them. Verified against the
approved Technical Overview: the right-hand column of `A4/01` is a single
184x594 block, while `US/01` splits the same content into 184x216 and
184x339 because the page is shorter.

Where a block genuinely needs to differ, the content model carries a
per-format value rather than letting the renderer guess:

```json
{ "kind": "features", "columns": { "a4": 1, "us": 2 }, "items": [...] }
```

Check both renders. A page that fits in US Letter can overflow in A4, and the
reverse — the example document went through both.
