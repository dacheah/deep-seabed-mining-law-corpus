# 03 — Authoritative-text policy (Deep Seabed Mining Law Corpus)

## Principles (inherited)

- **Authentic-language only** in `authoritative/`. Store the text in a language in which the
  instrument was actually enacted/issued. Any translation is derived and unofficial (doc 06).
- **Prefer official sources** — the issuer, official gazette/registry, or treaty depositary. A clean
  copy from a non-official aggregator is `source_is_official: false`.
- **Reproduce faithfully, including defects.** If the official source contains a typo or spacing
  error, reproduce it and flag it (`text_fidelity`, `provenance_note`) — do not silently "fix" it.
  Corrections are dated `corrections[]` entries, made only against the official source.
- **Gaps are flagged, not filled.** If only a translation exists and no authentic text can be
  obtained, ingest an `authoritative_status: authoritative_missing` placeholder (no `text.txt`) and
  attach the translation in the derived layer.
- **Fidelity ladder** — set it honestly and upgrade it only after a real check against the source,
  recording a `verification{}` record.

## DSM authentic-language rules (DSM-specific)

- **UNCLOS and the 1994 Agreement** are authentic in **Arabic, Chinese, English, French, Russian and
  Spanish**, all equally (UNCLOS Art 320; the Agreement's final clauses). We store the **English**
  authentic text this phase. The other five authentic languages are a recorded **coverage gap**, not
  a translation problem — each is equally authoritative and may be added later as its own
  `authentic_text` record. Depositary: the UN Secretary-General; canonical publisher for the consolidated
  text: UN Division for Ocean Affairs and the Law of the Sea (DOALOS).
- **ISA regulations, recommendations and decisions** are issued by the ISA in the six UN languages;
  **English** is authentic and is what we store. Canonical citation is the `ISBA/...` document symbol.
- **ITLOS 2011 Advisory Opinion (Case 17):** ITLOS renders judgments and advisory opinions in its two
  official languages, **English and French**, and states in the decision itself which text is
  authoritative (Rules of the Tribunal, art. 125). Which language is authoritative for Case 17 must be
  read off the opinion at ingestion and recorded — see **JC-004**. We store the authoritative-language
  text; the other official-language version is a recorded gap.
- **US instruments (DSHMRA; 15 CFR 970/971; OCSLA/BOEM):** authentic in **English**; sources are US
  Government works.

Store `language` as the ISO-639 code of the stored `text.txt` (`en` throughout this phase) and list
every authentic language in `authentic_languages`.
