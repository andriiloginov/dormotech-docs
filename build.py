#!/usr/bin/env python3
"""Build a Dormotech document into BOTH page formats, then check it.

    python build.py content/documents/pediatrics.json

Producing one format is an incomplete deliverable, so this always emits both
and fails if either overflows, collapses a block, or trips a check.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from dormotech import checks, tokens
from dormotech.render import render

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

# Measured inside the browser: the page box alone is not enough. `.body` is a
# flex child with a fixed height, so content can spill out of it and paint
# under the footer while the page still measures as fitting — that is how a
# clipped compliance placeholder once passed a green check.
PROBE = """() => {
  const out = [];
  document.querySelectorAll('.page').forEach((el, i) => {
    const body = el.querySelector('.body');
    const collapsed = [...el.querySelectorAll('.body > *:not(.spacer)')]
      .filter(c => c.clientHeight === 0).length;
    out.push({
      index: i + 1,
      overflow: Math.max(
        el.scrollHeight - el.clientHeight,
        body ? body.scrollHeight - body.clientHeight : 0),
      collapsed,
    });
  });
  return out;
}"""


def main(src):
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    name = doc.get("id") or Path(src).stem
    DIST.mkdir(exist_ok=True)

    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for fmt, spec in tokens.formats().items():
            html_path = DIST / f"{name}-{fmt}.html"
            html_path.write_text(render(doc, fmt), encoding="utf-8")

            tab = browser.new_page()
            tab.goto(html_path.as_uri())
            tab.wait_for_timeout(400)

            for page_report in tab.evaluate(PROBE):
                flags = []
                if page_report["overflow"] > 1:
                    flags.append(f"OVERFLOW +{page_report['overflow']}px")
                if page_report["collapsed"]:
                    flags.append(f"{page_report['collapsed']} COLLAPSED block(s)")
                if flags:
                    failures += 1
                print(f"  {spec['label']} page {page_report['index']}: "
                      f"{', '.join(flags) if flags else 'ok'}")

            tab.pdf(
                path=str(DIST / f"{name}-{fmt}.pdf"),
                width=spec["pdf"]["width"],    # page.pdf() rejects pt — inches/mm only
                height=spec["pdf"]["height"],
                print_background=True,         # without this every fill disappears
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )

            for i, el in enumerate(tab.query_selector_all(".page"), 1):
                el.screenshot(path=str(DIST / f"{name}-{fmt}-p{i}.png"))

            tab.close()
            print(f"{spec['label']}: dist/{name}-{fmt}.pdf")
        browser.close()

    print("\nchecks:")
    failures += checks.run_all()

    if failures:
        print(f"\n{failures} problem(s) — fix before shipping.")
        return 1
    print("\nBoth formats built and checked.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python build.py content/documents/<document>.json")
    sys.exit(main(sys.argv[1]))
