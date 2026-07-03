---
name: Annual review
about: Yearly review checklist, aligned to the ISA session cycle
labels: annual-review
---

# Annual review checklist (Phase 2 cadence)

- [ ] Re-run `python3 scripts/validate_corpus.py` — green.
- [ ] Review `monitoring/last_report.md` and the year's source-watch issues.
- [ ] UNCLOS Part XI / 1994 Agreement — any correction or new authentic-language text to add?
- [ ] ISA — new/amended exploration regulations, LTC recommendations, ISBA/... decisions?
- [ ] **Mining Code** — has a new draft revision been issued, or has the Code been adopted?
      (If adopted, ingest as a new in-force version; see JC-002.)
- [ ] ITLOS / Seabed Disputes Chamber — new advisory opinions or cases? Complete the 2011 AO text if still pending.
- [ ] US track — changes to DSHMRA, 15 CFR 970/971, or Federal Register actions?
- [ ] New sponsoring-state national laws to add (authentic-language rule, JC-005)?
- [ ] Update `docs/design/judgement-calls.md` with any decisions taken.
- [ ] Rebuild derived + site; commit.

Cadence note: during **Phase 1** (through Mining Code adoption + US-regime stabilisation) monitor
closer-than-annual; revert to **Phase 2** (annual) once the regime settles (docs/design & README).
