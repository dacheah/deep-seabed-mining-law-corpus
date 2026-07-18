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
**Status (2026-07-03):** applied — DSHMRA ingested as `usa/statute/dshmra-1980` (jurisdiction USA, document_type national_statute); the `us_non_unclos_parallel_regime` concept marks its provisions.

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
**Status (2026-07-03):** applied — the Dec-2025 consolidated draft (ISBA/31/C/CRP.2) is ingested as
`isa/draft/exploitation-code-2025`, authentic draft text, `entry_into_force_date: null`, short_title and
provenance marked DRAFT/NOT IN FORCE; alternatives preserved verbatim.

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

---

## JC-006 — How to store multiple authentic languages of one instrument
**Date:** 2026-07-11
**Context:** UNCLOS, the 1994 Agreement and the ISA regulations are authentic in the six UN languages;
the 2011 Advisory Opinion is authentic in English and French. The schema stores one `language` per
record in `authoritative/<corpus_id>/<version_id>/`, so two languages of the same instrument need
distinct records.
**Options:** (a) language sub-folder under one version; (b) encode language in `version_id`;
(c) a language-suffixed `corpus_id`, one sibling record per language.
**Decision:** (c). The first-stored language (English here) keeps the **base** `corpus_id`
(e.g. `itlos/advisory-opinion/sdc-area-2011`). Each additional authentic language is a **sibling
record** whose `corpus_id` is the base plus an ISO-639 suffix (`…-fr`, `…-es`, `…-ar`, `…-zh`,
`…-ru`). Every language record carries `language: <iso>`, the full `authentic_languages` list, the
same `version_id` (the instrument's date), and cross-links to its siblings via `related_documents`.
**Reason:** existing English `corpus_id`s stay stable (external references don't break — the doc 01
rule); it needs no schema or script change (the tools glob by folder); and each language remains a
first-class, independently-hash-verified authentic text — none is treated as a translation of another
(translations stay in the derived layer, doc 06).

**Status (2026-07-11):** Proven at scale. The three ISA exploration regulations are now stored as
sibling records in **five** authentic languages — EN (base), FR, ES, RU, ZH — all byte-exact
reproducible by `scripts/extract.py`, all cross-linked, all concept-tagged (RU/ZH structure is parsed
via `concepts.HEADER_PATTERNS_EXTRA`: `第N条` and the Cyrillic `Правило/Раздел/Часть/Приложение`
headers; RU/ZH concept phrases were added to `concepts.KW`). Arabic is **held** — tested 2026-07-11: the PDFs are in logical order but carry font-encoded reversed ligature clusters (e.g. المجلس→اجمللس) that every extractor reproduces identically; a shaping-based reorder pass was measured and rejected (it corrupted more words than it fixed). Needs a properly-encoded source or Arabic-literate review (see docs/source-map.md, "Multilingual coverage & holds").

---

## JC-007 — Are ITLOS contentious proceedings in scope, and are party pleadings law?
**Date:** 2026-07-18
**Context:** The source monitor was corrected on 2026-07-18 to watch the ITLOS **case register**
(`/cases/list-of-cases/`) rather than the overview page it had been pointed at, which carried only
prose and a case count. That immediately surfaced two contentious cases against the Authority —
**Case No. 34** (*Nauru Ocean Resources Inc. v. ISA*) and **Case No. 35** (*Tonga Offshore Mining
Ltd. v. ISA*), both instituted 30 May 2026 and arising from an ISA inquiry into sponsored
contractors. Case 34 has produced **Order 2026/6 of 24 June 2026**, and a provisional-measures
hearing opened on 2 July 2026. Doc 05 as written admitted exactly one item of case law — the 2011
Advisory Opinion (Case 17) — so neither case was in scope, and neither could have been found while
the source URL was wrong.

**Two questions:** (a) are ITLOS proceedings concerning the Area in scope at all; (b) if so, does
that extend to the parties' pleadings as well as the Tribunal's own decisions.

**Options:** (a) hold scope at Case 17 alone; (b) admit ITLOS **decisions** — advisory opinions,
judgments, orders — in proceedings concerning the Area; (c) admit the whole **case file**, pleadings
and annexes included.

**Decision:** (b). Scope extends to decisions of the Tribunal and its Seabed Disputes Chamber in
proceedings concerning the Area. **Party pleadings are not ingested** into the authoritative layer;
they are recorded in `queue/candidates.md` with their official URLs.

**Reason:** this corpus holds *the law governing the Area*. An order or judgment is the Tribunal
exercising jurisdiction under Part XI and stating law. An application states *a party's case*, and is
not law however official the filing. The schema reaches the same conclusion independently:
`binding_force` has no honest value for a pleading, because a pleading is not an instrument capable
of binding or not binding — when a required field cannot be answered truthfully, that is evidence the
record does not belong. Admitting pleadings would also convert a law corpus into a case-file corpus,
which carries a different and much heavier completeness obligation: a case file is only meaningful
when substantially complete — both parties, annexes, transcripts — whereas a decision stands alone.

**Consequence:** Order 2026/6 (Case 34) is in scope and queued for capture and ingest. The NORI and
TOML Applications of 30 May 2026 are recorded, not ingested. Case 35 currently lists no Tribunal
decision. ITLOS press releases are excluded as communications *about* proceedings; the extraction
schema excludes them structurally by URL path rather than by manual filtering.

**Status (2026-07-18):** decided. Order 2026/6 not yet captured. Cases 34 and 35 are now monitored
sources in their own right, at document level — these are live proceedings, not closed records.

---

## JC-008 — Identifying multiple decisions within one case
**Date:** 2026-07-18
**Context:** JC-007 admitted ITLOS decisions in Area proceedings. Doc 02's shape
`<authority>/<type>/<slug>-<year>` assumes **one decision per matter**, which held while the only
case law was the 2011 Advisory Opinion. It does not hold for contentious proceedings: Case 34 has
already produced Order 2026/6, held a provisional-measures hearing, and will produce further orders
and a judgment. These are **distinct instruments, not versions of one text**, so `version_id` cannot
separate them — that field records textual states of the *same* instrument.

**Options:** (a) party shorthand — `itlos/order/nori-isa-order6-2026`; (b) the Tribunal's own case
number — `itlos/order/case34-order6-2026`; (c) subject-descriptive slugs, as `sdc-area-2011`.

**Decision:** (b). ITLOS decisions in contentious proceedings take
`itlos/<type>/case<N>[-<discriminator>]-<year>`, where `<N>` is the ITLOS case number and the
discriminator is the official decision number where a case may yield several of that type:

```
itlos/order/case34-order6-2026     Case 34, Order 2026/6 of 24 June 2026
itlos/judgment/case34-2026         Case 34, judgment (one per case — no discriminator)
```

**Reason:** `corpus_id` is stable forever (doc 01), so it must be built from the most stable official
identifier available. ITLOS case numbers are assigned by the Tribunal, unique and permanent. Party
shorthand is none of those: "NORI" is unofficial, party names change through succession or
intervention, and Cases 34 and 35 are both "*X* v. ISA" — near-identical party slugs invite exactly
the confusion that a stable identifier exists to prevent. Subject-descriptive slugs (option c) do not
scale to a case producing many decisions. The readability objection is answered by the schema itself:
`title` and `short_title` carry human meaning, and `sdc-area-2011` already relies on this by putting
"(Case No. 17)" in `short_title`. Optimising the identifier for readability duplicates `short_title`
and pays for it in stability.

**Grandfathering:** `itlos/advisory-opinion/sdc-area-2011` and its `-fr` sibling are **not renamed**.
Identifier stability outranks retrospective consistency, and a rename would break `related_documents`
links in five other records. The rule applies to decisions identified from 2026-07-18 onward.

**Status (2026-07-18):** decided; first applied to `itlos/order/case34-order6-2026`, not yet ingested.
