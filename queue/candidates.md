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

## Recorded but not ingested — official URLs

Kept so the trail to the full case record exists without the pleadings entering the authoritative
layer (JC-007). If scope is ever extended to case files, start here.

- ITLOS Case 34, Application by Nauru Ocean Resources Inc., 30 May 2026 —
  `https://www.itlos.org/fileadmin/itlos/documents/cases/34/2026.05.30_Nauru_Ocean_Resources_Inc._-_Application_92502112.1_.pdf`
- ITLOS Case 35, Application by Tonga Offshore Mining Ltd., 30 May 2026 —
  `https://www.itlos.org/fileadmin/itlos/documents/cases/35/2026.05.30_Tonga_Offshore_Mining_Ltd._-_Application_92502116.1_.pdf`

Both case pages also carry ITLOS **press releases**, which are communications *about* proceedings and
never enter `authoritative/`. The extraction schema excludes them structurally: case documents sit
under `/documents/cases/`, press releases under `/documents/press_releases_english/`.
