# Judgement calls (dated decision log)

Every non-obvious decision, with its options, the choice, and the reason. Never change a locked
design doc silently — record the change here.

---

## JC-001 — How to classify the US DSHMRA/OCSLA track relative to the ISA regime
**Date:** 2026-07-03
**Options:** (a) fold US law in beside ISA instruments as one seabed-mining body; (b) keep it as a
clearly distinct, parallel/alternative track.
**Decision:** (b). The US is **not** a party to UNCLOS and administers deep seabed hard-mineral mining
**outside** the ISA under DSHMRA (NOAA). It is a genuinely alternative legal basis that many states
regard as inconsistent with UNCLOS Part XI. We capture it, but keep it unmistakably distinct:
`jurisdiction: USA`, `usa/…` identifiers, `document_type: national_statute`/`national_regulation`, and
a `provenance_note` stating it operates outside the ISA regime. It is never placed under ISA/UN
identifiers.
**Reason:** neutrality and accuracy — record both regimes faithfully without implying the US track is
part of, or blessed by, the ISA regime.

---

## JC-002 — When a draft Mining Code revision is a citable version
**Date:** 2026-07-03
**Options:** (a) ingest every draft as it appears; (b) ingest no drafts until the Code is adopted;
(c) ingest drafts as dated, clearly-marked **draft** versions, promoted to in-force only on adoption.
**Decision:** (c). Each ingested draft revision is a version_id = its draft date, with
`authoritative_status: authentic_text` **but** a `provenance_note` and `short_title` marking it a
**draft, not in force**, and `entry_into_force_date: null`. Whether a given draft is "stable enough to
cite" is a human call flagged to the maintainer; the corpus records what each draft text *was*,
regardless.
**Reason:** the value now is being the reference record of *how the regime formed*; append-only
versioning captures that without pretending a draft is binding law.
**Status this session:** no draft ingested yet (foundational core only); policy pre-agreed for Phase 1.

---

## JC-003 — Which authentic language to store for multilingual instruments
**Date:** 2026-07-03
**Options:** (a) store all authentic languages; (b) store one authentic language now, record the rest
as a coverage gap.
**Decision:** (b) — store the **English** authentic text this phase (English is an authentic language
of UNCLOS/the 1994 Agreement and an official language of ITLOS and the ISA). The other authentic
languages (Arabic, Chinese, French, Russian, Spanish) are recorded as a coverage gap in
`provenance_note`, addable later as their own `authentic_text` records. This is **not** a translation
shortcut — each stored text is genuinely authentic.
**Reason:** proves the pipeline on clean canonical English text now; keeps the door open, honestly
flagged, for the equally-authoritative other languages.

---

## JC-004 — Authoritative language of the 2011 Advisory Opinion (Case 17)
**Date:** 2026-07-03
**Options:** English-authoritative vs French-authoritative.
**Decision:** read the authoritative-language statement **off the opinion itself** at ingestion (ITLOS
states which of the English/French texts is authoritative, per Rules art. 125) and record it in
`provenance_note` + `authentic_languages`. Do not assume.
**Resolution (2026-07-03):** the opinion's closing states "Done in English and French, **both texts
being authoritative**" — so English and French are equally authentic. Recorded in the record's
`authentic_languages` (`en`, `fr`) and `provenance_note`; the French authentic text is a coverage gap (JC-003).

---

## JC-005 — National sponsoring-state law available only in unofficial translation
**Date:** 2026-07-03
**Options:** store the unofficial translation as authoritative; ingest an `authoritative_missing`
placeholder + attach the translation in the derived layer.
**Decision:** the latter — never let an unofficial translation masquerade as authoritative text. Store
the authentic-language original when obtainable; otherwise `authoritative_missing` + derived-layer
translation, gap flagged.
**Reason:** the authentic-language rule (doc 03) is absolute.
**Status this session:** not yet triggered (no national law ingested this session).
