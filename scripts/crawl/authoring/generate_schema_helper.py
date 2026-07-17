#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_schema_helper.py — OFF-PIPELINE schema drafting (the ONLY LLM step in this layer).

Run once per source, by a human, to DRAFT a JsonCssExtractionStrategy schema from a sample of the
source's index HTML, using JsonCssExtractionStrategy.generate_schema() (an LLM call). The draft is then
HAND-REVIEWED against the live page and committed to scripts/crawl/schemas/. Runtime extraction
(map_sources.py / watch_sources.py) never calls this — it uses the committed schema deterministically.

Requires crawl4ai and an LLM key (e.g. OPENAI_API_KEY). NOT run in CI or the monthly monitor.

Usage:
  python3 scripts/crawl/authoring/generate_schema_helper.py \
      --url "https://official-index-page" --out scripts/crawl/schemas/<name>.json \
      [--provider openai/gpt-4o]
Then open the output, hand-review every selector against the live page, and commit it.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request

DEFAULT_QUERY = ("Extract each listed legal instrument as a record with fields: "
                 "title, citation (official citation), date, doc_url (the href to the document), language.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="official index/registry page to sample")
    ap.add_argument("--out", required=True, help="where to write the DRAFT schema (schemas/<name>.json)")
    ap.add_argument("--provider", default="openai/gpt-4o")
    ap.add_argument("--query", default=DEFAULT_QUERY)
    a = ap.parse_args()

    try:
        from crawl4ai import JsonCssExtractionStrategy, LLMConfig
    except Exception:
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        from crawl4ai import LLMConfig

    token = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_TOKEN")
    if not token:
        print("Set OPENAI_API_KEY (or LLM_API_TOKEN). This authoring step needs an LLM; the runtime never does.",
              file=sys.stderr)
        return 2

    req = urllib.request.Request(a.url, headers={"User-Agent": "provenance-schema-authoring"})
    html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", errors="replace")

    cfg = LLMConfig(provider=a.provider, api_token=token)
    try:
        schema = JsonCssExtractionStrategy.generate_schema(html, query=a.query, schema_type="css", llm_config=cfg)
    except TypeError:
        # older/newer signatures may not accept `query`
        schema = JsonCssExtractionStrategy.generate_schema(html, schema_type="css", llm_config=cfg)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"DRAFT schema written to {a.out}")
    print("HAND-REVIEW every selector against the live page before committing.")
    print("Runtime extraction is deterministic and LLM-free; this step is authoring-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
