#!/usr/bin/env python3
"""check_revisions.py — is a HELD revision still the latest PUBLISHED revision?

WHY THIS EXISTS (issue #14, found by the 2026 annual review). Every other check in this corpus watches
a page, and a page can stay byte-stable for a year while the revision that supersedes a held text is
published somewhere the monitor is not looking. That is exactly what happened in 2026: the held Mining
Code draft (ISBA/31/C/CRP.2, 23 December 2025) was superseded by the Further Revised Consolidated Text
ISBA/31/C/CRP.1/Rev.3 (19 June 2026), negotiated across the 31st session's two parts — and nothing in
the corpus said so. The page monitor was not broken; the pages it watches really did not change. It
took a human running the annual review to notice. The reproducibility gate cannot catch it either: it
re-derives the superseded text byte-for-byte, forever, with a green tick. The failure mode is therefore
not "late" — it is a WRONG CLAIM that survives every other automated check this corpus has.

WHAT IT DOES. Reads monitoring/held_revisions.json — a declared list of records whose instrument is
expected to be revised, each with a pattern that extracts the revision ordinal and the pages where a
newer revision would first appear. Fetch each page once, extract every match, compare the MAXIMUM with
the ordinal of the held identifier. Higher -> OUTDATED. Equal -> CURRENT.

WHY PER-PAGE ANCHORS. An entry lists pages, not one page: a signal may appear on a session page while
a summary page stays stale for years (that is the 2026 finding in miniature). Each page therefore
declares its own `expect_contains`, so a page that has changed shape is detected per page. A page that
carries no match for the series contributes no evidence but is NOT an error — it is listed as NO MATCH.
The check is BROKEN only when NO page in the entry yields a reading at all: a check that goes quiet
when its evidence disappears is worse than no check, because silence reads as good news.

ADVISORY ONLY. It changes no record and ingests nothing: it reports, and the workflow opens an issue
for a human. Nothing in this corpus is ever ingested automatically.

Version history:
  1.0  2026-09-16  first cut, written for issue #14. Offline --selftest covers every verdict path,
                   including the ones that must never be a pass (series absent everywhere; anchor
                   missing; a held identifier the pattern cannot read). --manifest/--report exist so
                   the "can it actually fire?" test runs against the live pages without touching the
                   committed manifest or report.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# Politeness and page-reading are shared with the page monitor on purpose: one user agent, one timeout,
# one definition of "the text of this page". Two monitors disagreeing about what a page says would be a
# new class of defect, not a feature.
from watch_sources import fetch_raw, to_text  # noqa: E402

MANIFEST = os.path.join(REPO, "monitoring", "held_revisions.json")
REPORT = os.path.join(REPO, "monitoring", "revision_check.md")

CURRENT, OUTDATED, UNKNOWN = "CURRENT", "OUTDATED", "CANNOT DETERMINE"
READ, NOMATCH, UNREADABLE, UNFETCHED = "read", "no match", "unreadable", "not fetched"


def ordinal(identifier: str, pattern: str) -> int | None:
    """The revision ordinal inside an identifier, using the manifest's own pattern.

    One extractor for both sides of the comparison — the held identifier and the page text go through
    the same regex — so a pattern that cannot read the held value fails loudly instead of quietly
    comparing two different things.
    """
    m = re.search(pattern, identifier or "")
    return int(m.group(1)) if m else None


def read_page(page_text: str, pattern: str, expect_contains: str) -> tuple[str, int | None, str]:
    """Classify ONE page. Pure — no network, no state. This is what --selftest exercises."""
    if expect_contains and expect_contains not in page_text:
        return (UNREADABLE, None,
                f"page does not contain {expect_contains!r} — wrong page, or the page changed shape")
    found = [int(m) for m in re.findall(pattern, page_text)]
    if not found:
        return (NOMATCH, None, f"page does not mention the series ({pattern!r} matches nothing)")
    return (READ, max(found), f"highest revision on this page: Rev.{max(found)}")


def verdict_for(pages: list[tuple[dict, str, int | None, str]], held: str, pattern: str
                ) -> tuple[str, str]:
    """Combine per-page readings for one held record. The newest thing any page shows wins."""
    held_ord = ordinal(held, pattern)
    if held_ord is None:
        return (UNKNOWN, f"the HELD identifier {held!r} does not match {pattern!r} — the manifest is "
                         f"wrong, not the pages")
    readings = [(p, top) for (p, state, top, _) in pages if state == READ and top is not None]
    if not readings:
        return (UNKNOWN, "no watched page yielded a reading — the check has lost its evidence")
    top = max(top for _, top in readings)
    where = ", ".join(p["url"] for p, t in readings if t == top)
    if top > held_ord:
        return (OUTDATED, f"a newer revision is published: Rev.{top} vs held Rev.{held_ord} ({where})")
    return (CURRENT, f"held Rev.{held_ord} is the highest revision any watched page shows ({where})")


def check_one(entry: dict) -> dict:
    """Fetch every page for one entry and combine. Returns a report row."""
    held, pattern = entry["held"], entry["pattern"]
    pages, notes = [], []
    for spec in entry.get("watch_urls", []):
        url = spec if isinstance(spec, str) else spec["url"]
        anchor = "" if isinstance(spec, str) else spec.get("expect_contains", "")
        try:
            raw, _ctype = fetch_raw(url)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
            pages.append(({"url": url}, UNFETCHED, None, f"NOT CHECKED ({type(e).__name__}: {e})"))
            notes.append(f"{url}: {UNFETCHED}")
            continue
        state, top, why = read_page(to_text(raw.decode("utf-8", "replace")), pattern, anchor)
        pages.append(({"url": url}, state, top, why))
        notes.append(f"{url}: {state} — {why}")
    verdict, why = verdict_for(pages, held, pattern)
    return {"record": entry["record"], "held": held, "verdict": verdict, "why": why,
            "revisions_seen": sorted({top for (_, state, top, _) in pages
                                      if state == READ and top is not None}),
            "pages": [{"url": p["url"], "state": state, "why": why}
                      for (p, state, _top, why) in pages],
            "notes": notes}


def run_checks(manifest_path: str) -> tuple[list[dict], list[str]]:
    data = json.load(open(manifest_path, encoding="utf-8"))
    checks = data.get("checks") or []
    problems = []
    if not checks:
        problems.append("manifest declares no checks — a check list with nothing in it reads as a pass")
    for e in checks:
        for k in ("record", "held", "pattern", "watch_urls"):
            if not e.get(k):
                problems.append(f"entry {e.get('record')!r} is missing {k!r}")
    return ([check_one(e) for e in checks if e.get("watch_urls")], problems)


def write_report(results: list[dict], problems: list[str], path: str) -> None:
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n_out = sum(1 for r in results if r["verdict"] == OUTDATED)
    n_unk = sum(1 for r in results if r["verdict"] == UNKNOWN)
    n_cur = sum(1 for r in results if r["verdict"] == CURRENT)
    lines = [f"# Held-revision check — {today}", "",
             f"{n_cur} current · {n_out} OUTDATED · {n_unk} cannot determine · "
             f"{len(results)} held record(s) checked", "",
             "Advisory only: nothing was ingested and no record was changed. This check exists because a "
             "page monitor cannot see a held text being superseded — the pages can stay byte-stable "
             "while the newer revision is published elsewhere (JC-009).", "",
             "**A check with no reading is NOT a pass.** Where a page could not be read, or no longer "
             "mentions the series, that is stated per page below; a record reads CANNOT DETERMINE when "
             "no watched page yielded a reading at all.", ""]
    if problems:
        lines += ["## Problems", ""] + [f"- {p}" for p in problems] + [""]
    for r in sorted(results, key=lambda r: ({OUTDATED: 0, UNKNOWN: 1, CURRENT: 2}.get(r["verdict"], 3),
                                            r["record"])):
        mark = {OUTDATED: "🔴", UNKNOWN: "🔶", CURRENT: "✅"}.get(r["verdict"], "?")
        lines += [f"## {mark} {r['verdict']} — `{r['record']}`", "",
                  f"- held: **{r['held']}**",
                  f"- revision ordinals seen on the watched pages: {r['revisions_seen'] or 'none'}",
                  f"- why: {r['why']}", "", "  per page:", ""]
        lines += [f"    - {p['state']:12} {p['url']} — {p['why']}" for p in r["pages"]] + [""]
    lines += ["---", "",
              "Method: `scripts/check_revisions.py` reads `monitoring/held_revisions.json`, fetches each "
              "declared page once, extracts every match of the entry's pattern, and compares the maximum "
              "against the held identifier. A newer revision means the corpus is asserting a superseded "
              "text: the fix is a new dated record, not an edit to the old one."]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {path}")


def emit_outputs(results: list[dict], problems: list[str]) -> None:
    outdated = any(r["verdict"] == OUTDATED for r in results)
    broken = bool(problems) or any(r["verdict"] == UNKNOWN for r in results)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"outdated={'true' if outdated else 'false'}\n")
            f.write(f"broken={'true' if broken else 'false'}\n")
    print(f"[v1.0] {len(results)} held record(s); outdated={'yes' if outdated else 'no'}; "
          f"broken={'YES' if broken else 'no'}")
    for r in results:
        print(f"  {r['verdict']:16} {r['record']}  (held {r['held']}) — {r['why']}")


def selftest() -> int:
    """Offline assertions, no network. The UNKNOWN cases are the ones that matter."""
    pat = r"ISBA/31/C/CRP\.1/Rev\.(\d+)"
    held = "ISBA/31/C/CRP.1/Rev.3"
    page = "Further Revised Consolidated Text (Revision 3) ISBA/31/C/CRP.1/Rev.3 and CRP.7"
    checks: list[tuple[str, bool]] = []

    def case(name, cond):
        checks.append((name, bool(cond)))

    def combined(text, h, anchor="Further Revised Consolidated Text"):
        got = read_page(text, pat, anchor)
        return verdict_for([({"url": "u"}, got[0], got[1], got[2])], h, pat)[0]

    case("held ordinal parses", ordinal(held, pat) == 3)
    case("a page carrying only the held revision is CURRENT", combined(page, held) == CURRENT)
    case("a newer revision on the page is OUTDATED",
         combined(page + " ISBA/31/C/CRP.1/Rev.4", held) == OUTDATED)
    case("the MAXIMUM wins, not the first match",
         combined("ISBA/31/C/CRP.1/Rev.5 then ISBA/31/C/CRP.1/Rev.2", held, "") == OUTDATED)
    case("a readable page that does not mention the series is NO MATCH, never a reading",
         read_page("The Mining Code page, no series here", pat, "")[0] == NOMATCH)
    case("...so a record with only NO MATCH pages is CANNOT DETERMINE, never CURRENT",
         combined("no series here", held, "") == UNKNOWN)
    case("a page missing its anchor is UNREADABLE", read_page(page, pat, "Rev.9")[0] == UNREADABLE)
    case("a held identifier the pattern cannot read is CANNOT DETERMINE (manifest is wrong)",
         combined(page, "ISBA/31/C/CRP.2") == UNKNOWN)
    case("a lower held revision against an unchanged page is OUTDATED (the check CAN fire)",
         combined(page, "ISBA/31/C/CRP.1/Rev.1") == OUTDATED)
    case("sibling papers do not collide (CRP.7 is not a revision of CRP.1)",
         read_page("ISBA/31/C/CRP.7 updated", pat, "")[0] == NOMATCH)
    case("one unreadable page does not mask another page's reading",
         verdict_for([({"url": "a"}, UNREADABLE, None, ""),
                      ({"url": "b"}, READ, 4, "")], held, pat)[0] == OUTDATED)
    case("the committed manifest parses and every entry carries what a check needs",
         all(all(e.get(k) for k in ("record", "held", "pattern", "watch_urls"))
             for e in json.load(open(MANIFEST, encoding="utf-8"))["checks"]))

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {n}")
    print(f"\nselftest: {len(checks) - len(bad)}/{len(checks)} passed")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Is a held revision still the latest published revision?",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="offline assertions; no network")
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--report", default=REPORT)
    ap.add_argument("--no-report", action="store_true", help="check only; write no report")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    if not os.path.isfile(a.manifest):
        print(f"ERROR: no manifest at {a.manifest}. A missing manifest is not a pass.")
        return 2
    results, problems = run_checks(a.manifest)
    if not a.no_report:
        write_report(results, problems, a.report)
    emit_outputs(results, problems)
    return 0


if __name__ == "__main__":
    sys.exit(main())
