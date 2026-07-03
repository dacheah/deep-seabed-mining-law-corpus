# Maintainer's guide — Deep Seabed Mining Law Corpus

This guide lets a competent stranger run and extend the corpus from the documents alone. Read the six
locked design docs in `docs/design/` first — they are the constitution and override convenience.

## Mental model

Two kinds of work, kept separate:
- **Mechanical** (the scripts, never re-implemented): hashing, packaging, validating, structure
  parsing, concept tagging, site generation, monitoring, dataset export.
- **Judgement** (you): scope, finding/vetting official sources, the neutral concept vocabulary,
  awkward sourcing, and fidelity verification. Surface genuine legal-judgement calls in
  `docs/design/judgement-calls.md`.

## Adding an instrument, end to end

1. **Scope check.** Is it in scope (`docs/design/05-scope-boundary.md`)? Borderline → record it in
   `queue/candidates.md` and decide with a dated note, don't ingest silently.
2. **Capture.** Retrieve the **authentic-language** text from the most official source (issuer,
   official gazette/registry, treaty depositary). If a fetcher can't reach it, escalate: a real
   browser, then a human-downloaded official file stored byte-for-byte (a provenance *upgrade*). Never
   bypass bot-protection/CAPTCHAs — have a human download instead. Save what you captured under
   `capture/`.
3. **Manifest.** Copy an existing file in `manifests/` and fill every field (see
   `docs/design/01-provenance-schema.md`). Identifiers follow `docs/design/02-versioning-scheme.md`
   (e.g. `isa/regulation/nodules-2013`, `usa/statute/dshmra-1980`). Store only authentic-language text
   as authoritative; a translation-only source → `authoritative_status: authoritative_missing`
   placeholder (JC-005).
4. **Ingest.** `python3 scripts/ingest.py --manifest manifests/your.json`. It stores files, computes
   SHA-256 hashes, writes `metadata.yaml`, validates, and **refuses to overwrite** a version.
5. **Verify.** Compare `text.txt` against the official source; catch defects; set `text_fidelity`
   honestly and add a dated `verification` record. Reproduce genuine source defects (flag them); fix
   only true capture errors, as dated `corrections` entries. Both states stay in Git.
6. **Derive + publish.** `python3 scripts/build_derived.py && python3 scripts/build_site.py`.
7. **Validate + commit.** `python3 scripts/validate_corpus.py` must be green before every commit.

## The concept layer

`scripts/concepts.py` holds the whole domain vocabulary: 20 **neutral** concepts (what a provision is
*about*, taking no side), a keyword fallback (`KW`), curated per-instrument tags (`TAGS`, add for
high-value instruments after review), provision header words (`UNIT_HEADERS`), and cross-reference
regexes. Keep it neutral — a "pro-mining"/"pro-moratorium" tag would be advocacy and is forbidden
(`docs/design/06-two-layer-separation.md`).

## Priority backlog (next additions)

1. **ISA exploration regulations** — polymetallic nodules (ISBA/19/C/17, as amended), polymetallic
   sulphides (ISBA/16/A/12/Rev.1), cobalt-rich crusts (ISBA/18/A/11). English authentic, from
   `isa.org.jm` (ISBA/... symbols). `document_type: isa_regulation`.
2. **Draft Exploitation Regulations ("the Mining Code")** — ingest each draft revision as a dated,
   clearly-marked **draft, not in force** version (JC-002). Front-loaded watch until adoption.
3. **Complete the 2011 Advisory Opinion** — human-download the full official English PDF and re-ingest
   as `authentic_text`; record the authoritative-language designation (JC-004).
4. **US DSHMRA track** — 30 U.S.C. ch. 26 (DSHMRA) + 15 CFR 970/971, from govinfo/eCFR; keep it a
   clearly-distinct parallel track (JC-001).
5. **Other authentic languages** of UNCLOS/the 1994 Agreement (JC-003), and other sponsoring-state laws.

## Monitoring

`monitoring/sources.json` lists pages watched monthly by `scripts/watch_sources.py`
(GitHub Action `watch-sources.yml`). A change opens an issue for a maintainer to **triage** — it may be
a genuine new/amended instrument or a cosmetic page update. Nothing is ingested automatically.

## The rules you never break

Two-layer wall (never put generated content under `authoritative/`); append-only authoritative layer;
gaps recorded, not hidden; never claim more fidelity than you checked; `validate_corpus.py` green
before every commit; never force-push or rewrite history — Git is the dated substrate.

## Future milestone

Move to a neutral institutional home and publish the dataset (`scripts/export_hf_dataset.py`) so the
corpus outlives any single maintainer.
