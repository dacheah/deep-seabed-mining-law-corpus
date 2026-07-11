# Source-coverage map (Deep Seabed Mining Law Corpus)

Written before ingestion (playbook Step 1). For each official source: what it publishes, formats,
languages, terms, and — the point — where authentic texts are missing or capture is imperfect. Gaps
are flagged, not papered over.

## Tier 1 — International (the ISA / UNCLOS regime)

### UNCLOS Part XI — "The Area" (Articles 133–191)
- **Publisher / role:** UN Division for Ocean Affairs and the Law of the Sea (DOALOS), Office of Legal
  Affairs — the depositary's division. Depositary of the Convention: the UN Secretary-General.
- **Authentic languages:** Arabic, Chinese, English, French, Russian, Spanish (UNCLOS Art 320). We
  store **English** this phase (JC-003).
- **Formats found:**
  - Per-Part HTML pages (`.../unclos/part11-1.htm` … `part11-5.htm`) — **complete**, clean, structured
    by Article. **Chosen capture source for Part XI.** DOALOS labels the web text "*may be used and
    reproduced freely by giving acknowledgment to the Division. This is not an official document.*"
    (recorded verbatim in the record's `rights_note`). Minor legacy glyph artifacts observed:
    "l"-for-"1" in a few cross-references (e.g. Art 134(3), 161(3), 163(8) "article l4", 169(3)) —
    reproduced and then corrected against the official PDF in the verification step.
  - Consolidated official PDF (`unclos_e.pdf`) — the fuller official rendering, **but** automated
    capture truncates at ~132 KB (reaches only Art 77), so it is usable as a **verification
    cross-reference for early Parts only**, not as a Part XI source. A human-downloaded byte-exact
    `unclos_e.pdf` is a recommended future provenance upgrade.
- **Coverage gap flagged:** the five other authentic languages (not stored this phase).

### 1994 Agreement relating to the Implementation of Part XI
- **Publisher:** DOALOS (`.../agreement_part_xi/agreement_part_xi.htm`). Adopted 28 Jul 1994 (UNGA
  res. 48/263); in force 28 Jul 1996. Amends/prevails over Part XI on conflict (Agreement Art 2).
- **Authentic languages:** six UN languages; **English** stored.
- **Format:** single HTML page — **complete** (Preamble, Arts 1–10, Annex Sections 1–9), 51 KB,
  captured in full. Same DOALOS "not an official document" disclaimer → `rights_note`.

### 2011 Seabed Disputes Chamber Advisory Opinion (ITLOS Case No. 17)
- **Publisher:** International Tribunal for the Law of the Sea (ITLOS),
  `.../cases/case_no_17/17_adv_op_010211_en.pdf`.
- **Official citation:** *Responsibilities and obligations of States with respect to activities in the
  Area, Advisory Opinion, 1 February 2011, ITLOS Reports 2011, p. 10.*
- **Authentic languages:** English and French (ITLOS official languages). The specific authoritative-
  text designation must be read from the opinion's closing (JC-004).
- **Capture problem (flagged):** the official English PDF **exceeds the fetch tool's ~132 KB output
  cap** and truncates around **paragraph 204** (before the final paragraphs and the operative reply).
  Storing that truncated text as a complete authoritative text would be dishonest. **Decision:**
  ingest an `authoritative_missing` placeholder with full provenance, and add the complete byte-exact
  official PDF by **human download** (the skill's escalation ladder). Not papered over.

### ISA instruments (exploration regs, Mining Code drafts, ISBA/... decisions) — *next phase*
- **Publisher:** International Seabed Authority, `isa.org.jm` (+ the ISA document repository). English
  authentic. The three exploration regulations and the draft Exploitation Regulations are the priority
  additions after the foundational core. A useful ISA consolidation ("Consolidation of Part XI of the
  Convention and the Implementation Agreement", 2025 e-book) exists as an `official_consolidation`
  cross-reference.

## Tier 2 — National

### US non-UNCLOS parallel track (DSHMRA; 15 CFR 970/971; OCSLA/BOEM) — *next phase*
- **Publisher:** US Government — the US Code / govinfo.gov (DSHMRA, 30 U.S.C. ch. 26); eCFR/Federal
  Register (15 CFR 970 licensing, 971 permits). English; US Government works (public domain).
- Kept as a clearly-distinct parallel track (JC-001).

## Tier 3 — Adjacent (NOT authoritative-layer law)
- ISA **DeepData** (scientific/environmental) — adjacency only.
- Antarctic Madrid Protocol mining ban; Central Arctic Ocean fisheries agreement — comparative
  references for the concept layer only. All three are in `queue/candidates.md`, decided out.

## Ingestion order (cleanest, most canonical first)
1. **UNCLOS Part XI** (complete HTML) — proves the pipeline on the foundational text.
2. **1994 Agreement** (complete HTML) — the modifier that prevails over Part XI.
3. **2011 Advisory Opinion** — registered now as a flagged `authoritative_missing` record; complete
   text to follow by human download.
Later phases: ISA exploration regulations → draft Mining Code → US DSHMRA track → other sponsoring-state laws.

## General constraints discovered (apply corpus-wide)
- **Fetch output cap (~132 KB):** long official PDFs truncate. Use HTML per-section sources where
  complete; otherwise escalate to a human-downloaded byte-exact PDF before treating a long PDF text as
  a complete authoritative text.
- **Byte-exact originals:** captures here are text extractions via the approved fetch tool, not
  byte-exact PDF downloads. Each record's `provenance_note` says so and flags the byte-exact official
  file as a recommended upgrade — an honest statement of fidelity, per the method.

## Completed via human download (2026-07-03)
The three items below were dropped as byte-exact official PDFs and are now ingested (complete,
verified). Original section retained for the record:

## (Historical) Pending human download (fetch tooling couldn't retrieve cleanly)
These are in scope and located, but the approved web-fetch tool can't capture them faithfully
(eCFR is JavaScript-rendered and its API times out; govinfo per-part HTML 404s; the ISA draft PDF
exceeds the fetch output cap). Per the method, complete them by dropping the byte-exact official PDF
into `capture/` (as was done for the 2011 Advisory Opinion):

| Instrument | Official source to download |
|---|---|
| ISA draft Exploitation Regulations (Mining Code), ISBA/31/C/CRP.2, 23 Dec 2025 | https://isa.org.jm/wp-content/uploads/2025/12/Further-Revised-Consolidated-Text-clean-version.pdf |
| 15 CFR Part 970 (NOAA exploration licences) | https://www.ecfr.gov/current/title-15/subtitle-B/chapter-IX/subchapter-D/part-970 (print → PDF), or the annual govinfo CFR |
| 15 CFR Part 971 (NOAA commercial-recovery permits) | https://www.ecfr.gov/current/title-15/subtitle-B/chapter-IX/subchapter-D/part-971 |

Note: 15 CFR 970/971 were revised by a final rule published 7 July 2025 (Fed. Reg. 2025-12513); capture
the current (post-revision) eCFR text and record that revision in `capture_history`.

## Parked: UNCLOS Part XI in non-English languages (decision 2026-07-11)
The 1982 Convention itself is only available in non-English languages as **degraded OCR scans** of the
UNTS volumes (both the DOALOS `unclos_f.pdf` and the ISA-hosted `French.pdf` are bad OCR — "min6rales",
"lea", "dana", stray glyphs). Ingesting that would put OCR errors into an authoritative text, so per the
maintainer's decision we **hold** UNCLOS Part XI in other languages until a clean digital source is found
(e.g. EUR-Lex, which is clean but exceeds the fetch cap before Part XI). The modern instruments (1994
Agreement, ISA regulations, the Advisory Opinion) are clean digital in every language and ARE ingested.
Recorded coverage gap under JC-003 / JC-006; not a fidelity failure.

## Multilingual coverage & holds (updated 2026-07-11)

The three ISA exploration regulations are now stored in **five of the six** UN authentic languages —
English (base), French, Spanish, **Russian**, and **Chinese** — each as an equally-authentic text under
JC-006 (language-suffixed `corpus_id`, same `version_id`, cross-linked via `related_documents`). All are
byte-exact reproducible from the official ISA per-language PDF by `scripts/extract.py`.

Official per-language PDFs (ISA Mining Code → Exploration Regulations page):
- Russian: `isba-19c-17_1_1-3.pdf` (nodules), `isba-16a-12rev1_1_1.pdf` (sulphides), `isba-18a-11_3-1.pdf` (crusts)
- Chinese: `isba-19c-17_1-1.pdf` (nodules), `isba-16a-12rev1_1.pdf` (sulphides), `isba-18a-11_1.pdf` (crusts)

### Held (not ingested) — honest fidelity reasons
- **Arabic ISA regulations.** The official Arabic PDFs extract as **Unicode presentation-form glyphs
  (U+FB50–FEFF) in visual (RTL-rendered) order** — measured ~65k presentation-form vs ~11k base-Arabic
  code points on the nodules text, i.e. ~85% non-canonical. Storing that would put reversed, non-canonical
  text into an authoritative record. It is **held** pending either a logical-order Arabic source or a
  verified NFKC-normalise + bidi-reorder pass (deferred: too error-prone to apply silently to legal text).
- **1994 Implementation Agreement in Arabic / Chinese / Russian.** The freely-available UN document-system
  PDFs for A/RES/48/263 in these three languages are legacy-font-garbled (AR, RU) or image-only (ZH). Held
  pending clean digital sources. (The Agreement is already stored in English, French, and Spanish.)
- **UNCLOS Part XI in non-English languages** — held (degraded OCR), see the section above.
