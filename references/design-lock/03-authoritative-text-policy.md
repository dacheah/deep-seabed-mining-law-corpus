# 03 — Authoritative-text policy (TEMPLATE)

- **Authentic-language only** in `authoritative/`. Store the text in the language(s) in which the
  instrument was enacted/issued. Any translation is derived and unofficial (doc 06).
- **Prefer official sources** — the issuer or an official gazette/registry/depositary. A clean copy
  from a non-official aggregator is `source_is_official: false`.
- **Reproduce faithfully, including defects.** If the official source contains a typo or spacing
  error, reproduce it and flag it (`text_fidelity`, `provenance_note`) — do not silently "fix" it.
  Corrections are dated `corrections[]` entries, made only against the official source.
- **Gaps are flagged, not filled.** If only a translation exists and no authentic text can be
  obtained, ingest an `authoritative_status: authoritative_missing` placeholder (no `text.txt`) and
  attach the translation in the derived layer.
- **Fidelity ladder** — set it honestly and upgrade it only after a real check against the source,
  recording a `verification{}` record.

[DOMAIN note: list which languages/issuers are authoritative for your field.]
