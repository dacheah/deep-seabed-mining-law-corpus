---
pretty_name: Deep Seabed Mining Law Corpus
license: other
license_name: mixed-provenance
license_link: https://github.com/OWNER/deep-seabed-mining-law-corpus/blob/main/docs/design/04-licensing-policy.md
language:
- en
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

- **Source of truth / build history:** https://github.com/OWNER/deep-seabed-mining-law-corpus
- **Human-browsable site:** https://OWNER.github.io/deep-seabed-mining-law-corpus/
- **2** instruments (2 verified against official sources) · **71** provisions · **251** neutral concept tags

## Why this dataset is different

Most legal datasets are scraped text with no sourcing. Here **every row is traceable**: the authoritative text is stored in its authentic language with a content hash and a fidelity flag, and anything generated (concept tags, structure) is kept in a separate, clearly-labelled layer. That makes it low-risk input for retrieval-augmented generation and citation-grounded legal NLP.

## Configs

**`documents`** — one row per instrument version: the full authoritative `text` plus provenance (`source_url`, `official_citation`, `authoritative_status`, `text_fidelity`, `content_hash`, `license`, `rights_note`, `provenance_note`, dates, jurisdiction, language).

**`provisions`** — one row per structural unit (article / section / principle / guideline): the unit `text`, its neutral `concepts` (a model pass, unreviewed), and a link back to the source instrument's text hash and URL. Ideal as pre-chunked, concept-labelled context for RAG.

```python
from datasets import load_dataset
docs = load_dataset("OWNER/deep-seabed-mining-law-corpus", "documents")
prov = load_dataset("OWNER/deep-seabed-mining-law-corpus", "provisions")
```

## Contents

| Instrument | Jurisdiction | Adopted | Fidelity |
|---|---|---|---|
| 1994 Part XI Implementation Agreement | international | 1994-07-28 | `extracted_verified` |
| UNCLOS Part XI (The Area) | international | 1982-12-10 | `extracted_verified` |

## Licensing

**Mixed, and recorded per record.** The compilation, structure, and concept tags (the derived layer) are **CC BY 4.0**. **Source texts are not relicensed** — each keeps its own terms (e.g. UN-materials terms; public-domain government works), recorded in every row's `license` / `rights_note`. See the [licensing policy](https://github.com/OWNER/deep-seabed-mining-law-corpus/blob/main/docs/design/04-licensing-policy.md).

## Disclaimer

This is a **reference record, not legal advice**. The authoritative text of each instrument is the original in its authentic language; **translations and concept tags are unofficial and derived** (the concept tags are an unreviewed model pass — expect occasional over/under-tagging). Always confirm against the cited official source for anything legally operative.

## Citation

```
Deep Seabed Mining Law Corpus (maintainers). https://github.com/OWNER/deep-seabed-mining-law-corpus
```

_Dataset generated from the repository by `scripts/export_hf_dataset.py` on 2026-07-03 — do not edit by hand._
