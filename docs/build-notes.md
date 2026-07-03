# Build notes — session 2026-07-03

Environment constraints and fixes recorded for reproducibility and honesty.

## Environment constraints encountered
- **Fetch tool output cap (~132 KB).** Long official PDFs truncate. UNCLOS Part XI and the 1994
  Agreement were captured complete from DOALOS HTML; the ITLOS 2011 Advisory Opinion PDF truncated at
  ~para 204, so it is registered `authoritative_missing` pending a human download (docs/source-map.md).
- **Captures are text extractions, not byte-exact PDFs.** Each authoritative record's `provenance_note`
  says so and flags a byte-exact official-file download as a recommended provenance upgrade (the
  skill's escalation ladder).
- **Git could not run on the delivery folder** (a Windows-backed mount that blocks git's internal file
  operations and deletion). The corpus was built with full git history in a native working directory
  and delivered as (a) the working tree and (b) a portable `deep-seabed-mining-law-corpus.bundle`
  (clone/restore the complete dated history with `git clone <bundle>`).

## Fix applied to a bundled script
- `scripts/export_hf_dataset.py` `_key()` normaliser: the regex alternation matched `art` before
  `article` (and `para` before `paragraph`), collapsing every "Article N" to the same key and giving
  all exported provisions one article's concept tags. Reordered the alternatives longest-first
  (`article|art\.?|paragraph|para\.?|…`) so provision-level concept tags join correctly. The
  authoritative layer and `derived/*/concepts.json` were never affected (they don't use `_key`).

## What a reviewer should double-check next
- Complete the 2011 Advisory Opinion from the official PDF; record its authoritative-language
  designation (JC-004).
- Cross-check Part XI / the 1994 Agreement against byte-exact official PDFs to lift them from
  "verified against capture source" to a byte-exact verification.

## Session addendum — ISA exploration regulations
- Ingested the three ISA exploration regulations (polymetallic nodules ISBA/19/C/17 as amended 2013;
  polymetallic sulphides ISBA/16/A/12/Rev.1; cobalt-rich crusts ISBA/18/A/11), each captured complete
  from the official ISA PDF (all fit just under the fetch cap) and cleaned with a deterministic
  de-artifacting/structure script (`removed UN job numbers, running headers, footnote markers`).
- Second fix to `export_hf_dataset.py`: the provision→concept join now matches on the **exact** unit
  label (falling back to `_key` only for curated tags), because `_key` does not strip "Regulation" and
  would otherwise collapse every "Regulation N" to one key. Authoritative/derived layers unaffected.
