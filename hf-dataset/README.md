---
pretty_name: Deep Seabed Mining Law Corpus
license: other
license_name: mixed-provenance
license_link: https://github.com/dacheah/deep-seabed-mining-law-corpus/blob/main/docs/design/04-licensing-policy.md
language:
- en
- fr
tags:
- legal
- law
- provenance
- legal-nlp
- rag
task_categories:
- text-retrieval
- text-classification
size_categories:
- n<1K
annotations_creators:
- machine-generated
configs:
- config_name: documents
  data_files: data/documents.jsonl
- config_name: provisions
  data_files: data/provisions.jsonl
---

# Deep Seabed Mining Law Corpus

A neutral, **provenance-first**, machine-readable record of the law governing mineral resources of "the Area" (the seabed beyond national jurisdiction): the international ISA/UNCLOS regime and the US non-UNCLOS parallel track. Every record carries its official source, retrieval date, citation, language, an authoritative-status flag, and a SHA-256 content hash; texts are verified against official sources.

- **Source of truth / build history:** https://github.com/dacheah/deep-seabed-mining-law-corpus
- **Human-browsable site:** https://dacheah.github.io/deep-seabed-mining-law-corpus/
- **11** instruments (11 verified against official sources) · **1165** provisions · **2681** neutral concept tags

## Why this dataset is different

Most legal datasets are scraped text with no sourcing. Here **every row is traceable**: the authoritative text is stored in its authentic language with a content hash and a fidelity flag, and anything generated (concept tags, structure) is kept in a separate, clearly-labelled layer. That makes it low-risk input for retrieval-augmented generation and citation-grounded legal NLP.

## Configs

**`documents`** — one row per instrument version: the full authoritative `text` plus provenance (`source_url`, `official_citation`, `authoritative_status`, `text_fidelity`, `content_hash`, `license`, `rights_note`, `provenance_note`, dates, jurisdiction, language).

**`provisions`** — one row per structural unit (article / section / principle / guideline): the unit `text`, its neutral `concepts` (a model pass, unreviewed), and a link back to the source instrument's text hash and URL. Ideal as pre-chunked, concept-labelled context for RAG.

```python
from datasets import load_dataset
docs = load_dataset("dacheah/deep-seabed-mining-law-corpus", "documents")
prov = load_dataset("dacheah/deep-seabed-mining-law-corpus", "provisions")
```

## Contents

| Instrument | Jurisdiction | Adopted | Fidelity |
|---|---|---|---|
| Draft Exploitation Regulations / Mining Code — Dec 2025 consolidated draft [DRAFT] | international |  | `extracted_verified` |
| ISA Cobalt-rich Crusts Exploration Regulations (2012) | international | 2012-07-27 | `extracted_verified` |
| ISA Polymetallic Nodules Exploration Regulations (2013) | international | 2013-07-22 | `extracted_verified` |
| ISA Polymetallic Sulphides Exploration Regulations (2010) | international | 2010-05-07 | `extracted_verified` |
| 2011 Seabed Disputes Chamber Advisory Opinion (Case No. 17) | international | 2011-02-01 | `extracted_verified` |
| Avis consultatif de la Chambre pour le règlement des différends relatifs aux fonds marins (2011, affaire n° 17) [FR] | international | 2011-02-01 | `extracted_verified` |
| 1994 Part XI Implementation Agreement | international | 1994-07-28 | `extracted_verified` |
| UNCLOS Part XI (The Area) | international | 1982-12-10 | `extracted_verified` |
| 15 CFR 970 — DSM Exploration Licences (NOAA) | USA | 1981-09-15 | `extracted_verified` |
| 15 CFR 971 — DSM Commercial Recovery Permits (NOAA) | USA |  | `extracted_verified` |
| US Deep Seabed Hard Mineral Resources Act (DSHMRA) | USA | 1980-06-28 | `extracted_verified` |

## Licensing

**Mixed, and recorded per record.** The compilation, structure, and concept tags (the derived layer) are **CC BY 4.0**. **Source texts are not relicensed** — each keeps its own terms (e.g. UN-materials terms; public-domain government works), recorded in every row's `license` / `rights_note`. See the [licensing policy](https://github.com/dacheah/deep-seabed-mining-law-corpus/blob/main/docs/design/04-licensing-policy.md).

## Disclaimer

This is a **reference record, not legal advice**. The authoritative text of each instrument is the original in its authentic language; **translations and concept tags are unofficial and derived** (the concept tags are an unreviewed model pass — expect occasional over/under-tagging). Always confirm against the cited official source for anything legally operative.

## Citation

```
Deep Seabed Mining Law Corpus (maintainers). https://github.com/dacheah/deep-seabed-mining-law-corpus
```

_Dataset generated from the repository by `scripts/export_hf_dataset.py` on 2026-07-11 — do not edit by hand._
