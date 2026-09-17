# Releases

Approved PDFs live here or, better, on a GitHub Release tag — not in `dist/`,
which is a build directory and is ignored.

Why built PDFs are not committed on every change: a PDF is a binary that
changes completely on every rebuild, so committing them makes the repository
grow fast and the diffs say nothing. The *source* of a document — its JSON
content model in `content/documents/` — is what carries the history worth
reading: who changed which sentence, and when.

So:

- `content/documents/*.json` — always committed. This is the document.
- built PDFs — attached to a GitHub Release when a document is approved, or
  downloaded from the CI run's artifacts for review.

Every pull request already uploads the rendered pages as a CI artifact, so a
reviewer approves a picture rather than a diff.
