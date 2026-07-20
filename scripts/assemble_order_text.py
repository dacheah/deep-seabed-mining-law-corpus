#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""assemble_order_text.py — build the reconciled reading text for ITLOS Order 2026/6.

ONE-OFF, kept for audit. Every transformation is listed here and repeated verbatim in the record's
provenance_note; nothing is done that is not written down.

BASE: Google Vision output. Vision won 9 of the 10 engine disagreements (Tesseract read closing
double-quotes as apostrophes in 5 places, misread "[a]t" as "[aJt", produced signature scribble as
text, and garbled the Registrar's name "Ximena ... OYARCE" as "Xifhena ... OVARCE").

ADJUDICATED CORRECTION (1): Vision produced "the submission." with a full stop mid-sentence in
"time limit for the submission of the written statement"; Tesseract has no stop. Tesseract adopted.

STRUCTURAL (wording untouched):
  * Running headers removed from pages 2-3 only: "List of Cases No. 34" / bare page number /
    "Order 2026/6". The SAME lines on page 1 are the document's header block and are kept.
  * Hard line wraps rejoined into paragraphs; paragraph numbers ("1.") rejoined to their text.
  * Curly quotes normalised to straight. Vision rendered them inconsistently WITHIN one sentence
    (“[a]t ... State"), which is an OCR artefact, not the document's typography.
  * Canonical stored form: UTF-8, LF, no BOM, exactly one trailing newline.
"""
from __future__ import annotations
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GV = os.path.join(REPO, "capture", "staging", "itlos-order-case34-order6-2026", "ocr", "gv")
OUT = os.path.join(REPO, "capture", "staging", "itlos-order-case34-order6-2026", "text.reconciled.txt")

RUNNING = re.compile(r"^(List of Cases No\. 34|Order 2026/6|\d{1,2})$")


def page_lines(n: int, strip_header: bool) -> list:
    raw = open(os.path.join(GV, f"p-{n:02d}.txt"), encoding="utf-8").read().splitlines()
    lines = [l.rstrip() for l in raw]
    if strip_header:
        # Running header sits at the very top; only strip the leading run, never mid-page text.
        while lines and (not lines[0].strip() or RUNNING.match(lines[0].strip())):
            lines.pop(0)
    return lines


# Display lines kept one-per-line: the header block on page 1, and the signature block at the end.
# Running them together would misrepresent the document's structure — these are not prose.
HEADER_END = "ORDER"
SIG_START = re.compile(r"^(David Joseph ATTARD|Ximena HINRICHS OYARCE)$")
# A new prose paragraph begins at a recital, the operative formula, a numbered whereas, or an
# operative disposition. Vision emits no blank lines between them, so boundaries must be explicit.
PARA_START = re.compile(
    r"^(Having regard to|Makes the following Order|Fixes\s|Reserves\s|Done in English|\d+\.$)")


def rejoin(lines: list) -> list:
    """Rejoin hard wraps into paragraphs, preserving display lines and operative boundaries."""
    out, buf = [], ""
    in_header, in_sig = True, False

    def flush():
        nonlocal buf
        if buf:
            out.append(buf)
            buf = ""

    for l in lines:
        s = l.strip()
        if not s:
            flush()
            continue
        if in_header:
            flush()
            out.append(s)                       # one display line each
            if s == HEADER_END:
                in_header = False
            continue
        if SIG_START.match(s) or in_sig:
            flush()
            out.append(s)                       # signature block: one line each
            in_sig = True
            continue
        if PARA_START.match(s):
            flush()
            buf = s
            continue
        buf = f"{buf} {s}".strip() if buf else s
    flush()
    return out


def main() -> int:
    all_lines = page_lines(1, False) + page_lines(2, True) + page_lines(3, True)
    paras = rejoin(all_lines)

    text = "\n\n".join(paras)
    # adjudicated correction (site 7)
    before = text
    text = text.replace("as the time limit for the submission. of the written statement",
                        "as the time limit for the submission of the written statement")
    if text == before:
        print("WARNING: site-7 correction did not apply — check the source text", file=sys.stderr)
    # quote normalisation (documented above)
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'")):
        text = text.replace(a, b)
    text = re.sub(r"[ \t]+", " ", text).strip() + "\n"

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote {OUT}  ({len(text)} chars, {text.count(chr(10)) + 1} lines)")
    print("STAGING ONLY — nothing written to authoritative/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
