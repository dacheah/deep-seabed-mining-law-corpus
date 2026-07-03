# 04 — Licensing policy (Deep Seabed Mining Law Corpus)

Two different things: **our contributions** vs **the source texts**. Source texts are never relicensed;
each keeps its own terms, recorded per document in `license` / `rights_note`.

## Our contributions
The derived layer, schemas, scripts, docs and the generated site are licensed **CC BY 4.0**.

## Source texts, by type (DSM-specific)

- **UN treaty texts (UNCLOS, 1994 Agreement)** — `license: un-materials-terms`. UN documents are
  reproduced under the UN's terms with attribution to the United Nations; we store the byte-exact
  official PDF plus the extracted English text, with full provenance and no assertion of ownership.
- **ISA instruments (regulations, ISBA/... decisions, recommendations)** — `license: isa-materials-terms`.
  Official ISA documents, attributed to the International Seabed Authority; stored with attribution and
  a link to the ISA record. Where ISA asserts specific reuse terms, capture them in `rights_note`.
- **ITLOS materials (2011 Advisory Opinion, ITLOS Reports)** — `license: itlos-materials-terms`.
  Attributed to the International Tribunal for the Law of the Sea; official PDF stored with provenance.
- **US Government works (DSHMRA in the US Code; 15 CFR; Federal Register)** — `license: us-gov-public-domain`.
  Edicts of government and US Government works are in the public domain in the United States; stored in full.
- **National legislation of other sponsoring states** — case by case. Many official gazettes permit
  reproduction with attribution; some assert Crown/state copyright with reuse conditions. Record the
  precise position per document in `rights_note`; where rights are unclear or restrictive, default to
  **hash + URL + provenance (no stored full text)** and treat it as a judgement call.

**No wholesale redistribution** of third-party copyrighted translations or commentary. Unofficial
translations we generate live in the derived layer, labelled, under CC BY 4.0 for our text only.

When rights are unclear or high-stakes, it is a judgement call, not a default.
