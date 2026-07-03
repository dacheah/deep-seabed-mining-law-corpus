# 01 — Provenance schema (TEMPLATE)

Every authoritative document carries, from its first commit, enough provenance that a stranger
can trace it to source and detect tampering. These are the required fields (see
`schema/authoritative-metadata.schema.json` for the machine-checkable version):

- `corpus_id` — stable identifier, assigned once, never changed (external references depend on it).
- `version_id` — the date the textual state took effect (`YYYY-MM-DD`), or a labelled fallback.
- `title`, `short_title`, `jurisdiction`, `document_type`.
- `official_citation` — how the source is cited in [DOMAIN].
- `authentic_languages` / `language` — the language(s) in which it was enacted/issued.
- `source_url`, `source_publisher`, `source_is_official` (issuer/depositary vs reproduction).
- `retrieval_date`, `retrieved_by`.
- `original_format`, `original_filename`, `original_sha256` — the byte-exact captured artifact.
- `text_sha256`, `content_hash` — hash of the stored text.
- `text_fidelity` — `verbatim_transcription` > `extracted_verified` > `extracted_unverified` > `ocr_unverified`.
- `authoritative_status` — `authentic_text` | `official_consolidation` | `certified_copy` | `authoritative_missing`.
- `license`, `rights_note` — per this document's source (see doc 04).
- `capture_history[]`, `supersedes`, `superseded_by`, `related_documents[]`, `provenance_note`.
- Optional after checking against the source: `verification{}`, `corrections[]`.

**Rule:** never claim more fidelity than you verified. A visible gap is an asset; a hidden one is a liability.
