#!/usr/bin/env python3
"""reconcile_itlos_orders.py — reconcile the two OCR engines for Orders 2026/8 and 2026/9.

Adjudication performed 2026-09-14. Base text is TESSERACT's, because it is structurally correct
(layout, spacing, paragraph numbers, running headers) and matched the page images at every site
checked. RapidOCR's output is the second opinion; the adopted RapidOCR corrections are ones verified
RIGHT against the page.

ENGINE DIVISION OF LABOUR, every site adjudicated against the 300-dpi page renders:

  Tesseract adopted (RapidOCR wrong):
    - running headers incl. page numbers ("List of Cases No. 34 2 Order 2026/8") - RapidOCR omits
      the page number
    - paragraph markers: RapidOCR dropped the "2." of para 2 on both orders
    - "of the Rules of the Tribunal" - RapidOCR inserted a spurious full stop
    - "(ISBA/31/C34), the Legal and Technical Commission ... (hereinafter" - RapidOCR inserted a
      spurious full stop
    - "NORI" - RapidOCR read a lowercase l
    - "v." in the case name - lowercase in the document; RapidOCR read uppercase V
    - "Secretary-General" - RapidOCR read a trailing i ("Generai")
    - Order 2026/9 page 1, the whole "Having regard to articles 27 and 40, paragraph 1, of the
      Statute of the Tribunal" recital - RapidOCR produced garbage here

  RapidOCR adopted (Tesseract wrong):
    - the Registrar's given name "Ximena" - Tesseract dropped the X on Order 2026/8 ("imena") and
      rendered a brace on Order 2026/9 ("X{mena"). Verified on both page images.
    - "Registrar" on Order 2026/9 - Tesseract split it into "f Real" + "egistrar" and lost the
      initial R. Verified: RapidOCR read the word correctly on both orders.

  Adjudicated against the page, NEITHER engine exact:
    - the numeral in "before the end of part I of [the Commission's] next session" (quoted passage,
      para 5) is a Roman capital I. Tesseract read it as a pipe; RapidOCR did not recover it either.

  Dropped as non-text: the handwritten signature strokes, which Tesseract emitted as character
  noise ("ae ------- mena an", "va / | 4", "f Real") and RapidOCR omitted. Signatures are not part
  of the authentic text; the typed names beneath them are retained.

ORDERS 2026/3 AND 2026/4 (Cases No. 34 and No. 35, 10 June 2026) — SAME METHOD, SHORTER DOCUMENTS.
Both are office-scanner images (Konica, "KM_4050i") carrying an Adobe Paper Capture VENDOR text layer.
That layer was NOT adopted and is not the base: it is a third, unversioned engine, and it is provably
wrong in it — it reads "ING." for "INC." on Order 2026/3 and "heceinafter" for "hereinafter", which is
how it was identified as vendor OCR rather than the Tribunal's own typing. The text is the two-engine
reading, adjudicated the same way as the orders above:

  Tesseract adopted (RapidOCR wrong):
    - "hereinafter" — RapidOCR read "hereinater" (Order 2026/3, page 1).
    - whole recital lines: RapidOCR garbled "International" as "Internatioral" and merged or dropped
      lines on both orders' page 1. Tesseract's structure matched the page at every site checked.
  RapidOCR adopted (Tesseract wrong):
    - the Registrar's given name "Ximena" on BOTH orders. Tesseract read "de" on Order 2026/3 and
      "ximene" on Order 2026/4; RapidOCR read the name correctly on both, verified against both page
      images. This is the same correction the sibling orders needed — a third confirmation of it.
  Adjudicated ON THE PAGE and retained as the Tribunal's own text, not "corrected" as an OCR error:
    - Order 2026/4: "the Request submitted by TOML Registry on 5 June 2026" — the word "Registry" is
      PRINTED on the page. It is a drafting slip in the instrument (Order 2026/3 reads "submitted by
      NORI", with no such word) and it is reproduced, not silently fixed. Likewise "transmitted to the
      NORI and the Authority" / "the TOML and the Authority" — the article is on the page in both.
  Dropped as non-text: the signature strokes. Tesseract emitted them as "4 ." and "bal" (Order
  2026/3) and "Pr 4" (Order 2026/4); RapidOCR omitted them. On Order 2026/4 a scanner edge mark was
  read as "|" at the head of the last recital line.

NORMALISATION — matched to the ingested sibling record itlos/order/case34-order6-2026, which is the
spec, not invented here:

  * Curly quotation marks are normalised to STRAIGHT ("), and curly apostrophes to straight (').
    The sibling's text.txt carries 20 straight double quotes and zero curly ones. (Its provenance
    note records the same rule: "curly quotes normalised to straight".)
  * The running header ("List of Cases No. NN" / page number / "Order 2026/N") is removed from pages
    2 and 3 only - the same lines on page 1 ARE the document's header block and are kept.
  * Display lines - the header block, the case title, "ORDER", "THE PRESIDENT OF THE CHAMBER" and
    everything after it (the disposition and the signature block) - are each their own block,
    separated by a blank line, exactly as the sibling presents them. Wrapped body prose is rejoined
    into paragraphs.
  * Canonical UTF-8, LF, no BOM, one trailing newline.
"""
from __future__ import annotations
import pathlib
import re

STAGING = pathlib.Path("capture/staging")

# Adjudicated corrections to the Tesseract base. Applied PER SOURCE LINE, before blocks are joined —
# a correction applied after the join cannot change block boundaries, which merged the Registrar's
# name onto the line above it the first time round.
LINE_CORRECTIONS = {
    "itlos-order-case34-order8-2026": [("imena HINRICHS", "Ximena HINRICHS"),
                                       ("part | of", "part I of")],
    "itlos-order-case35-order9-2026": [("X{mena HINRICHS", "Ximena HINRICHS"),
                                       ("part | of", "part I of")],
    # Orders 2026/3 and 2026/4 (10 June 2026). Adjudicated 2026-09-16 against the 300-dpi renders:
    # the Registrar's given name is printed "Ximena" in both (Tesseract read "de" and "ximene"), and
    # on Order 2026/4 a scanner edge mark sits at the head of the last recital line.
    "case34-order3-2026": [("de HINRICHS OYARCE", "Ximena HINRICHS OYARCE")],
    "case35-order4-2026": [("ximene HINRICHS OYARCE", "Ximena HINRICHS OYARCE"),
                           ("| Having regard", "Having regard")],
}

# Tail repairs applied AFTER the join. On Order 2026/9 Tesseract split "Registrar" into "f Real" +
# "egistrar" (losing the R) and both fragments were dropped as noise, so the word has to be restored
# from the second engine, which read it correctly.
TAIL_REPAIR = {"itlos-order-case35-order9-2026": "Registrar"}

# Lines that are signature strokes / scanner artefacts, not text.
NOISE = {"|", "<n =o See -.", "ae ———- mena an", "va / | 4", "f Real", "egistrar",
         "f Real egistrar",
         # Signature-stroke noise on the 10 June 2026 orders, dropped after checking the page:
         # "4 ." and "bal" (Order 2026/3), "Pr 4" (Order 2026/4). RapidOCR omitted all of them.
         "4 .", "bal", "Pr 4"}

HEADER_RE = re.compile(r"^List of Cases No\.\s*\d+\s*\d*\s*Order 2026/\d+\s*$")

# Lines that are always their own block, never merged into neighbouring prose.
BLOCK_RE = re.compile(
    r"^(List of Cases No\.|Order 2026/\d+$|\(.*\)$|Makes the following Order:$|THE PRESIDENT|"
    r"Taking into account|Extends |Reserves |Fixes |Done in English|David Joseph ATTARD$|"
    r"President of the Seabed|Ximena HINRICHS|Registrar$|YEAR \d{4}$|\d{1,2} \w+ \d{4}$|"
    r"Having regard|Having ascertained|The President of the Seabed)"
)


def _is_display(line: str) -> bool:
    """True for centred display lines such as 'CASE CONCERNING AN INQUIRY' or 'ORDER'."""
    letters = [c for c in line if c.isalpha()]
    if len(letters) < 3:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.8


def rejoin(lines: list[str]) -> str:
    """Join wrapped prose into paragraphs, keeping display/structural lines as their own blocks.

    Deliberately NOT a line-per-block mode for the tail: the disposition and the "Done in English
    and in French ..." formula wrap across source lines and must rejoin, exactly as the sibling
    record presents them. Each signature name is a block because it matches BLOCK_RE.
    """
    blocks: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        new_block = (_is_display(line) or bool(re.match(r"^\d+\.\s", line))
                     or bool(BLOCK_RE.match(line)))
        if blocks and not new_block:
            blocks[-1] = blocks[-1] + " " + line
        else:
            blocks.append(line)
    return "\n\n".join(blocks)


def normalise_quotes(s: str) -> str:
    """Normalise quotation marks and apostrophes to STRAIGHT, per the sibling record's rule.

    Tesseract renders the closing mark of a double-quoted phrase as a right SINGLE quote, so the
    pairs are repaired against the opening curly double quote first. Without this step the closing
    mark straightens to ' and the text reads: (hereinafter "the Chamber') - a stray apostrophe.
    """
    s = re.sub(r"“([^“”\n]{1,140}?)’", lambda m: "“" + m.group(1) + "”", s)
    s = re.sub(r"“([^“”\n]{1,140}?)\"", lambda m: "“" + m.group(1) + "”", s)
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("’", "'").replace("‘", "'")
    return s


def build(order: str) -> str:
    base = STAGING / order / "ocr"
    pages: list[str] = []
    # Globbed, not hardcoded: the 10 June 2026 orders are two pages each and the 2026/6-2026/9
    # orders are three. A hardcoded page tuple silently drops pages the day a shorter document is
    # added to the loop below.
    for p in [f.stem for f in sorted((STAGING / order / "ocr" / "tess").glob("p-*.txt"))]:
        lines = (base / "tess" / f"{p}.txt").read_text(encoding="utf-8").splitlines()
        cleaned = []
        for ln in lines:
            if ln.strip() in NOISE:
                continue
            if p != "p-01" and HEADER_RE.match(ln.strip()):
                continue
            for old, new in LINE_CORRECTIONS[order]:
                ln = ln.replace(old, new)
            cleaned.append(ln)
        pages.append(normalise_quotes(rejoin(cleaned)))
    body = re.sub(r"\n{3,}", "\n\n", "\n\n".join(pages)).strip() + "\n"

    repair = TAIL_REPAIR.get(order)
    if repair:
        last = body.rstrip().split("\n\n")[-1]
        if last != repair:
            body = body.rstrip() + "\n\n" + repair + "\n"
    return body


def main() -> int:
    for order in ("itlos-order-case34-order8-2026", "itlos-order-case35-order9-2026",
                  "case34-order3-2026", "case35-order4-2026"):
        out = STAGING / order / "text.reconciled.txt"
        out.write_text(build(order), encoding="utf-8", newline="\n")
        b = out.read_bytes()
        t = b.decode("utf-8")
        assert not b.startswith(b"\xef\xbb\xbf"), "BOM present"
        assert b.endswith(b"\n") and not b.endswith(b"\n\n"), "trailing newline wrong"
        assert b"\r" not in b, "CR present"
        assert not any(c in t for c in "“”‘’"), "curly quote survived normalisation"
        assert not re.search(r"[|{}~^_\\]", t), "artefact character survived"
        print(f"wrote {out}  ({len(b)} bytes, {len(t.split())} words, "
              f"{t.count(chr(34))} quotes, blocks={t.count(chr(10)+chr(10))+1})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
