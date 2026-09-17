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
