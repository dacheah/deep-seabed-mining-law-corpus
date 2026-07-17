#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""capture.py — (skill step 4) fetch the official file for a draft manifest into staging.

  * PDF  sources -> verbatim byte download (byte-for-byte; never rendered or transformed).
  * HTML sources -> Crawl4AI-rendered DOM stored as original.html — a RENDERED SNAPSHOT, recorded as
    such with the pinned Crawl4AI version and browser config (Layer-1 boundary rule 3).

robots.txt is honoured on BOTH paths. Output goes to capture/staging/<slug>/ with a capture-log.json
(url, timestamp, HTTP status, crawler version). This does NOT ingest — a human verifies fidelity, sets
the manifest's capture paths, then runs ingest.py.
"""
from __future__ import annotations
import asyncio
import json
import os
import re
import sys

import common

STAGING = os.path.join(common.REPO, "capture", "staging")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")[:60] or "capture"


def _write_log(outdir, log):
    with open(os.path.join(outdir, "capture-log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def capture(manifest_path):
    man = json.load(open(manifest_path, encoding="utf-8"))
    url = man.get("source_url") or man.get("_source_url")
    if not url:
        raise SystemExit("manifest has no source_url")
    ctype = (man.get("capture_type") or "pdf").lower()
    slug = _slug(man.get("corpus_id") or man.get("title") or os.path.basename(manifest_path))
    outdir = os.path.join(STAGING, slug)
    os.makedirs(outdir, exist_ok=True)

    log = {"url": url, "capture_type": ctype, "timestamp": common.now_iso(),
           "crawl4ai_version": None, "http_status": None, "robots": None,
           "browser_config": None, "artifact": None, "note": None}

    if not common.robots_allows(url):
        log["robots"] = "DISALLOWED"
        log["note"] = "robots.txt disallows fetch — escalate to a human download; do not bypass."
        _write_log(outdir, log)
        raise SystemExit(f"robots.txt disallows {url} — escalate to a human download (boundary rule 2).")
    log["robots"] = "allowed"

    if ctype == "pdf":
        data, status = common.http_get_bytes(url)
        with open(os.path.join(outdir, "original.pdf"), "wb") as f:
            f.write(data)
        log.update(http_status=status, artifact="original.pdf",
                   note="verbatim byte download (byte-for-byte official file).")
    elif ctype == "html":
        ok, ver = common.crawl4ai_status()
        if not ok:
            raise SystemExit(f"HTML capture needs crawl4ai (rendered snapshot); not installed: {ver}")
        html, status = asyncio.run(common.crawl_render_html(url))
        with open(os.path.join(outdir, "original.html"), "w", encoding="utf-8") as f:
            f.write(html)
        log.update(http_status=status, artifact="original.html", crawl4ai_version=ver,
                   browser_config=common.BROWSER_CONFIG,
                   note=("RENDERED DOM snapshot (not a byte-for-byte file download). "
                         "Record original_capture: rendered_dom in metadata.yaml with this version + browser_config."))
    else:
        raise SystemExit(f"unknown capture_type: {ctype!r} (expected 'pdf' or 'html')")

    _write_log(outdir, log)
    print(f"captured -> {os.path.join(outdir, log['artifact'])}")
    print(f"capture log -> {os.path.join(outdir, 'capture-log.json')}")
    print("Next (human): verify fidelity vs the official source, set original_source_path/text_source_path "
          "in the manifest, then run scripts/ingest.py.")


def main():
    if len(sys.argv) < 2:
        print("usage: python3 scripts/crawl/capture.py <path/to/manifest.json>", file=sys.stderr)
        return 2
    capture(sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
