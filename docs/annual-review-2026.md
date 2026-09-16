# Annual review 2026 — deep seabed mining law corpus

**Review date:** 2026-09-16 · **Reviewer:** Jarvis (agent), for Dan Cheah
**Cadence:** the repo's Phase 2 cadence — annual — run for the first time per issue #1.
**Method:** every item below was checked against the live official source on 2026-09-16, not against
memory or the last report. Evidence (document identifiers, dates, URLs) is recorded with each finding
so a later reader can re-run the check. Where a source was already monitored, the report of
2026-09-15 (`monitoring/last_report.md`) was read first and the finding verified independently.

---

## 1. Integrity gate

`python3 scripts/validate_corpus.py` → **OK**: 37 authoritative records, 37 derived records, schema and
hash checks clean, path identity clean, zero-record floor satisfied. The corpus grew from 30 to 37
records this year, all seven additions being ITLOS Case 34/35 documents (issue #9).

## 2. The year's source watch

`monitoring/last_report.md` (2026-09-15, monitor v3.10): **22 sources · 0 changed · 0 suspect · 0
error**. The year's source-watch issues were all triaged and closed with no unmatched flags:

| Issue | Date | Outcome |
|---|---|---|
| #2 | 2026-08-01 | triaged, closed |
| #3 | 2026-09-01 | triaged, closed |
| #8, #10 | 2026-09-14 | the ITLOS incidental-proceeding sub-pages (the finding that led to issue #9) |
| #5 | — | ISA page churn: the v3.10 entity fix + two narrow `ignore_patterns` |
| #6 | — | Order 2026/7 sequence gap: resolved as the unnumbered order of 18 July 2026 |
| #4, #7, #9 | — | ingest, CI engine gate, and this review's scope question |

**Observation worth keeping:** the page layer *did* flag the ITLOS gap in September. What it could not
do is notice that a **document already held had been superseded** — no monitored surface compares a
held draft against the latest published revision. That is the gap this review closes by hand (item 5),
and it is a candidate for a record-level check in the monitor (see *Carried forward*).

## 3. UNCLOS Part XI and the 1994 Implementation Agreement

No correction, no amendment, no new authentic-language text published for either instrument: the
DOALOS pages are unchanged across the year's sweeps. Both are held in **EN, ES, FR**; the Russian and
Chinese authentic texts are not held, and the Arabic texts remain *held* under JC-006's measured
defect (font-encoded reversed ligature clusters — every extractor reproduces them identically and a
shaping-based reorder pass made things worse; needs a properly-encoded source or an Arabic-literate
review). **Recorded, not treated as a defect:** the multilingual rollout is complete for the ISA
regulations (five languages) and stopped at the two UN instruments (three). Adding RU and ZH siblings
is straightforward `-ru` / `-zh` work whenever it is wanted.

## 4. ISA — exploration regulations and LTC guidance

**No new or amended exploration regulation.** The operative set is unchanged and complete in the
corpus: nodules (ISBA/19/C/17, amended 2013), sulphides (ISBA/16/A/12/Rev.1, 2010) and crusts
(ISBA/18/A/11, 2012), each in five authentic languages.

**LTC recommendations were updated** and remain unheld — notably a new
**ISBA/21/LTC/15/Rev.1** (content, format and structure of annual reports, December 2025) and
ISBA/29/LTC/7 and ISBA/29/LTC/8 (2024) beside the older ISBA/25/LTC/6/Rev.3.
These are guidance to contractors and sponsoring States, not instruments, so they stay out of
`authoritative/` on the existing scope boundary. **Unchanged decision, restated here because it is the
first time the corpus has declined a live ISA document**, and a reader is entitled to see it recorded
rather than inferred from silence.

## 5. The Mining Code — the material finding of this review

**The Code was not adopted.** What happened instead, in the 31st session (2026):

- **Part I** (LTC 23 Feb – 6 Mar; Council 9 – 19 Mar 2026) took up Agenda Item 11 on the **Further
  Revised Consolidated Text**, presented as **ISBA/31/C/CRP.1/Rev.3** — a revision *newer than the text
  this corpus holds*.
- **Part II** (Council 13 – 24 Jul 2026) listed "Consideration, **with a view to adoption**, of the
  draft regulations on exploitation" and negotiated the Further Revised Consolidated Text, against an
  updated indicative list of outstanding issues (**ISBA/31/C/CRP.7**).
- Adoption did not follow. The Council adopted **ISBA/31/C/38**, "Decision … on the approach to the
  continuation of the elaboration of rules, regulations and procedures relating to exploitation and
  resolution of the remaining key outstanding issues" (July 2026; draft **ISBA/31/C/L.13**), and
  contemplated a **third part of the thirty-first session**.

**Consequence for the corpus.** The held draft — `isa/draft/exploitation-code-2025`, version_id
`2025-12-23`, official citation ISBA/31/C/CRP.2 (23 Dec 2025), 194 pp, complete — **is no longer the
latest text**. JC-002 (drafts are ingested as dated, clearly-marked drafts) applies exactly as written,
so the fix is another dated draft version, not a rewrite of the existing one. Raised as **issue #11**.

**What did not change:** JC-002's substance. The Code is still a draft, `entry_into_force_date: null`,
and no in-force exploitation regulation exists to ingest.

## 6. ITLOS / Seabed Disputes Chamber

The year's ITLOS work is Cases 34 and 35, and it is complete in the corpus: seven documents ingested
in September (the two orders of 18 July 2026, the three judges' declarations, and Orders 2026/3 and
2026/4 of 10 June 2026), on top of Orders 2026/6, 2026/8 and 2026/9.

Checked against the live case list today:
- **No new seabed-related proceeding.** The newest case, **No. 36 (Ghana/Togo maritime delimitation)**,
  is a boundary dispute with no Area dimension — outside this corpus's scope, recorded so the omission
  is deliberate rather than missed.
- The **2011 Advisory Opinion (Case 17)** is complete in English with its French authentic sibling
  (JC-004) — the checklist's "if still pending" is discharged.

**Watch item.** **ISBA/31/A/8** (Assembly, 2026): "Consideration of a request for an advisory opinion
from the Seabed Disputes Chamber … on matters relating to the legal implications for the ISA of
activities in the Area undertaken by **non-States Parties**". As of today **no such case appears on
ITLOS's list of cases**, so there is nothing to ingest yet — but if the request is transmitted, the
opinion will be the most significant addition to this corpus since the 2011 AO. Raised as **issue #12**.

## 7. US track

The corpus holds the statute (DSHMRA, 30 U.S.C. ch. 26) and both NOAA parts, 970 and 971, as
`official_consolidation` snapshots dated **1 July 2026** (JC-001 keeps this track distinct).

Checked against the Federal Register API today:
- **One rulemaking touched this track in 2026: the final rule "Deep Seabed Mining: Revisions to
  Regulations for Exploration License and Commercial Recovery Permit Applications" (doc 2026-01044,
  published 21 January 2026)**, following the August 2025 proposed rule (2025-14657).
- The held snapshots **post-date** that rule, so **no ingest is due** — the check the review exists to
  perform, and it passes.
- Since 1 July 2026 the activity is **licensing, not law**: a notice of intent to prepare an
  environmental impact statement for a proposed exploration licence to The Metals Company USA LLC
  ("USA-B", doc 2026-16722, 17 Aug 2026) and a notice of receipt of a consolidated application
  (doc 2026-16869, 19 Aug 2026). Neither changes 15 CFR 970/971; both are the kind of development the
  source watch will surface when it matters.

## 8. Sponsoring-state national law

**None is held**, and JC-005 ("never let an unofficial translation masquerade as authoritative") has
still never been triggered. The review's judgement: it should be triggered now, because the corpus has
just ingested the two contentious cases, and the sponsoring States in them are **Nauru** (NORI) and
**Tonga** (TOML).

- Sourcing route: the ISA's own **National Legislation Database on Deep Seabed Mining** (with the
  Pacific regional compilation), which exists precisely to hold this material in its authentic
  language — both States legislate in English, so the JC-005 problem does not arise for them.
- Candidate text identified: **Nauru's Seabed Minerals Authority Act 2024** (establishes the Nauru
  Seabed Minerals Authority and the sponsorship framework).

This is a **scope call, not a defect**: it adds a record class (`nn/`-style national law) the corpus
has never carried. Raised as **issue #13** for a decision rather than actioned here.

## 9. Judgement calls updated

- **JC-002** — status extended: the Dec-2025 consolidated draft is superseded; a superseded draft
  version is retained and a newer revision is ingested as its own dated draft (issue #11).
- **JC-009 (new)** — a held draft can be superseded without any monitored page reporting a change;
  the review is the check for it, and where possible the monitor should compare a held draft's
  identifier with the latest published revision.

## 10. Rebuild and commit

Derived layer rebuilt (`scripts/build_derived.py`), site rebuilt (`scripts/build_site.py`), integrity
gate re-run green, committed with this document.

---

## Carried forward

| # | Item | Owner |
|---|---|---|
| 11 | Ingest the Further Revised Consolidated Text Rev.3 (ISBA/31/C/CRP.1/Rev.3) — the held draft is superseded | next ingest job |
| 12 | Watch for the SDC advisory opinion on non-States-Parties activities (ISBA/31/A/8); add the 32nd session (2027) page to the watch list | monitor |
| 13 | Scope call on sponsoring-state national law (Nauru 2024, Tonga) — JC-005's first trigger | Dan |
| — | RU/ZH authentic siblings of the two UN instruments (JC-003/006 rollout) | whenever wanted |
| — | Arabic texts of UNCLOS, the 1994 Agreement and the ISA regulations remain held (encoding defect, JC-006) | needs a better source |
| 14 | A record-level "is a held draft still the latest revision?" check in the monitor | monitor |

**Bottom line for 2026:** the regime did not change. No Mining Code, no new ISA regulation, no
amendment to UNCLOS or the 1994 Agreement, no change to 15 CFR 970/971. What did change is that the
negotiation moved to a newer consolidated text and stalled on procedure, and that this corpus acquired
its first contentious-proceeding records. The single actionable gap the review found — a held draft
that is no longer the latest text — is exactly the kind of thing no page-level monitor can see.
