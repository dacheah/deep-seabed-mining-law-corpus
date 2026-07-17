"""
watch_sources.py -- Phase F source monitor (schema-aware).

Two modes per source in monitoring/sources.json:

  * SCHEMA mode — the source carries a `schema` and Crawl4AI is available: extract the listing with the
    committed CSS schema (deterministic, no LLM), canonicalise the records (sorted keys), hash the set,
    and diff against the previous run's snapshot -> a STRUCTURED change report: new instruments,
    disappeared entries, and changed fields. Snapshots live in monitoring/snapshots/.

  * WHOLE-PAGE mode — fallback for sources with no schema, or when Crawl4AI is not installed: reduce the
    page to text, hash it, and flag baseline/changed as before (a deliberately simple, noisy v1).

Automation only WATCHES and queues; the maintainer judges. Nothing is ingested automatically.
Designed to run in GitHub Actions. Offline self-test:  python3 watch_sources.py --selftest
"""
from __future__ import annotations
import datetime
import hashlib
import json
import os
import re
import sys
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SOURCES = os.path.join(REPO, "monitoring", "sources.json")
REPORT = os.path.join(REPO, "monitoring", "last_report.md")
SNAP_DIR = os.path.join(REPO, "monitoring", "snapshots")
UA = "provenance-corpus-monitor/0.2"

# Optional schema-mode via the crawl layer; falls back cleanly if unavailable (e.g. CI without crawl4ai).
sys.path.insert(0, os.path.join(HERE, "crawl"))
try:
    import common as _crawl            # scripts/crawl/common.py
    _HAVE_COMMON = True
except Exception:
    _crawl = None
    _HAVE_COMMON = False


# ---- whole-page mode (stdlib only) ----------------------------------------------------------------
def to_text(raw: str) -> str:
    """Reduce HTML to comparable text: drop scripts/styles/tags, collapse space."""
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def content_hash(raw: str) -> str:
    return "sha256:" + hashlib.sha256(to_text(raw).encode("utf-8")).hexdigest()


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")


def classify(sources: list, hashes: dict) -> list:
    """Pure whole-page diff logic (offline-testable). hashes: name -> new_hash or 'ERROR:..'."""
    events = []
    for s in sources:
        h = hashes.get(s["name"])
        if h is None or str(h).startswith("ERROR"):
            events.append((s["name"], "error", s.get("last_sha256"), h))
        elif s.get("last_sha256") is None:
            events.append((s["name"], "baseline", None, h))
        elif h != s["last_sha256"]:
            events.append((s["name"], "changed", s["last_sha256"], h))
        else:
            events.append((s["name"], "unchanged", s["last_sha256"], h))
    return events


# ---- schema mode ----------------------------------------------------------------------------------
def _rec_key(rec: dict) -> str:
    """Stable identity for an extracted record, for record-level diffing."""
    for k in ("doc_url", "url", "citation", "title"):
        if rec.get(k):
            return str(rec[k]).strip()
    return json.dumps(rec, sort_keys=True, ensure_ascii=False)


def diff_records(prev: list, cur: list) -> dict:
    """Pure structured diff (offline-testable): new / disappeared / changed-fields."""
    pv = {_rec_key(r): r for r in prev}
    cv = {_rec_key(r): r for r in cur}
    new = [cv[k] for k in cv if k not in pv]
    gone = [pv[k] for k in pv if k not in cv]
    changed = []
    for k in cv:
        if k in pv and cv[k] != pv[k]:
            fields = set(pv[k]) | set(cv[k])
            deltas = {f: {"was": pv[k].get(f), "now": cv[k].get(f)}
                      for f in sorted(fields) if pv[k].get(f) != cv[k].get(f)}
            changed.append({"key": k, "changes": deltas})
    return {"new": new, "disappeared": gone, "changed": changed}


def _snap_path(source_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")[:60] or "src"
    return os.path.join(SNAP_DIR, slug + ".json")


def schema_check(source: dict):
    """Extract via committed schema, hash, and diff vs snapshot. Returns (state, hash, report, records)."""
    import asyncio
    schema = _crawl.load_schema(source["schema"])
    records, _html, _status = asyncio.run(_crawl.crawl_extract(source["url"], schema))
    h = _crawl.records_hash(records)
    prev_hash = source.get("last_sha256")
    sp = _snap_path(source["name"])
    prev = json.load(open(sp, encoding="utf-8")).get("records", []) if os.path.isfile(sp) else []
    if prev_hash is None:
        return "baseline", h, None, records
    if h == prev_hash:
        return "unchanged", h, None, records
    return "changed", h, diff_records(prev, records), records


# ---- self-test (offline) --------------------------------------------------------------------------
def selftest() -> int:
    # whole-page normalisation + classify (unchanged contract)
    assert content_hash("<p>hi</p>") == content_hash("<p>  hi  </p>"), "hash normalisation failed"
    src = [{"name": "a", "url": "x", "last_sha256": "sha256:aaa"},
           {"name": "b", "url": "y", "last_sha256": None},
           {"name": "c", "url": "z", "last_sha256": "sha256:ccc"},
           {"name": "d", "url": "w", "last_sha256": "sha256:ddd"}]
    hh = {"a": "sha256:aaa", "b": "sha256:bbb", "c": "sha256:CHANGED", "d": "ERROR:timeout"}
    got = {n: st for n, st, _, _ in classify(src, hh)}
    assert got == {"a": "unchanged", "b": "baseline", "c": "changed", "d": "error"}, got
    # structured record diff
    prev = [{"title": "A", "doc_url": "a", "date": "2019"}, {"title": "B", "doc_url": "b", "date": "2020"}]
    cur = [{"title": "A", "doc_url": "a", "date": "2019"},
           {"title": "B rev.2", "doc_url": "b", "date": "2021"},
           {"title": "C", "doc_url": "c"}]
    d = diff_records(prev, cur)
    assert [r["title"] for r in d["new"]] == ["C"], d
    assert d["disappeared"] == [], d
    assert len(d["changed"]) == 1 and d["changed"][0]["key"] == "b", d
    assert set(d["changed"][0]["changes"]) == {"title", "date"}, d
    print("watch_sources selftest: OK")
    return 0


# ---- report + run ---------------------------------------------------------------------------------
def _fmt_schema(name, state, report):
    lines = []
    if state == "baseline":
        lines.append(f"- **{name}** — 🟦 baseline set (schema)")
    elif state == "unchanged":
        lines.append(f"- **{name}** — ✅ unchanged (schema)")
    elif str(state).startswith("error"):
        lines.append(f"- **{name}** — ⚠️ {state} (schema)")
    else:  # changed
        n, g, c = len(report["new"]), len(report["disappeared"]), len(report["changed"])
        lines.append(f"- **{name}** — 🔶 CHANGED (schema): {n} new, {g} gone, {c} amended")
        for r in report["new"]:
            lines.append(f"    - ➕ new: {r.get('title') or r.get('citation') or _rec_key(r)}")
        for r in report["disappeared"]:
            lines.append(f"    - ➖ gone: {r.get('title') or r.get('citation') or _rec_key(r)}")
        for ch in report["changed"]:
            lines.append(f"    - ✏️ amended [{ch['key']}]: {', '.join(ch['changes'].keys())}")
    return lines


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    data = json.load(open(SOURCES, encoding="utf-8"))
    sources = data["sources"]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(SNAP_DIR, exist_ok=True)
    have_schema_mode = _HAVE_COMMON and _crawl.crawl4ai_status()[0]

    lines = [f"# Source monitor report — {now}",
             f"_schema mode: {'on' if have_schema_mode else 'off (crawl4ai unavailable — whole-page fallback)'}_", ""]
    page_hashes = {}
    any_changed = False

    for s in sources:
        if s.get("schema") and have_schema_mode:
            try:
                state, h, report, records = schema_check(s)
                with open(_snap_path(s["name"]), "w", encoding="utf-8") as f:
                    json.dump({"generated": now, "records": records}, f, indent=2, ensure_ascii=False)
                lines += _fmt_schema(s["name"], state, report)
                if state == "changed":
                    any_changed = True
                if not str(state).startswith("error"):
                    s["last_sha256"] = h
            except Exception as e:
                lines.append(f"- **{s['name']}** — ⚠️ error:{type(e).__name__}: {e} (schema)")
        else:
            try:
                page_hashes[s["name"]] = content_hash(fetch(s["url"]))
            except Exception as e:
                page_hashes[s["name"]] = f"ERROR:{type(e).__name__}"
        s["last_checked"] = now

    # whole-page sources: classify + advance baseline + report
    page_sources = [s for s in sources if not (s.get("schema") and have_schema_mode)]
    for name, state, old, new in classify(page_sources, page_hashes):
        mark = {"changed": "🔶 CHANGED (page)", "baseline": "🟦 baseline set (page)",
                "error": "⚠️ fetch error (page)", "unchanged": "✅ unchanged (page)"}[state]
        lines.append(f"- **{name}** — {mark}")
        if state == "changed":
            lines += [f"    - was `{old}`", f"    - now `{new}`"]
            any_changed = True
    for s in page_sources:
        h = page_hashes.get(s["name"])
        if h is not None and not str(h).startswith("ERROR"):
            s["last_sha256"] = h

    lines += ["", "_Automation only watches and queues. A flag may be a genuinely new/amended instrument "
              "OR a cosmetic page update — the maintainer triages. Schema-mode reports instrument-level "
              "changes; whole-page mode flags any text change. Nothing is ingested automatically._"]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"changes={'true' if any_changed else 'false'}\n")
    print(f"Checked {len(sources)} sources "
          f"({sum(1 for s in sources if s.get('schema'))} schema, "
          f"{sum(1 for s in sources if not s.get('schema'))} page); changes={any_changed}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
