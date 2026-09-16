# Source URL audit — 2026-09-16T07:07:17Z

22 ok · 1 need review · 0 broken · 0 manual (declared unfetchable)

Advisory only — nothing was changed. A REDIRECT is not automatically wrong (sites move pages legitimately) but must be confirmed to still be the intended target. A title mismatch means the page may not be what the source claims to watch.

**A clean audit means no broken plumbing — not that every source watches the right page.** A URL resolving cleanly to a real but wrong page passes this tool UNLESS the source declares an `expect_contains` anchor (a stable string the right page must carry). Without an anchor, only a human reading the page catches a wrong-page.

**Anchor coverage: 23/23 sources declare an `expect_contains` anchor.** The remaining 0 are checked for plumbing only (HTTP status, redirects, title) and would NOT be caught resolving to a wrong page. Adding anchors to those is the durable fix for the resolving-but-wrong-page class (see the source-verification task).

## 🔶 REVIEW (1)

- **ISA — Exploitation: Official documents**
    - `https://isa.org.jm/the-mining-code/official-documents/`
    - page title 'The Mining Code' does not resemble the source name

## ✅ OK (22)

- **ISA — The Mining Code (exploitation regulations)**
    - `https://www.isa.org.jm/the-mining-code/`
    - 'The Mining Code' ✓ anchored
- **ISA — Exploration regulations**
    - `https://www.isa.org.jm/the-mining-code/exploration-regulations/`
    - 'The Mining Code: Exploration Regulations' ✓ anchored
- **ISA — 30th session (2025)**
    - `https://isa.org.jm/sessions/30th-session-2025/`
    - '30th session 2025' ✓ anchored
- **UN DOALOS — 1994 Part XI Implementation Agreement**
    - `https://www.un.org/depts/los/convention_agreements/texts/agreement_part_xi/agreement_part_xi.htm`
    - 'Agreement on Part XI UNCLOS' ✓ anchored
- **UN DOALOS — UNCLOS Part XI (The Area), Section 1**
    - `https://www.un.org/depts/los/convention_agreements/texts/unclos/part11-1.htm`
    - 'UNCLOS' ✓ anchored
- **ITLOS — Case No. 34 (Nauru Ocean Resources Inc. v. ISA)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-nauru-ocean-resources-inc-v-international-seabed-authority/`
    - 'Case concerning an inquiry by the International Seabed Authority (Nauru Ocean Resources Inc. v. International Seabed Authority)' ✓ anchored
- **ITLOS — Case No. 35 (Tonga Offshore Mining Ltd. v. ISA)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-tonga-offshore-mining-ltd-v-international-seabed-authority/`
    - 'Case concerning an inquiry by the International Seabed Authority (Tonga Offshore Mining Ltd. v. International Seabed Authority)' ✓ anchored
- **ITLOS — Case No. 34 provisional measures (incidental-proceeding sub-page)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-nauru-ocean-resources-inc-v-international-seabed-authority/case-concerning-an-inquiry-by-the-international-seabed-authority-nauru-ocean-resources-inc-v-international-seabed-authority-provisional-measures/`
    - 'Case concerning an inquiry by the International Seabed Authority (Nauru Ocean Resources Inc. v. International Seabed Authority), Provisional Measures' ✓ anchored
- **ITLOS — Case No. 35 provisional measures (incidental-proceeding sub-page)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/case-concerning-an-inquiry-by-the-international-seabed-authority-tonga-offshore-mining-ltd-v-international-seabed-authority/case-concerning-an-inquiry-by-the-international-seabed-authority-tonga-offshore-mining-ltd-v-international-seabed-authority-provisional-measures/`
    - 'Case concerning an inquiry by the International Seabed Authority (Tonga Offshore Mining Ltd. v. International Seabed Authority), Provisional Measures' ✓ anchored
- **ITLOS — Case No. 17 (2011 Advisory Opinion)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/case-no-17/`
    - 'Responsibilities and obligations of States sponsoring persons and entities with respect to activities in the Area (Request for Advisory Opinion submitted to the Seabed Disputes Chamber)' ✓ anchored
- **US eCFR — 15 CFR Part 970 (NOAA deep seabed mining, exploration licences)**
    - `https://www.ecfr.gov/api/versioner/v1/versions/title-15.json?part=970`
    - '' ✓ anchored
- **US eCFR — 15 CFR Part 971 (NOAA commercial recovery permits)**
    - `https://www.ecfr.gov/api/versioner/v1/versions/title-15.json?part=971`
    - '' ✓ anchored
- **ISA — Draft Exploitation Regulations (Mining Code drafts)**
    - `https://isa.org.jm/the-mining-code/draft-exploitation-regulations-2/`
    - 'The Mining Code: Draft Exploitation Regulations' ✓ anchored
- **ISA — Draft Standards and Guidelines (Mining Code)**
    - `https://isa.org.jm/the-mining-code/standards-and-guidelines/`
    - 'The Mining Code: Standards and Guidelines' ✓ anchored
- **ISA — Mining Code Recommendations and guidance (LTC)**
    - `https://isa.org.jm/mining-code-recommendations/`
    - 'The Mining Code: Recommendations' ✓ anchored
- **ISA — Legal and Technical Commission**
    - `https://isa.org.jm/organs/the-legal-and-technical-commission/`
    - 'The Legal and Technical Commission' ✓ anchored
- **ISA — 31st session (2026)**
    - `https://www.isa.org.jm/sessions/31st-session-2026/`
    - '31st session 2026' ✓ anchored
- **ISA — 32nd session (2027)**
    - `https://isa.org.jm/sessions/32nd-session-2027/`
    - '32nd session 2027' ✓ anchored
- **ISA — The Council**
    - `https://isa.org.jm/organs/the-council/`
    - 'The Council' ✓ anchored
- **ITLOS — List of cases (new cases / advisory opinions)**
    - `https://www.itlos.org/en/main/cases/list-of-cases/`
    - 'List of Cases' ✓ anchored
- **US Federal Register — deep seabed mining (newest docs, JSON)**
    - `https://www.federalregister.gov/api/v1/documents.json?conditions%5Bterm%5D=deep+seabed+mining&order=newest&per_page=10`
    - '' ✓ anchored
- **US NOAA — Deep Seabed Hard Minerals Mining**
    - `https://oceanservice.noaa.gov/deep-seabed-mineral-resources/deep-seabed-mining/`
    - 'Deep Seabed Hard Minerals Mining' ✓ anchored

