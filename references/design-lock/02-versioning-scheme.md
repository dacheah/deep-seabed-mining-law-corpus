# 02 — Versioning scheme (TEMPLATE)

Identifiers (adapt the shape to [DOMAIN]):

```
<authority>/<type>/<slug>-<year>      e.g. reg/eu/mifid2-2014
<jurisdiction ISO-3166-a3>/<slug>-<year>  for national instruments
```

On disk, one folder per version:

```
authoritative/<corpus_id>/<version_id>/
    original.<ext>   byte-exact captured artifact (integrity anchor)
    text.txt         the authoritative text (UTF-8, LF)
    metadata.yaml    full provenance (doc 01)
```

**Append-only. Never overwrite.**
- Same text, re-retrieved → append to `capture_history`.
- The text changed (amendment/consolidation) → a **new** `version_id` folder; set `supersedes`/`superseded_by`.
- Ingestion/extraction error → correct in place with a dated `corrections[]` entry and re-hash; the prior
  state stays in Git history. (Derived artifacts, by contrast, may simply be regenerated.)
- Never force-push or rewrite history. Git is the immutable, dated substrate.
