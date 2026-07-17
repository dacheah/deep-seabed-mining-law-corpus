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


def main():
    inv_path = os.path.join(common.REPO, "monitoring", "inventory.json")
    if not os.path.isfile(inv_path):
        print("no monitoring/inventory.json — run scripts/crawl/map_sources.py first", file=sys.stderr)
        return 2
    inv = json.load(open(inv_path, encoding="utf-8"))
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    n = skipped = 0
    for src in inv["sources"]:
        for rec in src.get("candidate_gaps", []):
            man = draft_manifest(src, rec)
            fn = f"draft__{_slug(src['name'])}__{_slug(rec.get('title') or rec.get('citation'))}.json"
            path = os.path.join(MANIFEST_DIR, fn)
            if os.path.exists(path):             # never clobber a human-edited draft
                skipped += 1
                continue
            json.dump(man, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            n += 1
    print(f"wrote {n} draft manifest(s) to {MANIFEST_DIR} ({skipped} already existed, left untouched)")
    print("Each is status: draft_requires_human_review. Verify citation/metadata, run capture.py, then ingest.py.")
    print("Nothing auto-ingests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
