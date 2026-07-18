"""
watch_sources.py -- Phase F source monitor (schema-aware).

Two modes per source in monitoring/sources.json:

  * SCHEMA mode — the source carries a `schema` and Crawl4AI is available: extract the listing with the
    committed CSS schema (deterministic, no LLM), canonicalise the records (sorted keys), hash the set,
    and diff against the previous run's snapshot -> a STRUCTURED change report: new instruments,
    disappeared entries, and changed fields. Snapshots live in monitoring/snapshots/.

  * WHOLE-PAGE mode — fallback for sources with no schema, or when Crawl4AI is not installed: reduce the
    page to text, hash it, and flag baseline/changed as before (a deliberately simple, noisy v1).

Two safeguards on schema mode:

  * BROKEN-SELECTOR GUARD — schema mode's one failure mode that whole-page mode does not have is
    UNDER-reporting: if a site's markup shifts, selectors can stop matching and real documents go
    unseen. A real listing loses documents one or two at a time; broken selectors lose all or most at
    once. So a collapse in record count is reported as `schema_suspect` — NOT as documents removed —
    and the baseline and snapshot are deliberately NOT advanced, so a broken schema can never quietly
    become the new "normal".

  * FALSE-ALARM INSTRUMENTATION — for each schema source we record BOTH the whole-page hash and the
    record-set hash each run, to monitoring/false_alarm_log.jsonl. A run where the page hash moved but
    the record set is identical is, by definition, a false alarm under the old whole-page method.
    Accumulated over months this MEASURES the precision gain instead of asserting it:
        python3 watch_sources.py --tally

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
FALSE_ALARM_LOG = os.path.join(REPO, "monitoring", "false_alarm_log.jsonl")
UA = "provenance-corpus-monitor/0.2"

# Broken-selector guard thresholds (see module docstring).
SCHEMA_MIN_PREV = 5        # below this the previous set is too small to judge a "collapse"
SCHEMA_DROP_RATIO = 0.5    # a fall to under half the previous count reads as broken selectors

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


def schema_suspect(prev_count: int, cur_count: int) -> bool:
    """True when the record count COLLAPSES — reads as broken selectors, not removed documents.

    Pure and offline-testable. On True the caller must report loudly and refuse to advance the
    baseline: silently accepting a collapsed record set is how a broken schema starts reporting
    'unchanged' forever while real documents go unseen.
    """
    if prev_count < SCHEMA_MIN_PREV:
        return False          # too small a previous set to distinguish collapse from ordinary churn
    if cur_count == 0:
        return True
    return cur_count < prev_count * SCHEMA_DROP_RATIO


def log_observation(ts: str, name: str, page_changed: bool, records_changed: bool, state: str) -> dict:
    """Pure: one instrumentation row comparing what whole-page mode WOULD have flagged vs reality."""
    verdict = ("false_alarm" if page_changed and not records_changed
               else "real_change" if records_changed
               else "quiet")
    return {"ts": ts, "source": name, "page_changed": bool(page_changed),
            "records_changed": bool(records_changed), "state": state, "verdict": verdict}


def _snap_path(source_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")[:60] or "src"
    return os.path.join(SNAP_DIR, slug + ".json")


def schema_check(source: dict) -> dict:
    """Extract via committed schema, hash records AND page, diff vs snapshot, apply the guard."""
    import asyncio
    schema = _crawl.load_schema(source["schema"])
    records, html, _status = asyncio.run(_crawl.crawl_extract(source["url"], schema))
    h_rec = _crawl.records_hash(records)
    h_page = content_hash(html) if html else None
    sp = _snap_path(source["name"])
    prev = json.load(open(sp, encoding="utf-8")).get("records", []) if os.path.isfile(sp) else []
    prev_hash = source.get("last_sha256")
    prev_page = source.get("last_page_sha256")
    info = {
        "records": records, "h_rec": h_rec, "h_page": h_page,
        "prev_count": len(prev), "cur_count": len(records),
        "records_changed": bool(prev_hash is not None and h_rec != prev_hash),
        "page_changed": bool(prev_page and h_page and h_page != prev_page),
        "report": None,
    }
    if prev_hash is None or not os.path.isfile(sp):
        # No comparable previous RECORD set — either the first run, or a source just switched from
        # whole-page mode (whose last_sha256 is a PAGE hash, not a records hash). Set a baseline
        # rather than emit a spurious "every document is new" report.
        info["state"] = "baseline"
    elif schema_suspect(len(prev), len(records)):
        info["state"] = "schema_suspect"
        info["report"] = diff_records(prev, records)
    elif not info["records_changed"]:
        info["state"] = "unchanged"
    else:
        info["state"] = "changed"
        info["report"] = diff_records(prev, records)
    return info


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
    # broken-selector guard
    assert schema_suspect(38, 0) is True, "total collapse must be suspect"
    assert schema_suspect(38, 10) is True, "collapse to a quarter must be suspect"
    assert schema_suspect(38, 18) is True, "below half must be suspect"
    assert schema_suspect(38, 19) is False, "exactly half is not below half"
    assert schema_suspect(38, 36) is False, "ordinary churn must not be suspect"
    assert schema_suspect(4, 0) is False, "previous set too small to judge"
    assert schema_suspect(0, 0) is False, "no previous set to judge"
    # false-alarm instrumentation
    assert log_observation("t", "s", True, False, "unchanged")["verdict"] == "false_alarm"
    assert log_observation("t", "s", True, True, "changed")["verdict"] == "real_change"
    assert log_observation("t", "s", False, True, "changed")["verdict"] == "real_change"
    assert log_observation("t", "s", False, False, "unchanged")["verdict"] == "quiet"
    print("watch_sources selftest: OK")
    return 0


# ---- instrumentation tally ------------------------------------------------------------------------
def tally() -> int:
    """Report the MEASURED whole-page false-alarm rate from accumulated observations."""
    if not os.path.isfile(FALSE_ALARM_LOG):
        print("No instrumentation recorded yet.")
        print("Run the monitor at least twice on a schema source, then re-run --tally.")
        return 0
    rows = []
    with open(FALSE_ALARM_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    obs = [r for r in rows if r.get("state") in ("changed", "unchanged", "schema_suspect")]
    if not obs:
        print(f"{len(rows)} row(s) logged, but none yet comparable (all baseline runs).")
        return 0
    page = sum(1 for r in obs if r.get("page_changed"))
    recs = sum(1 for r in obs if r.get("records_changed"))
    false = sum(1 for r in obs if r.get("page_changed") and not r.get("records_changed"))
    missed = sum(1 for r in obs if r.get("records_changed") and not r.get("page_changed"))
    srcs = sorted({r.get("source") for r in obs})
    span = f"{min(r['ts'] for r in obs)} .. {max(r['ts'] for r in obs)}"
    print(f"Schema-source observations: {len(obs)} across {len(srcs)} source(s)")
    print(f"Period: {span}")
    print("")
    print(f"  whole-page hash moved (would have flagged): {page}")
    print(f"  actual instrument-level changes:            {recs}")
    print(f"  FALSE ALARMS (page moved, list identical):  {false}")
    if missed:
        print(f"  page quiet but records changed:             {missed}  (whole-page mode would have MISSED these)")
    if page:
        print("")
        print(f"  => measured whole-page false-alarm rate: {false / page * 100:.0f}% of its flags")
    else:
        print("")
        print("  => no page-level movement observed yet; keep running to accumulate evidence.")
    return 0


# ---- report + run ---------------------------------------------------------------------------------
def _fmt_schema(name, state, info):
    lines = []
    report = (info or {}).get("report")
    if state == "baseline":
        lines.append(f"- **{name}** — 🟦 baseline set (schema): {info['cur_count']} records")
    elif state == "unchanged":
        lines.append(f"- **{name}** — ✅ unchanged (schema): {info['cur_count']} records")
    elif state == "schema_suspect":
        lines.append(f"- **{name}** — ⛔ **SCHEMA SUSPECT**: records fell "
                     f"{info['prev_count']} → {info['cur_count']}. Selectors have probably broken; "
                     f"this is NOT read as documents being removed. "
                     f"**Baseline and snapshot deliberately NOT advanced** — verify the schema against "
                     f"the live page before the next run.")
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
    if "--tally" in sys.argv:
        return tally()
    data = json.load(open(SOURCES, encoding="utf-8"))
    sources = data["sources"]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(SNAP_DIR, exist_ok=True)
    have_schema_mode = _HAVE_COMMON and _crawl.crawl4ai_status()[0]

    lines = [f"# Source monitor report — {now}",
             f"_schema mode: {'on' if have_schema_mode else 'off (crawl4ai unavailable — whole-page fallback)'}_", ""]
    page_hashes = {}
    observations = []
    any_changed = False
    suspects = 0

    for s in sources:
        if s.get("schema") and have_schema_mode:
            try:
                info = schema_check(s)
                state = info["state"]
                observations.append(
                    log_observation(now, s["name"], info["page_changed"], info["records_changed"], state))
                if state == "schema_suspect":
                    # Refuse to advance ANY baseline: keep the last known-good snapshot and hashes.
                    suspects += 1
                    any_changed = True
                else:
                    with open(_snap_path(s["name"]), "w", encoding="utf-8") as f:
                        json.dump({"generated": now, "records": info["records"]}, f, indent=2, ensure_ascii=False)
                    s["last_sha256"] = info["h_rec"]
                    if info["h_page"]:
                        s["last_page_sha256"] = info["h_page"]
                    if state == "changed":
                        any_changed = True
                lines += _fmt_schema(s["name"], state, info)
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

    if suspects:
        lines += ["", f"> ⛔ **{suspects} source(s) flagged SCHEMA SUSPECT.** Their baselines were not "
                  "advanced. Re-check the committed schema against the live page — a markup change is "
                  "far more likely than a bulk withdrawal of official documents."]
    lines += ["", "_Automation only watches and queues. A flag may be a genuinely new/amended instrument "
              "OR a cosmetic page update — the maintainer triages. Schema-mode reports instrument-level "
              "changes; whole-page mode flags any text change. Nothing is ingested automatically._"]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    if observations:
        with open(FALSE_ALARM_LOG, "a", encoding="utf-8") as f:
            for o in observations:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"changes={'true' if any_changed else 'false'}\n")
    print(f"Checked {len(sources)} sources "
          f"({sum(1 for s in sources if s.get('schema'))} schema, "
          f"{sum(1 for s in sources if not s.get('schema'))} page); "
          f"changes={any_changed}"
          + (f"; SCHEMA SUSPECT={suspects}" if suspects else "") + ".")
    if observations:
        print(f"Logged {len(observations)} instrumentation row(s) -> monitoring/false_alarm_log.jsonl "
              f"(measure with --tally).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
