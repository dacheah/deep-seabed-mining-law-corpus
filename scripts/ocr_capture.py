#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ocr_capture.py — dual-engine OCR of a captured PDF whose text layer cannot be trusted.

WHEN TO USE THIS. Not by default. `scripts/extract.py` remains the sole extractor for PDFs with a
sound text layer. This exists for the case where the text layer is ABSENT or CORRUPT:

  * ITLOS Order 2026/6 (Case 34): 3 pages, of which 2 are CCITT 1-bit scans with no text layer at
    all, and page 1's embedded font renders "ORDER" as "OROER" — a broken cmap.
  * The same failure class as the BBNJ Arabic PDF, where pdftotext/PyMuPDF yielded ~30% wrong
    glyphs because the fonts carry no usable Unicode map.

METHOD — deliberately the same as the BBNJ Arabic pass, so the verification bar is consistent:
render each page at 300 dpi, OCR with TWO independent engines, then reconcile. Neither engine's
output is authoritative on its own. `original.pdf` remains the integrity anchor throughout; OCR
recovers a READING of the official text, and the record must say so.

    python3 scripts/ocr_capture.py --pdf capture/staging/<slug>/original.pdf

Requires: pymupdf, pytesseract, pillow, requests. Tesseract binary on PATH or via TESSERACT env
var. Google Vision needs GVISION_API_KEY (3 pages = 3 units against a free 1,000/month).
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import sys

DPI = 300
PSM = 6      # assume a uniform block of text — right for a single-column judicial order
OEM = 3      # default LSTM engine


def _need(mod):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"Missing dependency: {mod}. Run: pip install pymupdf pytesseract pillow requests")


def render_pages(pdf_path, outdir, dpi=DPI):
    fitz = _need("fitz")
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf_path)
    paths = []
    for i, page in enumerate(doc, 1):
        p = os.path.join(outdir, f"p-{i:02d}.png")
        with open(p, "wb") as f:
            f.write(page.get_pixmap(dpi=dpi).tobytes("png"))
        paths.append(p)
    doc.close()
    return paths


def ocr_tesseract(png_paths, outdir, lang="eng"):
    pytesseract = _need("pytesseract")
    Image = _need("PIL.Image")
    from PIL import Image as PILImage
    cmd = os.environ.get("TESSERACT") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(cmd):
        pytesseract.pytesseract.tesseract_cmd = cmd
    ver = str(pytesseract.get_tesseract_version())
    os.makedirs(outdir, exist_ok=True)
    out = []
    for p in png_paths:
        txt = pytesseract.image_to_string(PILImage.open(p), lang=lang,
                                          config=f"--oem {OEM} --psm {PSM}")
        dst = os.path.join(outdir, os.path.basename(p).replace(".png", ".txt"))
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        out.append(dst)
    return out, ver


def ocr_gvision(png_paths, outdir, hint="en"):
    requests = _need("requests")
    key = os.environ.get("GVISION_API_KEY", "").strip()
    if not key:
        return [], "SKIPPED: GVISION_API_KEY not set"
    url = "https://vision.googleapis.com/v1/images:annotate?key=" + key
    os.makedirs(outdir, exist_ok=True)
    out = []
    for p in png_paths:
        body = {"requests": [{"image": {"content": base64.b64encode(open(p, "rb").read()).decode()},
                              "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                              "imageContext": {"languageHints": [hint]}}]}
        r = requests.post(url, json=body, timeout=90)
        r.raise_for_status()
        resp = r.json()["responses"][0]
        if "error" in resp:
            sys.exit(f"Vision error on {p}: {resp['error'].get('message')}")
        txt = resp.get("fullTextAnnotation", {}).get("text", "")
        dst = os.path.join(outdir, os.path.basename(p).replace(".png", ".txt"))
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        out.append(dst)
    return out, "google-cloud-vision DOCUMENT_TEXT_DETECTION"


def main():
    ap = argparse.ArgumentParser(description="Dual-engine OCR for a PDF with an untrustworthy text layer.")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--lang-tess", default="eng")
    ap.add_argument("--lang-gv", default="en")
    a = ap.parse_args()

    base = os.path.join(os.path.dirname(a.pdf), "ocr")
    pdf_sha = "sha256:" + hashlib.sha256(open(a.pdf, "rb").read()).hexdigest()

    pngs = render_pages(a.pdf, os.path.join(base, "pages"))
    print(f"rendered {len(pngs)} page(s) at {DPI} dpi")
    t_files, t_ver = ocr_tesseract(pngs, os.path.join(base, "tess"), a.lang_tess)
    print(f"tesseract {t_ver}: {len(t_files)} page(s)")
    g_files, g_ver = ocr_gvision(pngs, os.path.join(base, "gv"), a.lang_gv)
    print(f"google vision: {len(g_files)} page(s) — {g_ver if not g_files else 'ok'}")

    manifest = {"source_pdf": os.path.relpath(a.pdf), "source_sha256": pdf_sha, "dpi": DPI,
                "tesseract": {"version": t_ver, "psm": PSM, "oem": OEM, "lang": a.lang_tess,
                              "pages": len(t_files)},
                "gvision": {"engine": g_ver, "lang_hint": a.lang_gv, "pages": len(g_files)},
                "note": ("Neither engine is authoritative alone. Reconcile the two, adjudicate every "
                         "disagreement against the page images, and record the result honestly in "
                         "text_fidelity. original.pdf remains the integrity anchor.")}
    mpath = os.path.join(base, "ocr-manifest.json")
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"manifest -> {mpath}")
    if not g_files:
        print("\nWARNING: only ONE engine ran. A single-engine result is 'ocr_unverified',")
        print("a lower standard than the BBNJ Arabic text. Set GVISION_API_KEY and re-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
