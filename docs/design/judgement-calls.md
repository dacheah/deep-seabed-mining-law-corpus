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
**Status (2026-09-16, annual review #1):** the held text is **superseded**. The 31st session negotiated
the Further Revised Consolidated Text **ISBA/31/C/CRP.1/Rev.3** across its two parts, listed Item 11
"with a view to adoption" in July 2026, and did **not** adopt: the Council adopted **ISBA/31/C/38**
(decision on the approach to the continuation of the elaboration) and contemplated a third part of the
session. The Dec-2025 draft stays as the dated draft it was; the newer revision is due as its own
version (**issue #11**). Still no in-force exploitation regulation, so this JC governs unchanged.

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

**Status (2026-09-17, issue #9 — the case-file classes this JC did not name).** The 18 July 2026
provisional-measures orders in both cases, the 10 June orders, and the judges' declarations published
with them are **ingested** (the declarations as records of their own, identified by date — the orders
carry no official number, and minting one would invent a citation). Three further classes are ruled
**out** of `authoritative/`:

- **Hearing transcripts** (`ITLOS_PV26_C34-35_1..4_E.pdf`) — verbatim records of what was said. They
  state no law, they are the least authoritative rendition of anything in the case file, and
  ingesting four large scans would buy OCR cost and corruption risk for no legal content.
- **Party documents** — provisional-measures applications, final submissions, Nauru's written
  statement, the ISA's response. Already excluded when this JC was decided: an application states *a
  party's case*, not law. Issue #9 asserted a precedent for including them ("the corpus already holds
  the Case 34/35 Applications") — **that precedent does not exist**. The corpus's ITLOS holdings are
  six orders, three declarations and the 2011 Advisory Opinion; no application, submission, statement
  or transcript, from the main case pages or anywhere else. Checked record by record on 2026-09-17.
- **Compliance filings** (the applicants' report of 31 August 2026 on compliance with the provisional
  measures, and the Registrar's letter covering the ISA's initial report) — self-reported filings by
  the parties, unverified by the Tribunal. `authoritative/` holds operative instruments, extended once
  to judicial declarations; a second extension, to "whatever is in the case folder", dissolves the
  boundary that makes the layer citable.

**Consequence:** all three classes are recorded in `queue/candidates.md` with the official case-page
URLs, so the trail exists without the case file entering the layer. If the corpus is ever to carry the
proceedings' own state under supervision — what the compliance filings, and the ISA's initial report
under them, are evidence of — that is a **new layer with its own rules and its own completeness
obligation**, argued on its own merits. It is not an expansion of the citable layer.

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

---

## JC-009 — A held draft can be superseded without any monitored page reporting a change
**Date:** 2026-09-16 (found by the first annual review, issue #1)
**Context:** the held Mining Code draft (`ISBA/31/C/CRP.2`, 23 Dec 2025) was superseded during 2026 by
the Further Revised Consolidated Text **ISBA/31/C/CRP.1/Rev.3**, negotiated across both parts of the
31st session, with adoption attempted in July 2026 and not achieved (Council decision ISBA/31/C/38).
No source-watch flag pointed at it: the monitored Mining Code pages were byte-stable, and the page that
did change (the 31st session page) was triaged as session documents rather than as "the draft you hold
is now historical".
**Options:** (a) leave the check to the annual review; (b) compare a held draft's official identifier
against the latest published revision at every sweep.
**Decision:** (a) for now, with the check named in the review and (b) raised as **issue #14**. "Latest
revision" is per-instrument knowledge (CRP vs CRP/Rev vs L vs WP series, and which session published
each), and a false *superseded* claim is worse than a late one: it invites an ingest of a document that
supersedes nothing.
**Reason:** the corpus's value is being the reference record of how the regime formed, so a draft that
quietly becomes historical is a wrong claim, not merely a late one — and it is the one error class that
survives the reproducibility gate, which will re-derive the superseded text byte-for-byte forever.
**Status (2026-09-16):** applied — the superseded draft is retained unchanged and now carries
`superseded_by`; the newer revision is held as `isa/draft/exploitation-code-2026`; the record-level
freshness check is issue #14. **(2026-09-17, issue #15:)** the newer revision is no longer artefact-only
— it carries a derived, reproducible `text.txt`; see JC-010's resolution.

---

## JC-010 — A marked-up revision is not a text record: hold the artefact, never launder the marks
**Date:** 2026-09-16 (issue #11, from the annual review, issue #1)
**Context:** the latest text of the Mining Code draft, ISBA/31/C/CRP.1/Rev.3 (19 June 2026), carries
this revision's changes as VISUAL marks — inserted text set apart by formatting, deleted text left in
place. `pdftotext` cannot tell them apart and merges them where they share a position: at Regulation 1
the paragraph numbers come back as `4.`, `[45.`, `56.`, `67.`, `[78.`, `89.` (the previous numbering
and the renumbering rendered as single tokens), and a renumbered cross-reference comes back as
`Subject to paragraph 1 and 3the Schedule`, an insertion abutting existing text with no space.
**Options:** (a) store the extracted text as usual with the caveat declared in `provenance_note`;
(b) hold the byte-exact official PDF and store no text; (c) derive the text from the publisher's Word
form, whose changes are machine-readable tracked changes.
**Decision:** (b) now; (c) raised as a convention question, not taken (issue #15). (a) is refused.
**Reason:** (a) asserts deleted wording as text and mints paragraph numbers the document does not use.
That is a wrong claim, not a rough one — and it is the one error class the reproducibility gate cannot
catch, because a re-derivation reproduces the corruption byte-for-byte forever with a green tick. Same
shape as the `"Part XI, Section 5."` → `"5. 70."` corruption found under issue #9. (c) is faithful, but
`text.txt` in this corpus is *defined* as the committed extractor's output over `original.*`; deriving
it from a second artefact is a change to what the field means, so it needs a decision rather than a
script. The Word form is preserved in `capture/` so the derivation needs no further fetch.
**Status (2026-09-16):** applied — `isa/draft/exploitation-code-2026` holds the byte-exact official PDF
(3,661,689 bytes, sha256:c0d01ee2…c68c16, 335 pp) and stores no text (`authoritative_status:
authoritative_missing`), the gate reads it as "excluded — no stored text by design", and
`isa/draft/exploitation-code-2025` carries `superseded_by`. What a reader may rely on here: the file,
its hash, its page count, its date, and the citation — not a quotation.

**RESOLVED (2026-09-17, issue #15) — option (c) adopted, narrower than "a second artefact":** the text
is derived from the official Word form, but by the SAME committed extractor and stored under the same
name, so nothing about what `text.txt` means changes. `original_format` stays `pdf` (the PDF remains the
artefact a reader opens and the page-citation anchor) and the Word form is held beside it as
`original.docx`, recorded in `capture_history` with its own hash. `scripts/extract.py` gains a
`DOCX_EXTRACTORS` registry: for `isa/draft/exploitation-code-2026` the text is the Word form's paragraphs
with tracked changes resolved — insertions kept, deletions dropped, **nothing substituted for a deletion**
— and the 160 single-cell tables that carry secretariat and working-group commentary excluded on that
structural test.

Three things this decision rests on, all measured on 2026-09-17:
- **Nothing may be substituted for a deletion.** Substituting a space looks right on the obvious case
  (`defined]` + deleted space + `for` → `defined] for`) but splits words everywhere else, because most
  deletions in this document sit *inside* a word: `(a)` + deleted `t` + `he principle` becomes
  `(a) t he principle`, and `4` + deleted `5` + `.` becomes `4 .`, which stops the paragraph reading as
  a numbered item at all. Removing the deletion and nothing else is Word's own "accept all changes".
- **The commentary is separable by structure, not by guessing at prose.** Every one of the 160 commentary
  boxes is a table with one row and one cell; the Schedule's definitions table (121 rows, 2 cells) and
  every other multi-cell table is instrument text and is kept.
- **The result is the record's text, not a second-class citizen.** Because the resolver is committed code
  over a byte-exact original, the text re-derives byte-exactly and the reproduce gate verifies it on every
  push. No `repro-policy.json` exclusion was needed — which is what made option (c) worth taking rather
  than declaring: the corpus's reproducibility claim now covers the live draft instead of stopping short of it.

**Why this is not a laundering of the marks:** the marks are not interpreted, only resolved. What was
refused in (a) was asking `pdftotext` to answer a question its output cannot answer; what is done here is
reading the publisher's own machine-readable record of the same revisions. Residual, stated: where the
mark-up carried a space *inside* a deletion the words abut (`...are defined]for the purposes...`) — the
document's own mark-up, resolved exactly as Word resolves it, and recorded in `provenance_note`.
**Status (2026-09-17):** applied — `text_fidelity: extracted_verified`, `authoritative_status:
authentic_text`, text sha256:252a0da5…de5 (570,727 bytes), attestation authored in CI under the pinned
toolchain; JC-010's own question is settled and the rule is in doc 03 (authoritative-text policy).

## JC-011 — A margin-block page: read the record with the printed layout, not the default reading order
**Date:** 2026-09-18 (issue #13)
**Context:** the AGO's Revised Editions of Tonga's Seabed Minerals Act 2014 typeset each section as a
heading block — the number in a margin column, the title beside it — with the body in a second column.
`pdftotext`'s default reading order pairs those numbers with the *neighbouring* section: the assembly
produced `Section 6. (a).`, `Section 9. 10.`, and over the whole Act captured 85 of its 125 sections.
**Options:** (a) re-pair the numbers with the titles printed in the document's own Arrangement of
Sections; (b) adopt PyMuPDF as a per-record toolchain (the sibling BBNJ corpus has that precedent:
`un/unclos-1982` under pymupdf 1.28.2, its own attestation and its own branch in the validate check);
(c) read the same pinned poppler with `-layout`.
**Decision:** (c).
**Reason:** the read flag is a per-record *argument* on the same pinned toolchain — exactly parallel to
the existing `PDF_RAW` for the two UNCLOS language copies — so the toolchain contract, the attestation
and the gate's re-derivation are unchanged, and the args recorded in the attestation say what was
actually run. (b) reaches the same result through a larger change: a third toolchain branch in the
workflow's assert, for one record. (a) works from the instrument's own apparatus, but mis-pairs
silently wherever the Arrangement and the body disagree — the exact failure class this corpus exists
to avoid.
**Status (2026-09-18):** applied — 125 sections against the Arrangement's 125, zero gaps, no furniture
and no invented token in the text.

## JC-012 — A schedule is part of the instrument and is not sectioned
**Date:** 2026-09-18 (issue #13)
**Context:** the Nauru Seabed Minerals Authority Regulations 2025 end in three Schedules of forms. A
form's own item numbering continues the section sequence (Schedule 3 item 64 follows s.62), so the
section assembler minted a Section 63 and a Section 64 that the instrument does not have: 64 assembled
against the Table of Provisions' 62.
**Options:** (a) accept the extra sections; (b) drop the schedules from the text; (c) stop the numbered
assembly at the SCHEDULE heading and keep everything after it as printed.
**Decision:** (c).
**Reason:** (a) asserts sections that do not exist — a wrong citation, not a rough one, and one the
reproduce gate would re-derive byte-for-byte forever with a green tick. (b) discards operative material:
the schedules carry the forms a contractor actually files. (c) keeps them and stops the one inference
that is wrong there: after the heading no bare number is read as a section, and the printed line breaks
are kept as paragraph breaks so the form structure stays legible.
**Status (2026-09-18):** applied — 62 sections, zero gaps, 873 schedule lines retained.

## JC-013 — National legislation whose reuse terms are unstated
**Date:** 2026-09-18 (issue #13)
**Context:** none of the four national-law records carries a stated reuse licence. The Nauru copies
come from the ISA's National Legislation Database, whose terms govern the database and which states that
it reproduces State submissions "in the form and the language(s) received", "not formally edited and/or
translated"; the Tonga copy comes from the Attorney General's Office register. Both are the State's own
text; neither states terms for reuse.
**Options:** (a) treat government legislation as effectively public and record a permissive licence;
(b) refuse to ingest without stated terms; (c) ingest, with the licence recorded as unstated, the
reasoning written down, and a takedown path.
**Decision:** (c).
**Reason:** (a) is a claim about someone else's rights that we cannot source — the same class of error
as minting a citation. (b) would leave the primary law of two sponsoring States out of the corpus on a
paperwork question, when the corpus's job is to hold it accurately and say what is uncertain. What must
not happen is silence: the licence field says `government-legislation-terms-unstated` and the
`rights_note` on each record says where it came from and what the source does and does not state.
**Status (2026-09-18):** applied; a per-statute rights determination is recorded as an open item.

## JC-014 — The AKN registry grows by mapping, never by hand-editing a record
**Date:** 2026-09-18 (issue #13)
**Context:** four new records needed AKN Work URIs. `validate_corpus.py` mints them from
`schema/akn-registry.json` and FAILS any record whose stored fields differ from the mint, so a
hand-written URI is refused by construction — which is how a first-draft
`/akn/nr/regulation/…` (missing the `act` doctype the registry's own doctypes map supplies) was caught.
**Options:** (a) write the URIs into the records; (b) add the jurisdictions to the registry and let the
mint populate the records; (c) leave all four records without URIs.
**Decision:** (b) — `NRU → nr` and `TON → to` added to `alpha3_to_alpha2`, then
`scripts/migrate_akn.py --apply` (never an editor) wrote the records.
**Reason:** both are codes ISO 3166-1 actually assigns, so the country slot is spec-legal on the same
basis as every other nation-state in the map; nothing was invented to make a URI possible. (c) would
leave a real, closeable gap open out of caution.
**Status (2026-09-18):** applied — three records mint under basis `iso3166`. Tonga declines, and the
reason is recorded by the mint itself: its `version_id` (`2020-revised-edition`) is not an ISO date and
the AGO's Revised Edition carries none on its face, so no Work date can be derived; minting one would
invent it. Wrinkle worth stating plainly: the mint labels a code-bearing body's remaining failure
`unmapped` (a gap in our mapping), while Tonga's missing slot is arguably a fact about the source —
which that vocabulary reserves for `none`. Left as written rather than special-cased in shared code;
what a reader may rely on is the note, which names the failing slot.

## JC-015 — ISBA/31/A/11 is a secretariat note about the proceedings, not an instrument
**Date:** 2026-10-14 (issue #16)
**Context:** the 31st session finalised its document set and `ISBA/31/A/11` appeared on the session page
under the Assembly's Item 21 (Other matters). The document was read before any decision was taken:
"Provisional Measures Orders prescribed by the Seabed Disputes Chamber of the International Tribunal
for the Law of the Sea on 18 July 2026 in Cases No. 34 and 35 — Note by the secretariat",
advance unedited version, 26 July 2026, English only. Its paragraph 5 states that it refers solely to
publicly available information, does not address matters pertaining to the merits, and reports the
state of proceedings pending before the Chamber.
**Options:** (a) ingest it as an ISA session document, on the strength of its `ISBA/` symbol; (b) record
the symbol and its URLs in `queue/candidates.md` and mint no record; (c) ingest it as the corpus's text
of the 18 July 2026 orders.
**Decision:** (b).
**Reason:** (c) is the error JC-007 exists to prevent — the note's operative content belongs to the
Chamber, and this is the Authority's own summary of it, the Authority being the respondent in both
cases; a litigant's summary must not become the corpus's record of another body's act. The authentic
text is the Tribunal's, and the ITLOS renditions are already queued in `queue/manifests/`
(`ready__itlos-order-case34-order-18jul2026.json`, `ready__itlos-order-case35-order-18jul2026.json`),
the case file as a whole having been ruled out of `authoritative/` on 2026-09-17 (issue #9). (a) would
put a status update into a layer whose rule is the authentic text of instruments (doc 03). What the
note is good for is the trail: it is the Authority's dated statement that the orders were before the
Assembly under Other matters.
**Status (2026-10-14):** applied — candidate row added, no record minted, the session page remains a
watched source.

## JC-016 — A notice of receipt of a deep seabed mining application is recorded, not ingested
**Date:** 2026-10-14 (issue #16)
**Context:** the NOAA deep-seabed-mining page's 23 September 2026 update added The Metals Company
USA's consolidation application (exploration licence plus commercial recovery permit): Federal
Register document 2026-16869, published 19 August 2026, Docket No. 260706-0163, with a comment period
to 19 October 2026 and a virtual public hearing on 13 October 2026 — plus a notice of intent to
prepare an Environmental Impact Statement for the proposed issuance of an exploration licence for
`USA-B`, document 2026-16722, published 17 August 2026, Docket No. 260707-0164. The US track holds
the statute and the regulations (JC-001: `usa/statute/dshmra-1980`, `usa/regulation/cfr15-970-2026`,
`cfr15-971-2026`).
**Options:** (a) ingest the Federal Register notices as US-track instruments; (b) record them, with
their URLs and docket numbers, in `queue/candidates.md` and leave the US track unchanged; (c) treat
the application itself as a document of the corpus.
**Decision:** (b).
**Reason:** a notice of receipt states no rule and grants nothing; the application, the EIS notice and
the hearing are administrative steps toward a permit, and a company's application is not law — the
same distinction as JC-007's party documents. (c) confuses the application with the permit that may
follow it. What a reader needs from these notices is the state of the application queue, which the
candidate row carries with dates. **If a commercial recovery permit is issued, that is a State act and
a new scope question** — not covered by this decision.
**Status (2026-10-14):** applied — candidate row added; nothing in `authoritative/usa/` changed; the
NOAA page remains a watched source, being the only place the application queue is listed in one place.

## JC-017 — A second notice of receipt adds a queue entry, not an instrument
**Date:** 2026-10-14 (issue #16, second triage pass)
**Context:** the triage of the nine sources whose baselines date from 1 October 2026 read the watched
Federal Register JSON feed directly, and exactly one document has been published on it since:
**2026-20830**, published **13 October 2026**, **91 FR 64880–64881**, Docket No. 260930-0006 (National
Oceanic and Atmospheric Administration, Department of Commerce) — "Deep Seabed Mining: Notice of
Receipt of Application for Deep Seabed Mining Exploration License and Announcement of Public Comment
Period and Virtual Public Hearing", on **Eco Minerals, Inc.**'s application for an exploration
licence, with comments closing **14 December 2026**. The US track holds the statute and the
regulations (JC-001); the earlier Metals Company USA documents are recorded at JC-016.
**Options:** (a) ingest the notice as a US-track instrument; (b) record it in `queue/candidates.md`
and leave the US track unchanged; (c) treat the application as a document of the corpus.
**Decision:** (b).
**Reason:** JC-016's reason applies unchanged — a notice of receipt states no rule and grants
nothing, and the class does not change with the applicant. What this row adds that JC-016's could not
is that the US queue now carries a **second applicant**: the record is worth keeping precisely
because the corpus holds the statute and the regulations and not the queue, which is the only place
the queue is listed. An exploration licence issued under the Act and its implementing regulations
would be a State act and would open the same scope question JC-016 left open for a commercial
recovery permit.
**Status (2026-10-14):** applied — candidate row added; nothing in `authoritative/usa/` changed.

## JC-018 — The 31st session's second part holds no operative text the corpus lacks
**Date:** 2026-10-14 (issue #16, second triage pass)
**Context:** the September-2026 ISA documents were resolved through the Authority's per-symbol
document pages rather than the session page's row order, which associates a document's per-language
links with the *following* row — the file first fetched for `ISBA/31/C/38` was internally
`ISBA/31/C/37`, and the one fetched for `ISBA/31/C/L.13` was internally `ISBA/31/C/L.12`. Verified
this way: `ISBA/31/C/38` (24 July 2026), the Council's "Decision … on the approach to the
continuation of the elaboration of rules, regulations and procedures relating to exploitation and
resolution of the remaining key outstanding issues", under agenda item 11, "Consideration, with a
view to adoption, of the draft regulations on exploitation of mineral resources in the Area"; its
draft `ISBA/31/C/L.13`; the revised indicative list `ISBA/31/C/CRP.7` (4 July 2026, English only),
whose explanatory note records that elaboration continues under the thematic approach set by the
Council at its thirtieth session (`ISBA/30/C/18`); and `ISBA/31/C/19/Rev.1/Add.1` (advance unedited
version, **11 September 2026**, English only), "Statement of the President on the work of the Council
… during the second part of the thirty-first session", opening at the 355th meeting on 13 July 2026.
Administrative documents of the same part: `ISBA/31/C/30` (relinquishment report, Republic of
Korea's cobalt-rich ferromanganese crusts contract), `ISBA/31/C/32` (election to fill a Legal and
Technical Commission vacancy under article 163(7) of the Convention), `ISBA/31/C/33`,
`ISBA/31/C/34` (decision relating to the reports of the Chair of the Legal and Technical Commission),
`ISBA/31/C/37`.
**Options:** (a) ingest C/38 and the part's documents as ISA-track instruments; (b) record them in
`queue/candidates.md`, noting that C/38's outcome is already carried by the corpus; (c) ingest the
President's statement alone as a session record.
**Decision:** (b), with the statement recorded rather than ingested.
**Reason:** adoption did not follow, and the corpus already carries both the fact and the citation —
`docs/annual-review-2026.md` and the draft-code record's provenance note date the Council's decision
against `ISBA/31/C/CRP.7` and its draft `ISBA/31/C/L.13`. So (a) would fill no gap in the account of
the code's status: it would add a Council decision to an ISA track whose record types are
`isa_regulation` and `isa_draft` only — an instrument-type question for the maintainer, not a
gap-filling one. Nothing else in the part holds operative text the corpus lacks: C/38 defers
elaboration, and the remainder is administration. The President's statement is a **summary record of
proceedings**, the class JC-015 declined to ingest, and here the boundary is sharper still: the
corpus cites the *first* part's statement (`ISBA/31/C/19/Rev.1`, para. 43) as authority for the
President's proposal at the 354th meeting, so statements of the President are citable in this corpus
whilst not being held as records; the Add.1 is the same class for the part whose outcome the corpus
already records. Holding them as a class is a convention question, not a per-document decision.
**Also recorded:** the watched source "ISA — Exploitation: Official documents" ends its document list
at `ISBA/29/C9`, so it is stale by two sessions and its digest movement is not instrument movement;
the session pages are the live watch for code documents.
**Status (2026-10-14):** applied — candidate rows added; no record minted; the draft-code record's
status (draft, not in force) stands. The source page's staleness is noted here rather than patched in
`monitoring/sources.json`, since replacing a watched source is a maintainer decision.
