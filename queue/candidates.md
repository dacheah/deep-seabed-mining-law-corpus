# Candidate queue — borderline scope decisions

Borderline documents wait here for a recorded decision (doc 05). Nothing enters the corpus from here
without a dated note in `docs/design/judgement-calls.md`.

| Candidate | Why borderline | Decision | Date |
|---|---|---|---|
| Central Arctic Ocean Fisheries Agreement (2018) | fisheries, not Area law | comparative reference only — NOT ingested | 2026-07-03 |
| Antarctic Madrid Protocol Art 7 (mining ban) | different commons regime | comparative reference only — NOT ingested | 2026-07-03 |
| ISA DeepData datasets | scientific, not law | adjacency — NOT ingested (doc 05) | 2026-07-03 |
| ITLOS Case 34 — Application, Nauru Ocean Resources Inc. v. ISA (30 May 2026) | authentic official filing, but a party's pleading is not law; `binding_force` inapplicable | recorded — NOT ingested (JC-007) | 2026-07-18 |
| ITLOS Case 35 — Application, Tonga Offshore Mining Ltd. v. ISA (30 May 2026) | as above | recorded — NOT ingested (JC-007) | 2026-07-18 |
| ITLOS Cases 34 and 35 — four hearing transcripts (`ITLOS_PV26_C34-35_1..4_E.pdf`) | verbatim records of what was said; no operative text, least authoritative rendition in the case file | recorded — NOT ingested (JC-007, 2026-09-17) | 2026-09-17 |
| ITLOS Cases 34 and 35 — final submissions (NORI, TOML), written statement (Nauru), `ISA_Response_25.06.2026` | party documents: a party's case, not law; `binding_force` inapplicable | recorded — NOT ingested (JC-007, 2026-09-17) | 2026-09-17 |
| ITLOS Cases 34 and 35 — compliance reports filed 31 August 2026 (`Applicants_Report_on_Compliance_with_Provisional_Measures`, `Letter_ITLOS_Registrar_ISA_Initial_Report`) | self-reported filings by the parties, unverified by the Tribunal — not instruments | recorded — NOT ingested (JC-007, 2026-09-17); a case-state layer would be a new layer, not an extension of `authoritative/` | 2026-09-17 |
| ISA 31st session — `ISBA/31/A/11`, Provisional Measures Orders prescribed by the Seabed Disputes Chamber on 18 July 2026 (Cases No. 34 and 35), note by the secretariat | the operative content is the Chamber's, and this is the Authority's own summary of it — the Authority being the respondent; carries no operative text of its own | recorded — NOT ingested (JC-015) | 2026-10-14 |
| The Metals Company USA — consolidation application record (Federal Register 2026-16869; notice of intent 2026-16722) | administrative process toward a permit, not law; a notice of receipt states no rule and grants nothing | recorded — NOT ingested (JC-016) | 2026-10-14 |

## Recorded but not ingested — official URLs

Kept so the trail to the full case record exists without the pleadings entering the authoritative
layer (JC-007). If scope is ever extended to case files, start here.

- ITLOS Case 34, Application by Nauru Ocean Resources Inc., dated 30 May 2026, **filed with the
  Registry 5 June 2026** (filing date per Order 2026/6; the 30 May in the filename is the document
  date — do not treat a filename date as a legal date) —
  `https://www.itlos.org/fileadmin/itlos/documents/cases/34/2026.05.30_Nauru_Ocean_Resources_Inc._-_Application_92502112.1_.pdf`
- ITLOS Case 35, Application by Tonga Offshore Mining Ltd., 30 May 2026 —
  `https://www.itlos.org/fileadmin/itlos/documents/cases/35/2026.05.30_Tonga_Offshore_Mining_Ltd._-_Application_92502116.1_.pdf`

Both case pages also carry ITLOS **press releases**, which are communications *about* proceedings and
never enter `authoritative/`. The extraction schema excludes them structurally: case documents sit
under `/documents/cases/`, press releases under `/documents/press_releases_english/`.

## Recorded, not ingested — added 2026-10-14 (issue #16, JC-015, JC-016)

- **ISA 31st session — `ISBA/31/A/11`**, "Provisional Measures Orders prescribed by the Seabed
  Disputes Chamber of the International Tribunal for the Law of the Sea on 18 July 2026 in Cases
  No. 34 and 35 — Note by the secretariat", advance unedited version, 26 July 2026, English only
  (`sha256 220fb1ed324ec8eaf5313f3220e1789f78c81b0851e01557628f83c3e672ca6a`) —
  `https://isa.org.jm/wp-content/uploads/2026/07/ISBA_31_A_11-Provisional-Measures-Orders-prescribed-by-the-Seabed-Disputes-Chamber-of-the-ITLOS-on-18-July-2026-in-Cases-No.-34-and-35fv-AUV.pdf`
  · the 31st session page `https://www.isa.org.jm/sessions/31st-session-2026/` serves the final
  six-language set for the same symbol, under the Authority's numbered files; the symbol is the
  canonical citation. The note's own paragraph 5 states it refers solely to publicly available
  information, does not address the merits, and reports the state of proceedings pending before the
  Chamber.
- **The Metals Company USA** — "Deep Seabed Mining: Notice of Receipt of Consolidated Application
  for Deep Seabed Mining Exploration License and Commercial Recovery Permit and Announcement of
  Public Comment Period and Virtual Public Hearing", Federal Register 91 FR (19 August 2026),
  document 2026-16869, Docket No. 260706-0163 —
  `https://www.federalregister.gov/d/2026-16869` · and "Notice of Intent To Prepare an
  Environmental Impact Statement for the Proposed Issuance of an Exploration License to The Metals
  Company USA, LLC for `USA-B` (EISX-006-48-2CM-1779948024)", publication date 17 August 2026,
  document 2026-16722, Docket No. 260707-0164 — `https://www.federalregister.gov/d/2026-16722`.
  Recorded from the NOAA source watch (`US NOAA — Deep Seabed Hard Minerals Mining`), whose
  23 September 2026 update listed them; the comment period ran to 19 October 2026 and the virtual
  public hearing was 13 October 2026.

## The wider case file — ruled out 2026-09-17 (issue #9, JC-007)

Recorded here so the trail to the full case record exists without any of it entering the
authoritative layer. The documents below were listed by the per-case sub-pages the source watch
tracks from 2026-09-16; the case pages are the sources in `monitoring/sources.json`, and the file
names are as those pages list them.

- **Provisional-measures applications** (both cases, instituting the proceedings) — JC-007, party
  documents.
- **Final submissions** (Nauru Ocean Resources Inc., Tonga Offshore Mining Ltd.), **Nauru's written
  statement**, **`ISA_Response_25.06.2026`** — JC-007.
- **Four hearing transcripts**, `ITLOS_PV26_C34-35_1..4_E.pdf` — verbatim records; no operative text.
- **Compliance filings of 31 August 2026** — `Applicants_Report_on_Compliance_with_Provisional_Measures`
  and `Letter_ITLOS_Registrar_ISA_Initial_Report` (the ISA's initial report under the provisional
  measures). Self-reported, unverified by the Tribunal. These are the newest development in the
  proceedings and the reason a case-*state* view would need its own layer.

Case pages (official): Case 34
`https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-nauru-ocean-resources-inc-v-international-seabed-authority/`
· Case 35
`https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-tonga-offshore-mining-ltd-v-international-seabed-authority/`

## Recorded, not ingested — added 2026-10-14, second pass (JC-017, JC-018)

- **Eco Minerals, Inc.** — "Deep Seabed Mining: Notice of Receipt of Application for Deep Seabed
  Mining Exploration License and Announcement of Public Comment Period and Virtual Public Hearing",
  Federal Register document **2026-20830**, published **13 October 2026**, **91 FR 64880–64881**,
  Docket No. 260930-0006 (National Oceanic and Atmospheric Administration, Department of Commerce) —
  `https://www.federalregister.gov/d/2026-20830` · the only document on the watched Federal Register
  source published since the 1 October 2026 baseline, and the **second applicant** in the US queue
  after The Metals Company USA (JC-016). Written comments close **14 December 2026**; one virtual
  public hearing. A notice of receipt grants nothing; if an exploration licence is issued under the
  Act and its implementing regulations, that is a State act and a new scope question.
- **ISA 31st session, second part** (Council session part II, Kingston, 13–24 July 2026) — the part's
  documents, none held as text and none worth holding, recorded here by symbol and date:
  - `ISBA/31/C/38` (24 July 2026) — "Decision of the Council of the International Seabed Authority on
    the approach to the continuation of the elaboration of rules, regulations and procedures relating
    to exploitation and resolution of the remaining key outstanding issues", taken under agenda item
    11, "Consideration, with a view to adoption, of the draft regulations on exploitation of mineral
    resources in the Area"; its draft `ISBA/31/C/L.13`, against the revised indicative list
    `ISBA/31/C/CRP.7` (4 July 2026, English only), whose explanatory note records that elaboration
    continues under the thematic approach set by the Council at its thirtieth session
    (`ISBA/30/C/18`). **Its outcome is already carried by this corpus** — adoption did not follow
    (`docs/annual-review-2026.md`, `docs/design/judgement-calls.md`, and the draft-code record's
    provenance note) — so this row adds the citation, not the fact.
  - `ISBA/31/C/19/Rev.1/Add.1` (advance unedited version, **11 September 2026**, English only) —
    "Statement of the President on the work of the Council of the International Seabed Authority
    during the second part of the thirty-first session", opening at the 355th meeting of the Council,
    on 13 July 2026. The one document of the part cited nowhere in this corpus; the *first* part's
    statement (`ISBA/31/C/19/Rev.1`, para. 43) is cited as authority for a procedural fact, and by
    JC-018 the statements are citable but not held as records — a convention question, not this one.
  - Administrative, no operative text for the corpus: `ISBA/31/C/30` (relinquishment report under the
    Republic of Korea's cobalt-rich ferromanganese crusts contract), `ISBA/31/C/32` (election to fill
    a vacancy on the Legal and Technical Commission under UNCLOS article 163(7)), `ISBA/31/C/33`,
    `ISBA/31/C/34` ("Decision of the Council … relating to the reports of the Chair of the Legal and
    Technical Commission", 24 July 2026, agenda item 13), `ISBA/31/C/37`.
  - Session pages: `https://www.isa.org.jm/sessions/31st-session-2026/`, with per-symbol pages at
    `https://isa.org.jm/documents/<symbol-slug>/` — the reliable route, since the session page's row
    order associates a document's per-language links with the *following* row.
