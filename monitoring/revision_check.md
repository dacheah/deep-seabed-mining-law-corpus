# Held-revision check — 2026-09-16

1 current · 0 OUTDATED · 0 cannot determine · 1 held record(s) checked

Advisory only: nothing was ingested and no record was changed. This check exists because a page monitor cannot see a held text being superseded — the pages can stay byte-stable while the newer revision is published elsewhere (JC-009).

**A check with no reading is NOT a pass.** Where a page could not be read, or no longer mentions the series, that is stated per page below; a record reads CANNOT DETERMINE when no watched page yielded a reading at all.

## ✅ CURRENT — `isa/draft/exploitation-code-2026`

- held: **ISBA/31/C/CRP.1/Rev.3**
- revision ordinals seen on the watched pages: [3]
- why: held Rev.3 is the highest revision any watched page shows (https://www.isa.org.jm/sessions/31st-session-2026/)

  per page:

    - read         https://www.isa.org.jm/sessions/31st-session-2026/ — highest revision on this page: Rev.3
    - no match     https://isa.org.jm/sessions/32nd-session-2027/ — page does not mention the series ('ISBA/31/C/CRP\\.1/Rev\\.(\\d+)' matches nothing)
    - no match     https://isa.org.jm/the-mining-code/draft-exploitation-regulations-2/ — page does not mention the series ('ISBA/31/C/CRP\\.1/Rev\\.(\\d+)' matches nothing)

---

Method: `scripts/check_revisions.py` reads `monitoring/held_revisions.json`, fetches each declared page once, extracts every match of the entry's pattern, and compares the maximum against the held identifier. A newer revision means the corpus is asserting a superseded text: the fix is a new dated record, not an edit to the old one.
