#!/usr/bin/env python3
"""Ingest the five born-digital ITLOS records for issue #9, deriving their text UNDER THE PIN.

WHY THIS RUNS IN CI AND NOT ON THE WORKSTATION (issue #9, approach 1). These five records are
born-digital: they carry the Tribunal's own PDF text layer, so their text is EXTRACTED and not
OCR'd, and there is no engine disagreement to adjudicate. It is still a DERIVED text, though, and a
derived text is reproducible only against the toolchain that produced it. This corpus pins Poppler
22.02.0, which its CI runner (ubuntu-22.04) carries; the workstation that authored these manifests
carries 26.01.0. Deriving there would stamp a text_sha256 that CI re-derives differently - a record
whose own gate could never reproduce it - so the derivation happens here, under the pin, and the
hash is CI's own.

HOW IT FITS THE EXISTING PATH. The manifests in queue/manifests/ deliberately carry
"text_source_path": null. This script fills that slot with the text it derives from the committed
extractor and hands the manifest to scripts/ingest.py - the same ingester every other record in this
corpus went through. No bespoke packaging: hashing, key order, schema validation and the
append-only refusal all stay in one place.

IDEMPOTENT BY REPORTING, NOT BY OVERWRITING. ingest.py refuses to write over an existing record. On
a second run this script therefore VERIFIES instead: it re-derives each text and compares it to the
committed text.txt, reporting OK or DIFFERS, and never rewrites - so a re-dispatch is a check, not a
silent takeover. Exit status is 0 only if every record is either newly ingested or verified equal.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import extract as E          # noqa: E402
import ingest                # noqa: E402

MANIFESTS = [
    "ready__itlos-order-case34-order-18jul2026.json",
    "ready__itlos-order-case35-order-18jul2026.json",
    "ready__itlos-declaration-case34-35-kittichaisaree-18jul2026.json",
    "ready__itlos-declaration-case34-brown-18jul2026.json",
    "ready__itlos-declaration-case35-brown-18jul2026.json",
]
TMP = Path("/tmp/itlos9-derived")


def main() -> int:
    ver = E.poppler_version()
    print(f"pdftotext (Poppler) {ver}   pinned {E.PINNED_POPPLER}")
    if ver != E.PINNED_POPPLER:
        # Fail closed. A text derived under a different Poppler is a text whose own gate cannot
        # reproduce it, and this corpus's whole claim is that its stored text re-derives from the
        # committed extractor. ITLOS9_ALLOW_UNPINNED exists ONLY so the mechanics of this script can
        # be exercised on a workstation; it must never be set in CI, and the derivation it produces
        # must never be committed.
        if os.environ.get("ITLOS9_ALLOW_UNPINNED") == "1":
            print("  WARNING: ITLOS9_ALLOW_UNPINNED=1 - deriving under an UNPINNED toolchain. "
                  "This output is for testing the mechanics ONLY and must not be committed.")
        else:
            sys.exit(f"REFUSING to derive: this toolchain is Poppler {ver}, but the corpus pins "
                     f"{E.PINNED_POPPLER}. The stored text_sha256 must be one this corpus's own CI "
                     f"re-derives, so run this script on a runner that carries the pin "
                     f"(ubuntu-22.04) - issue #9, approach 1.")
    TMP.mkdir(parents=True, exist_ok=True)

    ingested, verified, differs, problems = [], [], [], []
    for name in MANIFESTS:
        mpath = REPO / "queue" / "manifests" / name
        if not mpath.is_file():
            problems.append(f"{name}: manifest missing"); continue
        m = json.loads(mpath.read_text(encoding="utf-8"))
        cid, vid = m["corpus_id"], str(m["version_id"])
        fn = E.PDF_EXTRACTORS.get(cid)
        if fn is None:
            problems.append(f"{cid}: no committed extractor - refusing to ingest unverifiable text")
            continue
        src = REPO / m["original_source_path"]
        if not src.is_file():
            problems.append(f"{cid}: staged original missing at {m['original_source_path']}")
            continue
        # ONE derivation path: the committed extractor, fed the same pdftotext call the gate uses.
        got = E.norm(fn(E.pdftotext(str(src))))
        out = TMP / (cid.replace("/", "__") + ".txt")
        out.write_bytes(got)

        vdir = REPO / "authoritative" / cid / vid
        if vdir.is_dir():
            committed = (vdir / "text.txt").read_bytes() if (vdir / "text.txt").is_file() else b""
            if committed == got:
                verified.append(cid)
                print(f"  OK       {cid} v{vid}: re-derives byte-exact ({len(got)} bytes)")
            else:
                differs.append(cid)
                print(f"  DIFFERS  {cid} v{vid}: re-derivation does not match the committed text "
                      f"({len(got)} bytes vs {len(committed)}). NOT overwritten - investigate.")
            continue

        m["text_source_path"] = str(out)
        d = ingest.ingest_document(m, repo_root=REPO)
        ingested.append(cid)
        print(f"  INGESTED {cid} v{vid}: {len(got)} bytes of text -> {d.relative_to(REPO)}")

    print(f"\ningested: {len(ingested)}   verified equal on re-run: {len(verified)}   "
          f"DIFFERS: {len(differs)}   problems: {len(problems)}")
    for c in differs:
        print(f"  DIFFERS: {c}")
    for p in problems:
        print(f"  PROBLEM: {p}")
    if differs or problems:
        return 1
    print("RESULT: OK - every record is ingested, or already present and re-deriving byte-exact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
