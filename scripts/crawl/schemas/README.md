# `scripts/crawl/schemas/` — per-source extraction schemas

One JSON file per official index/registry source. Each is a Crawl4AI **`JsonCssExtractionStrategy`**
schema — deterministic CSS extraction, **no LLM at runtime**. A source in `monitoring/sources.json`
becomes schema-monitored by adding `"schema": "<file>.json"`; a source with no `schema` stays on
whole-page-hash monitoring.

## Schema shape

```json
{
  "name": "human label",
  "baseSelector": "CSS selector matching EACH repeated listing item",
  "fields": [
    {"name": "title",    "selector": "…", "type": "text"},
    {"name": "citation", "selector": "…", "type": "text"},
    {"name": "date",     "selector": "…", "type": "text"},
    {"name": "doc_url",  "selector": "a", "type": "attribute", "attribute": "href"},
    {"name": "language", "selector": "…", "type": "text"}
  ]
}
```

Field `type` is `"text"` or `"attribute"` (with an `"attribute"` key, e.g. `href`). Keep the five
field names above (`title`, `citation`, `date`, `doc_url`, `language`) — `map_sources.py`,
`gen_manifests.py` and `watch_sources.py` all key off them.

## Authoring workflow (the one LLM step, off-pipeline)

Runtime extraction is deterministic. Authoring a schema is where an LLM may *draft* it — **once, by a
human, then hand-reviewed**:

1. Draft from a live sample (needs `crawl4ai` + an LLM key, e.g. `OPENAI_API_KEY`):

   ```
   python scripts/crawl/authoring/generate_schema_helper.py \
       --url "https://www.isa.org.jm/the-mining-code/official-documents/" \
       --out scripts/crawl/schemas/isa-official-documents.json
   ```

2. **Open the output and verify every selector against the live rendered page.** LLM-drafted
   selectors drift with site markup; the committed schema must be correct and stable. Fix by hand.
3. Commit the schema, then wire it in `monitoring/sources.json`:
   `"schema": "isa-official-documents.json"`.
4. `python scripts/crawl/map_sources.py` (inventory) and, from the next run, `watch_sources.py` will
   monitor it at instrument level.

`_TEMPLATE.json` is a starting point with placeholder selectors — copy it, don't wire it as-is.

## Known limitation: inline markup loses separators

Crawl4AI concatenates text across inline child elements **without inserting whitespace**. Where a
site splits a line with inline tags, the extracted text loses the space. Observed live on ITLOS,
whose case titles mark up party names separately from the "v.":

```
markup:    <i>… (Tonga Offshore Mining Ltd.</i>v.<i>International Seabed Authority)</i>
extracted: … (Tonga Offshore Mining Ltd.v.International Seabed Authority)
```

Consequences and the rule that follows:

- **Change detection is unaffected** — `_rec_key` uses `doc_url`, which is exact.
- **Extracted `title` and `citation` are INDICATIVE ONLY.** They are monitoring metadata, never
  authoritative content. A human must correct them against the source document at manifest review —
  which is already required, since every generated manifest is `draft_requires_human_review`.
- Do not "fix" this with text substitutions in the pipeline. Guessing where spaces belong is exactly
  the kind of silent transformation this layer exists to avoid.

## Selector choice: anchor on whatever is most specific to the content

Not a blanket "avoid classes" rule — the two authored schemas deliberately differ:

- **ISA** uses `li:has(a[href*='/wp-content/uploads/'][href$='.pdf'])`. The theme's `views-row`
  classes are generic and were applied inconsistently across years, so the PDF link is the stable
  anchor. `li:has(…)` is safe because list items do not nest here.
- **ITLOS** uses `div.fs-list-cases-item`, a purpose-built class for exactly this register. Here the
  content-anchored form would be **wrong**: `div:has(…)` also matches every *ancestor* div, so the
  page wrapper would come back as duplicate rows.

## Status

Authored: `isa-official-documents.json`, `itlos-list-of-cases.json`. The remaining 16 sources run in
whole-page-hash mode.

Remaining listing candidates (worth a schema): the ISA sessions index, Council documents, draft
exploitation regulations, draft standards and guidelines, LTC recommendations, the 31st session page,
the Mining Code landing page, and exploration regulations.

Correctly left on whole-page hashing (single documents — the page *is* the instrument): both UN
DOALOS texts, both eCFR parts, ITLOS Case No. 17, and the NOAA page. The US Federal Register source
is a JSON API and needs a small JSON handler rather than a CSS schema.
