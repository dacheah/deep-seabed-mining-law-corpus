#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_manifests.py — (skill step 4) turn the source inventory into DRAFT ingest manifests.

Reads monitoring/inventory.json and writes one draft ingest.py manifest per candidate-gap instrument
under queue/manifests/, each marked `status: draft_requires_human_review`.

NEVER runs ingest.py. A human verifies the citation and metadata, captures the official file
(capture.py), fills the capture paths, and only then runs ingest.py.
"""
from __future__ import annotations
import json
import os
import re
import sys

import common

MANIFEST_DIR = os.path.join(common.REPO, "queue", "manifests")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")[:60] or "instrument"


def draft_manifest(source, rec):
    """A draft matching ingest.py's manifest shape, with human-review placeholders for the judgement fields."""
    return {
        "status": "draft_requires_human_review",
        "_generated_by": "scripts/crawl/gen_manifests.py",
        "_source": source["name"],
        "_source_url": source["url"],
        "_listing": rec,                         # raw extracted fields, for the human to verify against the source
        # --- fields a human confirms before ingest (see docs/design/01, 02, 03) ---
        "corpus_id": "",                         # TODO assign per the identifier rules (doc 02)
        "title": rec.get("title", ""),
        "official_citation": rec.get("citation", ""),
        "jurisdiction": "",                      # TODO
        "document_type": "",                     # TODO
        "language": rec.get("language", ""),
        "authentic_languages": [rec["language"]] if rec.get("language") else [],
        "adoption_date": rec.get("date") or None,
        "source_url": rec.get("doc_url") or rec.get("url") or source["url"],
        "source_publisher": "",                  # TODO
        "source_is_official": True,
        "authoritative_status": "",              # TODO authentic_text / official_consolidation / certified_copy / authoritative_missing
        "capture_type": source.get("capture_type", "pdf"),
        # capture.py fills these once the official file is fetched:
        "original_source_path": "",              # REQUIRED before ingest (byte-for-byte original)
        "text_source_path": "",                  # required unless authoritative_status == authoritative_missing
        "capture_note": f"Listed by official source '{source['name']}'; drafted by the crawl layer, unverified.",
    }


def selected(src, rec, source_filter, match_filter) -> bool:
    """Pure: does this candidate gap pass the human's triage filters?"""
    if source_filter and source_filter.lower() not in src["name"].lower():
        return False
    if match_filter:
        hay = f"{rec.get('title', '')} {rec.get('citation', '')}".lower()
        if match_filter.lower() not in hay:
            return False
    return True


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="Draft ingest manifests from TRIAGED candidate gaps.",
        epilog="The gap list is deliberately over-inclusive — it is a list to judge, not a work queue. "
               "Filter it to what you have decided is in scope.")
    p.add_argument("--source", default="", help="only sources whose name contains this (case-insensitive)")
    p.add_argument("--match", default="", help="only instruments whose title or citation contains this")
    p.add_argument("--dry-run", action="store_true", help="list what would be written; write nothing")
    p.add_argument("--all", action="store_true", help="required to draft EVERY gap unfiltered (rarely right)")
    a = p.parse_args()

    inv_path = os.path.join(common.REPO, "monitoring", "inventory.json")
    if not os.path.isfile(inv_path):
        print("no monitoring/inventory.json — run scripts/crawl/map_sources.py first", file=sys.stderr)
        return 2
    inv = json.load(open(inv_path, encoding="utf-8"))

    picked = [(src, rec) for src in inv["sources"] for rec in src.get("candidate_gaps", [])
              if selected(src, rec, a.source, a.match)]
    total = sum(len(s.get("candidate_gaps", [])) for s in inv["sources"])

    # Refuse to flood the queue. Candidate gaps are over-inclusive BY DESIGN: the ITLOS register alone
    # contributes ~30, of which two are in scope for this corpus. Generating all of them would bury the
    # real work in files to delete, and invite ingesting something nobody judged.
    if not a.source and not a.match and not a.all:
        print(f"{total} candidate gap(s) across {len(inv['sources'])} source(s) — refusing to draft all of them.")
        print("\nGaps by source:")
        for s in inv["sources"]:
            g = len(s.get("candidate_gaps", []))
            if g:
                print(f"  {g:4d}  {s['name']}")
        print("\nTriage first, then filter, e.g.:")
        print('  python scripts/crawl/gen_manifests.py --source "Case No. 34" --dry-run')
        print('  python scripts/crawl/gen_manifests.py --match "Order"')
        print("Use --all only if you really do intend to draft every gap.")
        return 2

    if a.dry_run:
        print(f"DRY RUN — would write {len(picked)} manifest(s) of {total} candidate gap(s):")
        for src, rec in picked:
            print(f"  [{src['name']}] {rec.get('title') or rec.get('citation')}")
            print(f"      {rec.get('doc_url') or rec.get('url') or '(no document URL)'}")
        print("\nNothing was written.")
        return 0

    os.makedirs(MANIFEST_DIR, exist_ok=True)
    n = skipped = 0
    for src, rec in picked:
        man = draft_manifest(src, rec)
        fn = f"draft__{_slug(src['name'])}__{_slug(rec.get('title') or rec.get('citation'))}.json"
        path = os.path.join(MANIFEST_DIR, fn)
        if os.path.exists(path):                 # never clobber a human-edited draft
            skipped += 1
            continue
        json.dump(man, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        n += 1
    print(f"wrote {n} draft manifest(s) to {MANIFEST_DIR} ({skipped} already existed, left untouched)")
    print(f"selected {len(picked)} of {total} candidate gap(s)")
    print("Each is status: draft_requires_human_review. Verify citation/metadata, run capture.py, then ingest.py.")
    print("Nothing auto-ingests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
