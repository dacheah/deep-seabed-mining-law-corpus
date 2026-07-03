# 02 — Versioning scheme (Deep Seabed Mining Law Corpus)

## Identifier shape

`corpus_id` is `<authority>/<type>/<slug>-<year>`, lower-case, stable forever:

```
international level (the ISA / UNCLOS regime)
  un/convention/unclos-partxi-1982        UNCLOS Part XI (the Area)
  un/agreement/unclos-partxi-impl-1994    1994 Implementation Agreement
  itlos/advisory-opinion/sdc-area-2011    2011 Seabed Disputes Chamber Advisory Opinion (Case 17)
  isa/regulation/nodules-<year>           ISA exploration regs — polymetallic nodules
  isa/regulation/sulphides-<year>         ISA exploration regs — polymetallic sulphides
  isa/regulation/crusts-<year>            ISA exploration regs — cobalt-rich crusts
  isa/draft/exploitation-code-<year>      draft Exploitation Regulations ("the Mining Code")

national level
  <ISO-3166-a3>/<type>/<slug>-<year>
  usa/statute/dshmra-1980                 Deep Seabed Hard Mineral Resources Act
  usa/regulation/cfr15-970-<year>         NOAA licensing (exploration), 15 CFR 970
  usa/regulation/cfr15-971-<year>         NOAA permits (commercial recovery), 15 CFR 971
```

The US identifiers deliberately sit under `usa/…`, never under the ISA prefixes, so the non-UNCLOS
parallel track is unmistakable at the identifier level (JC-001).

## On disk — one folder per version

```
authoritative/<corpus_id>/<version_id>/
    original.<ext>   byte-exact captured artifact (integrity anchor)
    text.txt         the authoritative text (UTF-8, LF)
    metadata.yaml    full provenance (doc 01)
```

`version_id` is the date that textual state took effect:
- a Convention/Agreement → its date of adoption (or entry into force where that is the operative
  consolidated state; recorded in `provenance_note`).
- an ISA regulation → the date the Assembly/Council adopted that text (the `ISBA/...` decision date).
- a draft Mining Code → the date of that draft revision, and it is marked as a **draft, not in force**
  (JC-002). A draft is only treated as a citable version once the human decides it is stable enough.
- US CFR → the revision date of that CFR edition.

## Append-only. Never overwrite.

- Same text, re-retrieved → append to `capture_history`.
- Text changed (amendment/new consolidation/next draft) → a **new** `version_id` folder; set
  `supersedes`/`superseded_by`.
- Ingestion/extraction error → correct in place with a dated `corrections[]` entry and re-hash; the
  prior state stays in Git history. (Derived artifacts, by contrast, are simply regenerated.)
- Never force-push or rewrite history. Git is the immutable, dated substrate.
