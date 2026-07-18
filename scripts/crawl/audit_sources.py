#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_sources.py — verify every monitored source URL still points where we think it does.

Monitoring sophistication is worthless if a source URL is wrong. Two real defects found by hand on
2026-07-18 prompted this tool:

  * "ITLOS — List of cases" pointed at an overview page carrying prose and a case count, not the
    case register. Two ITLOS matters against the ISA had accumulated unseen.
  * "ISA — Council documents" pointed at /sessions/, which SILENTLY REDIRECTS to an agenda-item page
    from a previous session. It was hashing an unrelated page and would flag a meaningless "change"
    whenever the site repointed the redirect.

Neither is detectable by a content hash: both URLs returned HTTP 200 and stable content.

What this tool DOES catch, deterministically: HTTP errors, and silent redirects (a URL whose
destination is not where it was pointed). That is what found the ISA defect.

What it does NOT catch, and cannot: a URL that resolves correctly to a real, stable, related page
which is simply the WRONG page for the purpose. The ITLOS overview page is titled "Cases" and the
register "List of Cases"; no token heuristic separates those without inventing false alarms. That
defect was found by reading the page. Treat a clean audit as "no broken plumbing", never as
"every source is watching the right thing" — the latter needs human eyes, once, per source.

This tool is ADVISORY ONLY. It never edits sources.json. It reports; a human judges and fixes.

    python3 scripts/crawl/audit_sources.py            # report to stdout + monitoring/source_audit.md
    python3 scripts/crawl/audit_sources.py --selftest # offline checks of the pure logic
"""
from __future__ import annotations
import json
import os
import re
import sys
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

REPORT = os.path.join(common.REPO, "monitoring", "source_audit.md")

# Words that carry no signal when matching a source's name against a page title.
STOP = {"the", "and", "for", "with", "documents", "document", "official", "list", "page", "new",
        "session", "sessions", "isa", "authority", "international", "seabed"}


# ---- pure logic (offline-testable) ----------------------------------------------------------------
def norm_url(u: str) -> str:
    """Compare URLs ignoring scheme, www, trailing slash and case — differences that never matter."""
    u = (u or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.rstrip("/")


def redirected(requested: str, final: str) -> bool:
    return norm_url(requested) != norm_url(final)


def page_title(html: str) -> str:
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html or "")
    if not m:
        return ""
    t = re.sub(r"\s+", " ", m.group(1)).strip()
    return re.sub(r"\s*[|\-–—]\s*[^|\-–—]*$", "", t).strip() or t


def tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if len(w) > 3 and w not in STOP}


def name_matches_title(name: str, title: str) -> bool:
    """Heuristic: does the page look like what the source claims to be?

    Deliberately weak — one shared meaningful word passes. It is meant to catch a source called
    'List of cases' landing on a page titled 'Item 16', not to police wording.
    """
    nt, tt = tokens(name), tokens(title)
    if not nt or not tt:
        return True          # nothing to judge on; do not manufacture a warning
    return bool(nt & tt)


def verdict(req_url: str, final_url: str, status, name: str, title: str) -> tuple[str, str]:
    """Return (level, message). Levels: ok | review | broken."""
    if status is None:
        return "broken", "could not be fetched"
    if int(status) >= 400:
        return "broken", f"HTTP {status}"
    notes = []
    if redirected(req_url, final_url):
        notes.append(f"REDIRECTS to {final_url}")
    if not name_matches_title(name, title):
        notes.append(f"page title '{title}' does not resemble the source name")
    if notes:
        return "review", "; ".join(notes)
    return "ok", f"'{title}'"


# ---- live check -----------------------------------------------------------------------------------
def fetch(url: str):
    req = Request(url, headers={"User-Agent": common.UA})
    with urlopen(req, timeout=45) as r:
        raw = r.read().decode("utf-8", errors="replace")
        return raw, r.geturl(), int(getattr(r, "status", 200) or 200)


def selftest() -> int:
    assert norm_url("https://WWW.Isa.org.jm/sessions/") == "isa.org.jm/sessions"
    assert not redirected("https://www.isa.org.jm/sessions/", "https://isa.org.jm/sessions")
    assert redirected("https://www.isa.org.jm/sessions/",
                      "https://isa.org.jm/sessions-30th-session-2025-item16")
    assert page_title("<title>Item 16 - International Seabed Authority</title>") == "Item 16"
    assert page_title("<title>List of Cases | ITLOS</title>") == "List of Cases"
    # The ISA defect IS caught — twice over: deterministically by the redirect check, and by the
    # title heuristic ('Council documents' shares nothing with 'Item 16').
    assert not name_matches_title("ISA - Council documents", "Item 16")
    # The ITLOS defect is NOT caught, and this test exists to keep that honest. The overview page
    # is titled 'Cases' and the register 'List of Cases'; both share the word, and no token
    # heuristic can separate them. That defect was findable only by READING the page. Do not
    # "fix" this by tightening the heuristic — it would just manufacture false warnings.
    assert name_matches_title("ITLOS - List of cases (new cases / advisory opinions)", "Cases")
    # correct sources must not be flagged
    assert name_matches_title("ITLOS - List of cases (new cases / advisory opinions)",
                              "List of Cases")
    assert name_matches_title("ISA - Exploitation: Official documents", "Exploitation")
    lvl, _ = verdict("https://x.test/a", "https://x.test/a", 200, "Mining Code", "Mining Code")
    assert lvl == "ok"
    lvl, _ = verdict("https://x.test/a", "https://x.test/b", 200, "Mining Code", "Mining Code")
    assert lvl == "review"
    lvl, _ = verdict("https://x.test/a", "https://x.test/a", 404, "Mining Code", "Mining Code")
    assert lvl == "broken"
    print("audit_sources selftest: OK")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    data = common.load_sources()
    rows, counts = [], {"ok": 0, "review": 0, "broken": 0}
    for s in data["sources"]:
        name, url = s["name"], s["url"]
        try:
            raw, final, status = fetch(url)
            title = page_title(raw)
        except Exception as e:
            raw, final, status, title = "", url, None, f"{type(e).__name__}: {e}"
        level, msg = verdict(url, final, status, name, title)
        counts[level] += 1
        rows.append((level, name, url, msg))
        print(f"[{level.upper():6}] {name}\n           {msg}")

    lines = [f"# Source URL audit — {common.now_iso()}", "",
             f"{counts['ok']} ok · {counts['review']} need review · {counts['broken']} broken", "",
             "Advisory only — nothing was changed. A REDIRECT is not automatically wrong (sites move "
             "pages legitimately), but it must be confirmed to still be the intended target. A title "
             "mismatch means the page may not be what the source claims to watch.", ""]
    for level in ("broken", "review", "ok"):
        picked = [r for r in rows if r[0] == level]
        if not picked:
            continue
        mark = {"broken": "⛔ BROKEN", "review": "🔶 REVIEW", "ok": "✅ OK"}[level]
        lines.append(f"## {mark} ({len(picked)})")
        lines.append("")
        for _, name, url, msg in picked:
            lines.append(f"- **{name}**")
            lines.append(f"    - `{url}`")
            lines.append(f"    - {msg}")
        lines.append("")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n{counts['ok']} ok · {counts['review']} need review · {counts['broken']} broken")
    print(f"wrote {REPORT}")
    print("Advisory only — sources.json was NOT modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
