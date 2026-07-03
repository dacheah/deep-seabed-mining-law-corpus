# Deep Seabed Mining Law Corpus

A neutral, authoritative, machine-readable record of the law governing mineral resources of **"the
Area"** — the seabed and subsoil beyond national jurisdiction — built **provenance-first**. It covers
the international ISA/UNCLOS regime and, as a clearly-distinct parallel track, the US non-UNCLOS regime.

It is a sibling of the Space Law Corpus and inherits its architecture: a hard wall between official
source texts and anything generated from them, cryptographic provenance on every text, and append-only
dated versioning. **One principle governs everything: provenance and version integrity override
convenience, always.**

## What's here

| Instrument | Status |
|---|---|
| **UNCLOS Part XI — The Area** (arts. 133–191) | authentic English text, complete, `extracted_verified` |
| **1994 Part XI Implementation Agreement** | authentic English text, complete, `extracted_verified` |
| **ISA Polymetallic Nodules Exploration Regulations** (ISBA/19/C/17, as amended 2013) | authentic English text, complete, `extracted_verified` |
| **ISA Polymetallic Sulphides Exploration Regulations** (ISBA/16/A/12/Rev.1, 2010) | authentic English text, complete, `extracted_verified` |
| **ISA Cobalt-rich Crusts Exploration Regulations** (ISBA/18/A/11, 2012) | authentic English text, complete, `extracted_verified` |
| **2011 Seabed Disputes Chamber Advisory Opinion** (ITLOS Case 17) | `authoritative_missing` — registered with full provenance; complete text pending a human download (fetch-tool output cap truncated it) |

Six instruments; five complete authoritative texts plus one flagged gap. Cross-instrument concept
coverage (20 neutral concepts, ~800 provision-concept tags) is in `derived/concept-index.md`.

## Layout

```
authoritative/<corpus_id>/<version_id>/   original.* · text.txt · metadata.yaml   (LAYER 1 — official texts)
derived/<corpus_id>/<version_id>/          structure.json · concepts.json · derived-metadata.yaml (LAYER 2 — generated, unofficial)
schema/                                    the two JSON Schemas
scripts/                                   the pipeline (ingest, validate, build_derived, build_site, watch_sources, export_hf_dataset)
docs/design/                               the six locked design docs + judgement-call log (the "constitution")
docs/source-map.md                         honest source-coverage report
manifests/                                 ingest manifests (inputs)
capture/                                   raw/cleaned captures used at ingest (provenance trail)
monitoring/                                source-watch config
site/                                      generated static site (regenerable; git-ignored)
```

## The two layers (never conflated)

- **`authoritative/`** — primary source texts only, in their authentic enacting language, with full
  provenance (source URL, retrieval date, official citation, jurisdiction, language, authoritative-
  status flag, SHA-256 hashes). Append-only; corrections/amendments are new dated versions.
- **`derived/`** — structure extraction, neutral concept tags, summaries, machine translations.
  Unofficial, labelled, and traceable to a specific authoritative version by its text hash.

The wall is enforced by folder, schema, and `scripts/validate_corpus.py`.

## Run it

```bash
pip install -r scripts/requirements.txt
python3 scripts/validate_corpus.py     # integrity gate — must be green
python3 scripts/build_derived.py       # regenerate the derived layer
python3 scripts/build_site.py          # regenerate the browsable site into site/
python3 scripts/watch_sources.py --selftest   # offline monitor self-test
```

## Add an instrument (short version)

1. Capture the authentic-language text from the most official source (issuer / gazette / registry).
2. Write a manifest in `manifests/` (see the existing three) and run
   `python3 scripts/ingest.py --manifest manifests/your.json` (it hashes, writes `metadata.yaml`,
   validates, and refuses to overwrite).
3. Verify fidelity against the source; upgrade `text_fidelity` with a dated `verification` record.
4. `python3 scripts/build_derived.py && python3 scripts/build_site.py`, validate, commit.

See `docs/maintainers-guide.md` for the full workflow, the neutral concept vocabulary
(`scripts/concepts.py`), and the judgement calls in `docs/design/judgement-calls.md`.

## Maintenance cadence (two phases)

- **Phase 1 (active, now):** through adoption of the ISA **Mining Code** (draft Exploitation
  Regulations) and stabilisation of the US regime. Closer-than-annual monitoring; automated watch on
  ISA Council/LTC outputs and the US Federal Register (`monitoring/sources.json`).
- **Phase 2 (settled):** annual review aligned to the ISA Assembly/Council session cycle, earlier only
  on a material event.

## Licensing

Our contributions (derived layer, schema, scripts, site, docs) are **CC BY 4.0**. Source texts are
**not** relicensed — each keeps its own terms, recorded per document in `license`/`rights_note`
(UN/ISA/ITLOS materials under their terms; US Government works public domain). See
`docs/design/04-licensing-policy.md`.

## Honest limits of this build

- Captures are text extractions via an approved fetch tool, **not** byte-exact official PDFs;
  each record flags a byte-exact download as a recommended provenance upgrade.
- Only the **English** authentic text is stored so far; the other authentic languages are a recorded
  coverage gap (JC-003).
- The 2011 Advisory Opinion needs its complete official text added by a human download
  (https://www.itlos.org/fileadmin/itlos/documents/cases/case_no_17/17_adv_op_010211_en.pdf).
- The draft Mining Code (exploitation regulations) and the US DSHMRA/OCSLA track are scoped and mapped
  but not yet ingested — they are the priority next additions.
