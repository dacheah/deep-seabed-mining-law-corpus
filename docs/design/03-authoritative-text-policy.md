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

## Marked-up revisions and the publisher's machine-readable form (JC-010, issue #15)

- **Never store a marked-up document's text layer.** If a revision's changes are marked visually
  (insertions set apart by formatting, deletions struck through or left in place), `pdftotext` merges both
  wordings where they share a position — at Regulation 1 of ISBA/31/C/CRP.1/Rev.3 it returns the previous
  and the new paragraph numbers as single tokens (`4.`, `[45.`, `56.`, `67.`, `[78.`, `89.`) — and so
  asserts deleted wording as text and mints numbers the document does not use. That is a wrong claim, not
  a rough one, and the reproduce gate cannot catch it: re-derivation reproduces the corruption byte-for-byte.
- **Derive from the machine-readable form when the publisher issues one.** Where the same revision is
  published as a Word document whose changes are machine-readable (`w:ins` / `w:del`), the text is the
  committed extractor's resolution of that file — insertions kept, deletions dropped, and **nothing
  substituted for a deletion**. Substituting a space is the tempting wrong rule: it fixes the case where
  the mark-up carried a space away (`defined]` + `for`) and splits words everywhere else, because most
  deletions sit *inside* a word (`(a)` + deleted `t` + `he principle`).
- **Hold both files in the record.** `original_format` / `original_sha256` name the artefact a reader
  opens and the page-citation anchor; the machine-readable file is held beside it as `original.docx`,
  recorded in `capture_history` with its own hash, and is what the extractor reads.
- **Exclude editorial commentary by structure, never by guessing at prose.** In ISA conference-room
  papers the secretariat's commentary sits in single-cell tables (all 160 of Rev.3's boxes); those are
  excluded on that structural test and the count is recorded in `provenance_note`, so nothing disappears
  silently. A document that offers no structural separation keeps its commentary in the text, and the
  text says so.
- **Such records are attested like any other**, in CI, naming the toolchain that actually ran (`CPython
  x.y` for a Word-form resolver, `poppler x.y` for PDF extraction) — a per-record attestation is only
  meaningful if it names the engine that produced the bytes.

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
