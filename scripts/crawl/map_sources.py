#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""map_sources.py — (skill step 2) build a structured source inventory from official index pages.

For each source in monitoring/sources.json that carries a `schema`, run its DETERMINISTIC CSS schema
over the index page and emit a per-instrument inventory (title, citation, date, document URL, language).
Compare against records already in authoritative/ and flag CANDIDATE GAPS — instruments the official
source lists that the corpus does not yet hold. Output: monitoring/inventory.json.

No LLM. robots.txt respected. Nothing is ingested — this only maps.
"""
from __future__ import annotations
import asyncio
import glob
import json
import os
import re
import sys

import common


def _load_ingested_strings():
    import yaml
    seen = []
    for mp in glob.glob(os.path.join(common.REPO, "authoritative", "**", "metadata.yaml"), recursive=True):
        try:
            m = yaml.safe_load(open(mp, encoding="utf-8"))
        except Exception:
            continue
        for k in ("official_citation", "title", "short_title", "corpus_id"):
            if m.get(k):
                seen.append(str(m[k]))
    return seen


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def _matches_existing(rec, ingested_norm):
    """Light heuristic match of an extracted listing to an already-ingested record (human triages)."""
    hay = " ".join(_norm(rec.get(k, "")) for k in ("title", "citation"))
    # DEDUPLICATE. Counting token OCCURRENCES rather than distinct tokens let a single shared word
    # clear a threshold of two: "Order 2026/6 of 24 June 2026" yields "2026" twice, so every corpus
    # record mentioning 2026 scored 2 hits. That silently hid ITLOS Order 2026/6 from the gap list —
    # a false negative, which is far worse here than an extra candidate to dismiss.
    toks = sorted({t for t in hay.split() if len(t) > 3})
    if not toks:
        return False
    for ex in ingested_norm:
        hits = sum(1 for t in toks if t in ex)
        if hits >= max(2, len(toks) // 2):     # majority of distinctive tokens present
            return True
    return False


def main():
    data = common.load_sources()
    sources = data["sources"]
    ok, ver = common.crawl4ai_status()
    ingested_norm = [_norm(x) for x in _load_ingested_strings()]

    inventory = {"generated": common.now_iso(), "crawl4ai": ver if ok else None, "sources": []}
    for s in sources:
        schema_file = s.get("schema")
        entry = {"name": s["name"], "url": s["url"], "schema": schema_file,
                 "scope": s.get("scope"), "http_status": None,
                 "instruments": [], "candidate_gaps": [], "status": None}
        if not schema_file:
            entry["status"] = "no_schema (whole-page-hash monitoring only)"
        elif not ok:
            entry["status"] = "skipped (crawl4ai not installed)"
        else:
            try:
                schema = common.load_schema(schema_file)
                records, _html, status = asyncio.run(common.crawl_extract(s["url"], schema))
                entry["http_status"] = status
                entry["instruments"] = records
                entry["candidate_gaps"] = [r for r in records if not _matches_existing(r, ingested_norm)]
                entry["status"] = f"ok ({len(records)} listed, {len(entry['candidate_gaps'])} candidate gaps)"
            except Exception as e:
                entry["status"] = f"error: {type(e).__name__}: {e}"
        inventory["sources"].append(entry)

    out = os.path.join(common.REPO, "monitoring", "inventory.json")
    json.dump(inventory, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    gaps = sum(len(x["candidate_gaps"]) for x in inventory["sources"])
    print(f"wrote {out}: {len(sources)} sources, {gaps} candidate gap(s) flagged")
    print("Candidate gaps are NOT auto-ingested — a human triages them into draft manifests (gen_manifests.py).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
