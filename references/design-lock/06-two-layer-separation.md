# 06 — Two-layer separation (TEMPLATE)

The wall the whole corpus rests on.

- **`authoritative/`** — primary source texts only, authentic language, full provenance. The legal
  record. **No machine- or human-generated interpretation, ever. Append-only.**
- **`derived/`** — everything generated: structure extraction, concept tags, summaries, translations.
  Unofficial, labelled, traceable to a specific authoritative version by its text hash. May be
  regenerated.

The wall is enforced three ways: by **folder location**, by the **schemas**, and by the
**validator** (which also flags a derived artifact as *stale* when its source text hash changes).
Never let derived content appear under `authoritative/`, and never present derived content as
authoritative. Where a file lives tells you what it is.
