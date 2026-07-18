# `scripts/crawl/` — Crawl4AI source-mapping, capture & monitoring layer

This is a **build/monitor** layer, not an access layer. It helps *find, draft-capture, and watch*
official sources. It is corpus-agnostic: everything reads `monitoring/sources.json` and the per-source
schemas in `schemas/`, with no corpus-specific logic, so it can be lifted into the shared
`provenance-corpus-builder` toolkit unchanged.

## The Layer-1 boundary (non-negotiable)

Crawl4AI **never** produces authoritative content. Concretely:

1. **Crawl4AI output is never stored as `text.txt`.** The authoritative layer holds official files
   **byte-for-byte** — PDF bytes as `original.pdf`, or the raw rendered DOM as `original.html`.
   Crawl4AI's markdown is discarded. `scripts/extract.py` remains the **sole, version-pinned
   extractor**, so the reproducibility check (`extract.py` re-derives `text.txt` from the stored
   original) stays valid.
2. **No stealth / undetected / magic / proxy escalation** against official sources — ever. If a source
   blocks the crawler, escalate per the skill: a real browser, then a human download stored verbatim
   (a provenance *upgrade*). `check_robots_txt=True` on every crawl; the verbatim-bytes path checks
   `robots.txt` too.
3. **Rendered-DOM originals are flagged.** When the stored original is a rendered snapshot of a
   JS-heavy official site (not a PDF), the generated ingest manifest records
   `original_capture: rendered_dom` with the pinned Crawl4AI version and the browser config, so a
   reader knows it is a snapshot, not a byte-for-byte file download.
4. **No LLM at runtime.** `JsonCssExtractionStrategy` runs deterministic CSS extraction. The only LLM
   step is `authoring/generate_schema_helper.py`, run **once per source, by a human, off-pipeline**, to
   *draft* a schema — which is then hand-reviewed and committed. The committed schema is what runs.

Nothing here runs `ingest.py`. It produces **drafts** (`status: draft_requires_human_review`); a human
verifies citation/metadata and runs `ingest.py`.

## Toolchain (pinned)

- **Crawl4AI `0.8.9`** — pinned in `scripts/requirements.txt`. (The docs site is labelled "v0.9.x";
  the package `__version__` is `0.8.9`. Bump the pin here *and* in `common.py` together if a newer
  stable lands, and re-author/re-verify schemas.)
- Browser config for rendered captures: headless Chromium, JavaScript on, **stealth off, no proxy**
  (see `common.BROWSER_CONFIG`).
- Install: `pip install -r scripts/requirements.txt` then `python -m playwright install chromium`
  (Crawl4AI's browser). The monthly monitor degrades to whole-page-hash if Crawl4AI is absent.

## Components

| File | Skill step | What it does |
|---|---|---|
| `map_sources.py` | 2 (map sources) | Runs each source's schema over its index page → structured inventory (`monitoring/inventory.json`), flagging gaps vs the design-lock scope. |
| `gen_manifests.py` | 4 (ingest) | Inventory → **draft** `ingest.py` manifests under `queue/manifests/`, each `draft_requires_human_review`. Never runs ingest. |
| `capture.py` | 4 (capture) | Given a manifest: PDF → verbatim bytes; HTML → Crawl4AI rendered `original.html`. Into `capture/staging/` with a capture log. |
| `../watch_sources.py` | 7 (self-maintain) | Per source with a schema: extract → canonicalise (sorted keys) → hash → diff vs previous run → structured change report (new / disappeared / changed fields). Whole-page-hash fallback for schema-less sources. |
| `authoring/generate_schema_helper.py` | — | **Off-pipeline** LLM draft of a schema for a source, for hand-review before commit. |

Schemas live in `schemas/<source>.json` (Crawl4AI `JsonCssExtractionStrategy` format). Each source in
`monitoring/sources.json` may carry `schema`, `capture_type` (`pdf`/`html`), and `scope` fields; a
source with no `schema` falls back to whole-page-hash monitoring.

## Schema-mode safeguards

Schema mode is more precise than whole-page hashing — cosmetic churn (news blocks, "last updated"
stamps, reworded intros) cannot trigger it, because only the document list is read. But it introduces
one failure mode whole-page hashing does not have, so both are guarded:

**1. Broken-selector guard (against silent under-reporting).** If a site's markup shifts, selectors can
stop matching and real documents go unseen — a *false negative*, which is worse than a false alarm. A
real listing loses documents one or two at a time; broken selectors lose all or most at once. So a
collapse in record count (to zero, or below half of a previous set of ≥5) is reported as
**`schema_suspect`**, explicitly *not* as documents being removed, and the run **refuses to advance the
baseline or overwrite the snapshot**. Silently accepting a collapsed set is how a broken schema starts
reporting "unchanged" forever. Thresholds: `SCHEMA_MIN_PREV`, `SCHEMA_DROP_RATIO` in
`../watch_sources.py`.

**2. False-alarm instrumentation (to measure the precision claim, not assert it).** For every schema
source each run records **both** hashes — the whole-page hash and the record-set hash — as one JSON
line in `monitoring/false_alarm_log.jsonl`. A run where the page hash moved but the record set is
identical is, by definition, a false alarm under the old method. The reverse case (records changed
while the page hash sat still) is also counted: those are changes whole-page mode would have *missed*.
Accumulated over months this yields a real number:

```
python3 scripts/watch_sources.py --tally
```

The log is committed — it is the evidence, and it only grows by one line per schema source per run.
