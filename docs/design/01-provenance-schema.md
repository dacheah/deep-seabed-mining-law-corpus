# 01 — Provenance schema (Deep Seabed Mining Law Corpus)

Every authoritative document carries, from its first commit, enough provenance that a stranger can
trace it to source and detect tampering. The machine-checkable version is
`schema/authoritative-metadata.schema.json`; this document is the human rationale. *(Fields inherited
from the Space Law Corpus; notes are DSM-specific.)*

## Required fields

- `corpus_id` — stable identifier, assigned once, never changed (see doc 02 for the DSM shape).
- `version_id` — the date the textual state took effect (`YYYY-MM-DD`), or a labelled fallback.
- `title` (verbatim official title), `short_title`, `jurisdiction`, `document_type`.
- `official_citation` — how the instrument is cited in DSM practice (e.g. "UNCLOS Part XI",
  "ISBA/19/C/17, annex", "ITLOS Reports 2011, p. 10", "15 CFR Part 970").
- `authentic_languages` / `language` — the language(s) in which it was enacted/issued, and the
  language of the stored `text.txt`.
- `source_url`, `source_publisher`, `source_is_official` (issuer/depositary vs reproduction).
- `retrieval_date`, `retrieved_by`.
- `original_format`, `original_filename`, `original_sha256` — the byte-exact captured artifact.
- `text_sha256`, `content_hash` — hash of the stored authentic-language text.
- `text_fidelity` — `verbatim_transcription` > `extracted_verified` > `extracted_unverified` > `ocr_unverified`.
- `authoritative_status` — `authentic_text` | `official_consolidation` | `certified_copy` | `authoritative_missing`.
- `license`, `rights_note` — per this document's source (see doc 04).
- `capture_history[]`, `supersedes`, `superseded_by`, `related_documents[]`, `provenance_note`.
- Optional after checking against the source: `verification{}`, `corrections[]`.

## DSM-specific notes

- **`jurisdiction`**: use `international` for UNCLOS / the 1994 Agreement / ISA instruments / ITLOS
  case law (the ISA regime), and the ISO 3166-1 alpha-3 code for national law (`USA`, etc.). This
  single field is how the corpus keeps the ISA regime and the US non-UNCLOS track visibly distinct
  (see JC-001).
- **`document_type`**: controlled free-form values used to group instruments on the site —
  `convention`, `implementing_agreement`, `advisory_opinion`, `isa_regulation`,
  `isa_recommendation`, `isa_decision`, `national_statute`, `national_regulation`.
- **`official_citation`** for ISA instruments should carry the `ISBA/...` document symbol, which is
  the stable citation handle in ISA practice.
- **`related_documents[]`** is used heavily here: Part XI ↔ 1994 Agreement (the Agreement modifies
  Part XI and prevails on conflict), each exploration regulation ↔ its enabling Convention articles,
  the 2011 Advisory Opinion ↔ Part XI Art 139/153 and Annex III.

**Rule:** never claim more fidelity than you verified. A visible gap is an asset; a hidden one is a liability.
