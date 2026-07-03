# 04 — Licensing policy (TEMPLATE)

Two different things: **your contributions** vs **the source texts**.

- **Your contributions** — the derived layer, schema, scripts, docs — pick one licence (CC BY 4.0
  is a common choice for open data/infrastructure) and state it once.
- **Source texts are NOT relicensed.** Each keeps its own terms, recorded per document in
  `license`/`rights_note`. Common patterns:
  - Government/official legal texts: often public-domain or freely reproducible with attribution —
    but this varies by jurisdiction; some assert Crown/state copyright with reuse terms.
  - Third-party/commercial publishers, and many translations: may assert copyright — **link + cite +
    your own summary**, do not store full text without a clear basis.
- **Storing byte-exact originals** in-repo is appropriate where terms permit; where they don't,
  default to hash + URL + provenance (no stored full text).

When rights are unclear or high-stakes, treat it as a judgement call, not a default.
[DOMAIN note: list the main source types in your field and each one's rights position.]
