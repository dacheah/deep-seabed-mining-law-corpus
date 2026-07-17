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

> Not yet authored: the 18 current sources still run in whole-page-hash mode. Author each with the
> helper above (the ISA WordPress listings and ITLOS case list are the highest-value first targets;
> the US Federal Register source is a JSON API — better watched whole-page or via a small JSON handler
> than a CSS schema).
