# Figma linkage

`components.json` is a cached map of the Dormotech Figma library: component
ids, names, sizes and the approved reference documents.

## Why this file exists — do not delete it as redundant

The Figma plan allows **20 read calls per month** on Starter (200/day on
Professional with a Dev or Full seat). `get_design_context`, `get_metadata`,
`get_screenshot` and `get_variable_defs` all count; writes do not.
Rediscovering these ids costs real quota, and running out mid-task means a
document has to be finished from cached values.

## Ids break, names survive

Moving or renaming a component in Figma preserves its node id. **Rebuilding or
copy-pasting one does not** — the copy gets a new id and the old one dies.

So every entry carries the layer name and size as well as the id. On a miss,
resolve by name within the components section, then update this file with the
new id in the same commit.

## Egress

`figma.com` is blocked from the build sandbox. Request screenshots inline
(`enableBase64Response: true`) rather than trying to download the URL, and
don't retry the fetch — it cannot succeed.
