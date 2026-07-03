# 06 — Two-layer separation (Deep Seabed Mining Law Corpus)

The wall the whole corpus rests on.

- **`authoritative/`** — primary source texts only, authentic language, full provenance. The legal
  record. **No machine- or human-generated interpretation, ever. Append-only.**
- **`derived/`** — everything generated: structure extraction, neutral concept tags, summaries,
  machine-draft translations. Unofficial, labelled, and traceable to a specific authoritative version
  by its text hash. May be regenerated at will.

The wall is enforced three ways: by **folder location**, by the **schemas** (the authoritative schema
forbids model/interpretive fields; the derived schema requires a disclaimer and a source hash), and by
the **validator** (which also flags a derived artifact as *stale* when its source text hash changes).

Never let derived content appear under `authoritative/`, and never present derived content as
authoritative. In this domain that wall matters especially for two things: (1) the **draft Mining
Code** — drafts are authoritative *as drafts* (what the text of that revision was) but are marked
not-in-force; any commentary on what they *should* say is derived; and (2) **concept tags** describing
whether a provision is "pro-mining" or "pro-moratorium" would be advocacy — forbidden. Tags describe
only what a provision is *about*. Where a file lives tells you what it is.
