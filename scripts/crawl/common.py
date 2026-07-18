#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""common.py — shared helpers for the Crawl4AI source-mapping / capture / monitoring layer.

Corpus-agnostic. Loads monitoring/sources.json + per-source CSS schemas, and wraps the DETERMINISTIC
Crawl4AI runtime (JsonCssExtractionStrategy — no LLM, no stealth, robots respected). See
scripts/crawl/README.md for the Layer-1 boundary: nothing here ever writes authoritative/ text;
scripts/extract.py stays the sole version-pinned extractor.
"""
from __future__ import annotations
import datetime
import hashlib
import json
import os
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

# Pinned Crawl4AI version — MUST match scripts/requirements.txt. Recorded in captures + rendered-DOM metadata.
PINNED_CRAWL4AI = "0.8.9"
# Deterministic browser config for rendered-DOM captures (recorded in the manifest per boundary rule 3).
BROWSER_CONFIG = {
    "browser_type": "chromium",
    "headless": True,
    "java_script_enabled": True,
    "stealth": False,       # boundary rule 2 — never
    "magic": False,         # never
    "proxy": None,          # never
}
UA = "provenance-corpus-monitor/0.2 (+deterministic; honours robots.txt)"

HERE = os.path.dirname(os.path.abspath(__file__))     # scripts/crawl
SCRIPTS = os.path.dirname(HERE)                        # scripts
REPO = os.path.dirname(SCRIPTS)                        # repo root
SOURCES_PATH = os.path.join(REPO, "monitoring", "sources.json")
SCHEMAS_DIR = os.path.join(HERE, "schemas")


# ---- io -------------------------------------------------------------------------------------------
def load_sources() -> dict:
    with open(SOURCES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_sources(data: dict) -> None:
    with open(SOURCES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_schema(schema_file: str) -> dict:
    with open(os.path.join(SCHEMAS_DIR, schema_file), encoding="utf-8") as f:
        return json.load(f)


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- deterministic hashing ------------------------------------------------------------------------
def canonical_json(obj) -> bytes:
    """Stable serialisation for hashing: sorted keys, minimal separators, UTF-8."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def records_hash(records: list) -> str:
    """Hash of a source's extracted record set, invariant to key/record order."""
    canon = sorted(canonical_json(r).decode("utf-8") for r in records)
    return sha256_hex(canonical_json(canon))


# ---- robots + verbatim byte fetch (stdlib; used for official PDFs) --------------------------------
def robots_allows(url: str, ua: str = UA) -> bool:
    """Honour robots.txt on the verbatim-bytes path (the Crawl4AI path uses check_robots_txt=True)."""
    try:
        p = urlparse(url)
        rp = RobotFileParser()
        rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
        rp.read()
        return rp.can_fetch(ua, url)
    except Exception:
        return True  # unreadable robots is not a fabricated block; the caller logs HTTP status


def http_get_bytes(url: str, timeout: int = 60) -> tuple[bytes, int]:
    """Verbatim byte GET — official PDFs are stored byte-for-byte, never rendered or transformed."""
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r:
        return r.read(), int(getattr(r, "status", 200) or 200)


def http_get_text(url: str, timeout: int = 45) -> tuple[str, int]:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace"), int(getattr(r, "status", 200) or 200)


# ---- Crawl4AI (optional at runtime; deterministic CSS extraction only) ----------------------------
def crawl4ai_status() -> tuple[bool, str]:
    try:
        import crawl4ai
        v = getattr(crawl4ai, "__version__", None)
        if not isinstance(v, str):
            # crawl4ai.__version__ can be the submodule object, not the string — dig out the string.
            v = getattr(v, "__version__", None)
            if not isinstance(v, str):
                try:
                    from importlib.metadata import version
                    v = version("crawl4ai")
                except Exception:
                    v = "unknown"
        return True, v
    except Exception as e:  # not installed / import error -> caller falls back
        return False, f"{type(e).__name__}: {e}"


def _import_css_strategy():
    try:
        from crawl4ai import JsonCssExtractionStrategy  # top-level (0.8.x+)
        return JsonCssExtractionStrategy
    except Exception:
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy  # fallback path
        return JsonCssExtractionStrategy


async def crawl_extract(url: str, schema: dict, render: bool = True):
    """DETERMINISTIC Crawl4AI run: CSS-schema extraction, robots respected, no stealth/LLM.

    Returns (records: list[dict], html: str, status: int|None). Requires crawl4ai installed.
    """
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
    strategy = _import_css_strategy()(schema)
    bconf = BrowserConfig(
        browser_type=BROWSER_CONFIG["browser_type"],
        headless=BROWSER_CONFIG["headless"],
        java_script_enabled=BROWSER_CONFIG["java_script_enabled"] and render,
        user_agent=UA,
        verbose=False,
    )
    run = CrawlerRunConfig(
        extraction_strategy=strategy,
        check_robots_txt=True,          # boundary rule 2 — never bypass
        cache_mode=CacheMode.BYPASS,
    )
    async with AsyncWebCrawler(config=bconf) as crawler:
        res = await crawler.arun(url=url, config=run)
        status = getattr(res, "status_code", None)
        if not getattr(res, "success", False):
            raise RuntimeError(f"crawl failed (status={status}): {getattr(res, 'error_message', '') or 'unknown'}")
        records = json.loads(res.extracted_content) if getattr(res, "extracted_content", None) else []
        return records, (getattr(res, "html", "") or ""), status


async def crawl_render_html(url: str, render: bool = True):
    """Render a page and return its raw DOM HTML (for storing a rendered original.html)."""
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
    bconf = BrowserConfig(browser_type=BROWSER_CONFIG["browser_type"], headless=True,
                          java_script_enabled=render, user_agent=UA, verbose=False)
    run = CrawlerRunConfig(check_robots_txt=True, cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler(config=bconf) as crawler:
        res = await crawler.arun(url=url, config=run)
        status = getattr(res, "status_code", None)
        if not getattr(res, "success", False):
            raise RuntimeError(f"render failed (status={status}): {getattr(res, 'error_message', '') or 'unknown'}")
        return (getattr(res, "html", "") or ""), status
