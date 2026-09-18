"""
extract.py — reproducible source→text extraction.

Re-derives every authoritative `text.txt` from its stored `original.*` using committed,
deterministic code, and checks each result byte-for-byte against the recorded `text_sha256`.
This closes the reproducibility axis for the four PDF-sourced records (the text can be regenerated
from the byte-exact official PDF by code in this repo), and confirms the six text-sourced records
reproduce via the canonical normaliser.

PINNED TOOLCHAIN: PDF text is read with `pdftotext -enc UTF-8` from Poppler **22.02.0**.
Byte-exact reproduction of the PDF-sourced records is guaranteed only against this Poppler version;
a different version may shift whitespace/ligatures. The script prints the detected version and warns
on mismatch. (The authoritative anchor remains the byte-exact original.pdf + its recorded hash; this
script proves the derived text.txt is reproducible, not a substitute for that anchor.)

Usage:
    python3 scripts/extract.py            # check all records, print X/Y reproduced (exit 1 if any differ)
    python3 scripts/extract.py --write    # (re)write text.txt from the committed extractor
    python3 scripts/extract.py --attest   # write/refresh per-record toolchain attestations

PINNED_POPPLER is the version NEW derivations are calibrated against — a statement about the present.
The per-record attestations under extraction/ are the historical claim (which toolchain actually
re-derived which record's text); see the ATTEST comment below for why the two are not the same thing.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, subprocess, sys, unicodedata
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH = os.path.join(REPO, "authoritative")
PINNED_POPPLER = "22.02.0"

def pdftotext(pdf: str, raw: bool = False, layout: bool = False) -> str:
    """pdftotext with this record's extra flags (both are per-record: see PDF_RAW / PDF_LAYOUT).

    `-layout` keeps every printed line where it sits on the page. It is the honest read for a document
    whose section number and section title are typeset as a margin block, because the default reading
    order pairs each number with the wrong section (Tonga's 2016 Revised Edition, issue #13).
    """
    cmd = (["pdftotext", "-enc", "UTF-8"] + (["-raw"] if raw else []) + (["-layout"] if layout else [])
           + [pdf, "-"])
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

def poppler_version() -> str:
    out = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr
    m = re.search(r"pdftotext version (\S+)", out)
    return m.group(1) if m else "?"

def norm(text: str) -> bytes:
    """Canonical stored form: UTF-8, LF, no BOM, exactly one trailing newline (matches hashing.py)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("﻿"): text = text[1:]
    return (text.rstrip("\n") + "\n").encode("utf-8")

_LIG = [("ﬁ","fi"),("ﬂ","fl"),("ﬀ","ff"),("ﬃ","ffi"),("ﬄ","ffl"),("ﬅ","ft"),("ﬆ","st")]

# ---- per-source cleaners (each returns the full text incl. its title line) -------------------

def clean_ao(raw: str) -> str:
    m = re.search(r"ADVISORY OPINION\s*\nPresent:", raw); body = raw[m.start():]
    kept = []
    for ln in body.split("\n"):
        s = ln.strip()
        if s == "\x0c" or s == "": kept.append(""); continue
        low = s.lower()
        if low == "responsibilities and obligations of states with respect to": continue
        if low == "activities in the area (advisory opinion of 1 february 2011)": continue
        if re.fullmatch(r"\d{1,3}", s): continue
        kept.append(s.replace("\x0c", ""))
    t = "\n".join(kept)
    for a, b in _LIG: t = t.replace(a, b)
    t = re.sub(r"[ \t]*\n[ \t]*", " ", t); t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r'(?<=[.\)\]”"’:])\s+(\d{1,3}\.)\s+(?=[A-Z“"])', r"\n\n\1 ", t)
    paras = [p.strip() for p in t.split("\n\n") if p.strip()]
    title = ("Responsibilities and obligations of States sponsoring persons and entities with respect "
             "to activities in the Area — Advisory Opinion of 1 February 2011 (ITLOS Seabed Disputes "
             "Chamber, Case No. 17)")
    return title + "\n\n" + "\n\n".join(paras) + "\n"

# ---- ITLOS born-digital documents (text layer, no OCR) ------------------------------------------
# The orders and declarations issued from the Tribunal's own typesetting carry an extractable text
# layer, so nothing is OCR'd and nothing is adjudicated: pdftotext returns the Tribunal's own
# characters, and the byte-exact original.pdf stays the integrity anchor. What they need is the
# same STRUCTURAL NORMALISATION the scan-based ITLOS records received, so the two read alike - the
# running header and page numbers dropped, hard line wraps rejoined into paragraphs, display lines
# kept as their own block, curly quotes normalised to straight. Wording is never touched.
#
# Two features of the Tribunal's layout drive this cleaner:
#   * every page after the first opens with its page number and nothing else;
#   * the paragraph number sits in the left margin, so pdftotext emits it on a line of its own and
#     the cleaner folds 'N.' back onto the paragraph it numbers.
# A page break inside a paragraph is NOT re-joined, so such a paragraph appears as two blocks. The
# scan-based siblings were reconciled by hand and break at different places, so block structure is
# not comparable between the two conventions - only the wording is, and it is unchanged.
_ITLOS_MASTHEAD = [r"SEABED DISPUTES CHAMBER OF THE",
                   r"INTERNATIONAL TRIBUNAL FOR THE LAW OF THE SEA",
                   r"Year \d{4}", r"\d{1,2} [A-Z][a-z]+ \d{4}", r"List of Cases:", r"No\. \d+"]

def clean_itlos_text_layer(raw: str, title_anchor: str) -> str:
    m = re.search(title_anchor, raw)
    if not m:
        raise ValueError("anchor not found in extraction: %r" % title_anchor)
    blocks, page_of = [], []
    for pi, page in enumerate(raw[m.start():].split("\f")):
        lines = [l.rstrip() for l in page.split("\n")]
        while lines and not lines[0].strip():
            lines.pop(0)
        if pi:
            if lines and re.fullmatch(r"\d{1,3}", lines[0].strip()):
                lines.pop(0)
        elif len(lines) >= len(_ITLOS_MASTHEAD) and all(
                re.fullmatch(p, lines[i].strip()) for i, p in enumerate(_ITLOS_MASTHEAD)):
            # the masthead, kept line by line (the sibling record keeps the same lines as blocks)
            for i in range(len(_ITLOS_MASTHEAD)):
                blocks.append(lines[i].strip()); page_of.append(pi)
            lines = lines[len(_ITLOS_MASTHEAD):]
        for blk in "\n".join(lines).split("\n\n"):
            glines = [l.strip() for l in blk.split("\n") if l.strip()]
            if not glines:
                continue
            if len(glines) > 1 and re.fullmatch(r"\d{1,3}\.", glines[-1]):
                # a margin number stranded at the end of a group - the line it sits under is NOT
                # the paragraph it numbers, so peel it off and let it fold onto what follows. The
                # test is on its own LINE, never on the joined text: a sentence ending in a numeral
                # ("Section 5.") would otherwise be mistaken for a marker.
                blocks.append(" ".join(glines[:-1])); page_of.append(pi)
                glines = glines[-1:]
            blk = " ".join(glines)
            if blocks and re.fullmatch(r"\d{1,3}\.", blocks[-1]):
                blocks[-1] = blocks[-1] + " " + blk
            else:
                blocks.append(blk); page_of.append(pi)
    # The Tribunal's layout emits blank lines INSIDE a paragraph as well as between paragraphs, so
    # a paragraph often arrives as several groups. Re-join on two pieces of evidence: the earlier
    # group does not close a sentence (a group ending in a full stop, question or exclamation mark
    # does - a comma, semicolon or closing bracket does not, and neither does a footnote reference
    # interrupting a sentence), and the later group opens on a lower-case word, which in this
    # register is always a continuation rather than the start of a paragraph. Display lines, the
    # masthead and signature blocks therefore survive untouched.
    joined = []
    for b in blocks:
        prev = joined[-1] if joined else ""
        cont = (prev and b[:1].islower() and not re.fullmatch(r"\d{1,3}\.", b)
                and not re.search(r"[.!?]$", prev)
                and not re.search(r"\(\d{1,3}\)[.,;]?$", prev))
        if cont:
            joined[-1] = prev + " " + b
        else:
            joined.append(b)
    t = "\n\n".join(joined)
    for a, b in _LIG: t = t.replace(a, b)
    for a, b in (("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'")):
        t = t.replace(a, b)
    return t + "\n"

def clean_cfr(raw: str, part: str, title_line: str) -> str:
    lines = raw.splitlines()
    start = next(i for i, l in enumerate(lines) if re.match(r"^PART %s" % part, l))
    body = lines[start + 1:]
    def art(s):
        if re.match(r"^page \d+ of \d+$", s): return True
        if s.endswith("(enhanced display)"): return True
        if re.match(r"^15 CFR Part %s \(" % part, s): return True
        if re.match(r"^15 CFR %s\." % part, s): return True
        if s == "This content is from the eCFR and is authoritative but unofficial.": return True
        if s.startswith("Deep Seabed Mining Regulations for"): return True
        if re.match(r"^(Title 15|Subtitle B|Chapter IX|Subchapter D)\b", s): return True
        if s in ("EXPLORATION LICENSES", "COMMERCIAL RECOVERY PERMITS"): return True
        return False
    kept = [s.strip() for s in body if s.strip() and not art(s.strip())]
    SEC = re.compile(r"^§\s*(%s\.\d+)\s*(.*)$" % part); SUB = re.compile(r"^Subpart\s+[A-Z]")
    paras = []; cur = None; i = 0; n = len(kept)
    while i < n:
        s = kept[i]; m = SEC.match(s)
        if m:
            title = m.group(2).strip()
            if not title and i + 1 < n and not SEC.match(kept[i + 1]) and not SUB.match(kept[i + 1]):
                title = kept[i + 1]; i += 1
            if cur: paras.append(cur)
            cur = ("Section %s. %s" % (m.group(1), title)).strip().rstrip(".") + "."
        elif SUB.match(s) or s.startswith("Authority:") or s.startswith("Source:"):
            if cur: paras.append(cur)
            cur = s
        elif re.match(r"^\([a-z0-9]{1,3}\)\s", s) or re.match(r"^\(\d{1,2}\)\s", s):
            if cur: paras.append(cur)
            cur = s
        else:
            cur = (cur + " " + s) if cur else s
        i += 1
    if cur: paras.append(cur)
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]
    return title_line + "\n\n" + "\n\n".join(paras) + "\n"

_DRAFT_HDR = re.compile(r"^(Part|Regulation|Schedule|Annex|Appendix|Section)\s+([0-9]+|[IVXLCDM]+)(\s+bis)?\s*$")
_DRAFT_HDRT = re.compile(r"^(Part|Regulation|Schedule|Annex|Appendix|Section)\s+([0-9]+|[IVXLCDM]+)(\s+bis)?\s+(.+)$")
_DRAFT_NUM = re.compile(r"^\d{1,2}\.(\s+bis)?\s")
_DRAFT_LET = re.compile(r"^\([a-z0-9]{1,4}\)\s")


def _assemble_draft(lines, title_line: str, is_artefact) -> str:
    """Shared paragraph assembly for the exploitation-code drafts (PDF path and Word path).

    One function, not two, because the two sources must produce the SAME text conventions:
    a heading merged with its title line, one item per numbered paragraph, whitespace collapsed
    within a paragraph. It also means a change here moves BOTH records' hashes together, which is
    the honest behaviour - they are the same instrument in two dated states.
    """
    kept = [s.strip() for s in lines if s.strip() and not is_artefact(s.strip())]
    paras = []; cur = None; i = 0; n = len(kept)
    while i < n:
        s = kept[i]; mh = _DRAFT_HDR.match(s)
        if mh:
            title = ""
            if (i + 1 < n and not _DRAFT_HDR.match(kept[i + 1]) and not _DRAFT_HDRT.match(kept[i + 1])
                    and not _DRAFT_NUM.match(kept[i + 1]) and not _DRAFT_LET.match(kept[i + 1])
                    and len(kept[i + 1]) < 90):
                title = kept[i + 1]; i += 1
            if cur: paras.append(cur)
            cur = (s + (". " + title if title else "")).strip()
        elif _DRAFT_HDRT.match(s):
            if cur: paras.append(cur)
            cur = s
        elif _DRAFT_NUM.match(s) or _DRAFT_LET.match(s):
            if cur: paras.append(cur)
            cur = s
        else:
            cur = (cur + " " + s) if cur else s
        i += 1
    if cur: paras.append(cur)
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]
    return title_line + "\n\n" + "\n\n".join(paras) + "\n"


def clean_draft(raw: str, title_line: str) -> str:
    """The 23 December 2025 draft, from the ISA's PDF whose text layer carries no tracked changes."""
    lines = raw.splitlines()
    # body starts at the operative Preamble (after the ~14-page front matter / TOC)
    start = next(i for i, l in enumerate(lines) if l.strip() == "Preamble" and i > 480)
    def art(s):
        if re.match(r"^\d{1,3} of 194$", s): return True
        if s == "ISBA/31/C/CRP.2": return True
        if re.search(r"\.{6,}\s*\d+$", s): return True
        return False
    return _assemble_draft(lines[start:], title_line, art)


# ---- the tracked-changes Word form (issue #15) -----------------------------------------------
# THE PROBLEM THIS SOLVES. A marked-up revision sets its changes apart by FORMATTING - insertions
# underlined or boxed, deletions left in place struck through - so the PDF's text layer carries the
# OLD AND THE NEW wording fused together. At Regulation 1 the paragraph numbers come back as "4.",
# "[45.", "56.", "67.", "[78.", "89." (old number, new number, one token) and a cross-reference as
# "Subject to paragraph 1 and 3the Schedule". Storing that as text.txt would assert deleted wording
# as operative draft language and mint numbers the document does not use - and no gate could catch
# it, because the committed extractor would re-derive the same corruption byte-for-byte forever.
#
# THE FIX. The ISA publishes the same revision as a Word document in which the changes are
# MACHINE-READABLE (w:ins / w:del). The text is therefore derived from that part of the official
# record: insertions kept, deletions dropped, tracked changes resolved deterministically by
# committed code from a byte-exact preserved original.docx - Word's own "accept all changes",
# with nothing substituted in a deletion's place (the measured reason why is in
# _docx_paragraph_text). Comment bodies (word/comments.xml), footnotes and endnotes are separate
# zip parts, so they are absent by construction rather than by a filter that could miss one.
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx_paragraph_text(p) -> str:
    """One Word paragraph with the tracked changes RESOLVED. Insertions kept, deletions dropped.

    NOTHING IS SUBSTITUTED FOR A DELETION, and that is a measured decision, not a default. Putting
    a space where a deletion sat is tempting (the mark-up sometimes carries the space away with it,
    leaving "]for" where the ISA's own earlier clean text reads "] for"), but the same rule SPLITS
    WORDS: in 558 paragraphs the deletion sits INSIDE a word - "(a)" + deleted "t" + "he principle"
    - so a space there yields "(a) t he principle", and renumbering "4" + deleted "5" + "." yields
    "4 .", which stops the paragraph from reading as a numbered item at all. Deleting and
    substituting nothing is what Word's own "accept all changes" does, and it is the only rule of
    the three that never corrupts a word.
    """
    out = []

    def rec(el):
        for c in el:
            t = c.tag
            if t == _W + "del":          # struck-out wording: dropped whole
                continue
            if t == _W + "delText":      # only reached outside a w:del wrapper
                continue
            if t == _W + "t":
                out.append(c.text or "")
            elif t == _W + "tab":
                out.append("\t")
            elif t in (_W + "br", _W + "cr"):
                out.append("\n")
            else:
                rec(c)

    rec(p)
    return "".join(out)


def docx_paragraph_lines(path: str) -> list[str]:
    """Every Word paragraph, in document order; a table contributes its cells' paragraphs.

    THE COMMENTARY BOXES ARE EXCLUDED BY STRUCTURE, NOT BY GUESSWORK. Rev.3 carries 160 boxes of
    secretariat and working-group commentary ("Comments / It is proposed…", "Action:…",
    "Rev.3 - Group submission (…)", "Rev 3 - Comments"). Every one of them is a table with a single
    row and a single cell, and they sit inline among the provisions - so left in, they would be
    joined into the regulation they annotate and the stored text would present commentary as draft
    wording. Their count is reported in the record's provenance_note, so nothing disappears
    silently. Multi-cell tables are instrument text (the Schedule's definitions are one) and are kept.
    """
    import zipfile
    from xml.etree import ElementTree as ET
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    lines: list[str] = []

    def walk(el):
        for c in el:
            if c.tag == _W + "p":
                lines.append(_docx_paragraph_text(c))
            elif c.tag == _W + "tbl":
                rows = c.findall(_W + "tr")
                if len(rows) == 1 and len(rows[0].findall(_W + "tc")) == 1:
                    continue                      # a commentary box
                for row in rows:
                    for cell in row.findall(_W + "tc"):
                        walk(cell)
            else:
                walk(c)
    walk(root.find(_W + "body"))
    return lines


def clean_draft_docx(path: str, title_line: str) -> str:
    """Rev.3's text, resolved from the official Word form's tracked changes."""
    lines = docx_paragraph_lines(path)
    # The body starts at the Preamble that FOLLOWS the front matter's table of contents. Both
    # anchors are asserted rather than assumed: if either moves, this fails loudly instead of
    # quietly emitting the table of contents as if it were the instrument.
    toc = [i for i, l in enumerate(lines) if re.search(r"\t\d+$", l.strip())]
    if not toc:
        raise SystemExit("clean_draft_docx: no table of contents found — the slicing rule needs revisiting")
    start = next((i for i, l in enumerate(lines) if i > toc[-1] and l.strip() == "Preamble"), None)
    if start is None:
        raise SystemExit("clean_draft_docx: no body Preamble after the table of contents")

    def art(s):
        if re.match(r"^ISBA/\d", s): return True          # running document code
        if re.match(r"^\d{1,3} of \d+$", s): return True  # any page footer that reaches the XML
        if re.search(r"\t\d+$", s): return True           # any residual contents entry
        return False
    return _assemble_draft(lines[start:], title_line, art)



def clean_ao_fr(raw: str) -> str:
    m = re.search(r"AVIS CONSULTATIF\s*\nPrésents", raw); body = raw[m.start():]
    H1 = "responsabilités et obligations des etats dans le cadre"
    H2 = "d’activités menées dans la zone (avis consultatif du 1 février 2011)"
    kept = []
    for ln in body.split("\n"):
        s = ln.strip()
        if s == "\x0c" or s == "": kept.append(""); continue
        low = s.lower()
        if low == H1 or low == H2: continue
        if re.fullmatch(r"\d{1,3}", s): continue
        kept.append(s.replace("\x0c", ""))
    t = "\n".join(kept)
    for a, b in _LIG: t = t.replace(a, b)
    t = re.sub(r"[ \t]*\n[ \t]*", " ", t); t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r'(?<=[.\)\]»"”’:])\s+(\d{1,3}\.)\s+(?=[A-ZÀÂÉÈÊÎÏÔÙÛÜÇ«“"])', r"\n\n\1 ", t)
    paras = [p.strip() for p in t.split("\n\n") if p.strip()]
    title = ("Responsabilités et obligations des Etats qui patronnent des Personnes et des entités dans le "
             "cadre d’activités menées dans la Zone — Avis consultatif du 1er février 2011 (TIDM, Chambre "
             "pour le règlement des différends relatifs aux fonds marins, affaire n° 17)")
    return title + "\n\n" + "\n\n".join(paras) + "\n"

class AnchorNotFound(RuntimeError):
    """A cleaner's anchor line is absent from the extracted raw text.

    WHY THIS RAISES INSTEAD OF FALLING BACK. Each cleaner below slices the document at a line that
    marks the start of the annexed body (the preamble, or "Annexe"/"Anexo"/"Приложение"). Until
    2026-09-14 a missing anchor fell back silently to `body = lines`, i.e. the WHOLE document — so a
    shifted or re-rendered anchor produced a *different text* rather than an error, and the
    reproducibility gate reported a plain MISMATCH that pointed at the record instead of naming the
    cause. A silent fallback on a text-derivation path is the same defect class as a gate that passes
    when it cannot do its job: it converts "I could not find the anchor" into "the text is different",
    which is a much harder thing to diagnose and invites someone to "fix" the record.

    These anchors are extractor-version-sensitive by construction. The Chinese one is the most fragile
    of the four — a bare equality on 序言 with no confirming second line, unlike the fr/es/ru anchors
    which also require the following line to begin with a known phrase.
    """


def find_anchor(lines, predicate, anchor_desc, title_line):
    """Return the index of the line that begins the annexed body, or raise AnchorNotFound."""
    for i, line in enumerate(lines):
        if predicate(i, line):
            return i
    raise AnchorNotFound(
        f"anchor {anchor_desc} not found in the extracted text for {title_line[:70]!r}. "
        f"This recipe slices the document at that line; with it missing the WHOLE document would be "
        f"used instead, silently producing the wrong text. Most likely cause: the extractor rendered "
        f"the anchor differently (a different Poppler version can merge it with the following line, "
        f"or change its spacing). Check the pinned extractor version (extract.py prints it, and warns "
        f"when it differs) BEFORE regenerating any record."
    )


def clean_isa_fr(raw, title_line):
    lines=raw.splitlines()
    start=find_anchor(lines, lambda i,l: l.strip()=="Annexe" and i+1<len(lines)
                      and lines[i+1].strip().startswith("Règlement relatif"),
                      "'Annexe' followed by 'Règlement relatif'", title_line)
    body=lines[start+1:]
    def art(s):
        if re.match(r'^\d{2}-\d{5}$', s): return True
        if re.match(r'^\*\d+\*$', s): return True
        if re.match(r'^\d{6}$', s): return True
        if re.match(r'^ISBA/\S+$', s): return True
        if re.match(r'^\d{1,3}e?\s*séance', s): return True
        if re.match(r'^\d{1,2}\s+\w+\s+20\d\d$', s): return True
        if re.match(r'^_{3,}$', s): return True
        if re.match(r'^\d{1,2}\s+ISBA/', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        return False
    kept=[s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR=re.compile(r'^(Partie|Article|Section|Annexe|Appendice)\s+([0-9]+|premier|[IVXLC]+)\s*$')
    HDRT=re.compile(r'^(Partie|Article|Section|Annexe|Appendice)\s+([0-9]+|premier|[IVXLC]+)\s+(.+)$')
    STANDALONE=re.compile(r'^(Préambule|Introduction|Clauses types.*)$')
    NUM=re.compile(r'^\(?\d{1,2}\.(\s|$)|^\([a-z]{1,3}\)\s|^[a-z]\)\s')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not HDRT.match(kept[i+1]) and not NUM.match(kept[i+1]) and not STANDALONE.match(kept[i+1]) and len(kept[i+1])<95:
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=(s+(". "+title if title else "")).strip()
        elif HDRT.match(s) or STANDALONE.match(s):
            if cur: paras.append(cur)
            cur=s
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+" "+s) if cur else s
        i+=1
    if cur: paras.append(cur)
    paras=[re.sub(r'\s+',' ',p).strip() for p in paras if p.strip()]
    return title_line+"\n\n"+"\n\n".join(paras)+"\n"

def clean_agr_fr(raw, title_line):
    lines=raw.splitlines()
    start=next(i for i,l in enumerate(lines) if l.strip().startswith("ACCORD RELATIF À L"))
    body=lines[start:]
    def art(s):
        if re.match(r'^A/RES/\S+$', s): return True
        if re.match(r'^Page \d+$', s): return True
        if s=='/...': return True
        if re.match(r'^Vol\. ', s): return True
        if s in ("United Nations -","Nations Unies -","Treaty Series","Recueil des Traités","United Nations","Nations Unies"): return True
        if re.match(r'^\d{1,3}e séance', s): return True
        if re.match(r'^\d{1,2}\s+\w+\s+19\d\d$', s): return True
        if re.match(r'^\d{4}$', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        if re.match(r'^_{3,}$', s): return True
        return False
    kept=[s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR=re.compile(r'^(Article)\s+(premier|\d+)\s*$'); HDRT=re.compile(r'^(Article)\s+(premier|\d+)\s+(.+)$')
    SEC=re.compile(r'^SECTION\s+\d+\.?\s*$'); SECT=re.compile(r'^SECTION\s+\d+\.\s+(.+)$')
    NUM=re.compile(r'^\(?\d{1,2}\.(\s|$)|^\([a-z]\)\s|^[a-z]\)\s')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s) or SEC.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not SEC.match(kept[i+1]) and not NUM.match(kept[i+1]) and len(kept[i+1])<95 and not kept[i+1].endswith(':'):
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=(s+(". "+title if title else "")).strip()
        elif HDRT.match(s) or SECT.match(s):
            if cur: paras.append(cur)
            cur=s
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+" "+s) if cur else s
        i+=1
    if cur: paras.append(cur)
    paras=[re.sub(r'\s+',' ',p).strip() for p in paras if p.strip()]
    return title_line+"\n\n"+"\n\n".join(paras)+"\n"

def clean_isa_es(raw, title_line):
    lines=raw.splitlines()
    start=find_anchor(lines, lambda i,l: l.strip()=="Anexo" and i+1<len(lines)
                      and lines[i+1].strip().startswith("Reglamento sobre"),
                      "'Anexo' followed by 'Reglamento sobre'", title_line)
    body=lines[start+1:]
    def art(s):
        if re.match(r'^\d{2}-\d{5}(\s|$)', s): return True
        if re.match(r'^\*\d+\*$', s): return True
        if re.match(r'^\d{6}$', s): return True
        if re.match(r'^ISBA/\S+$', s): return True
        if re.match(r'^\d{1,3}[ªaºo]?\.?\s*sesión', s): return True
        if re.match(r'^\d{1,2}\s+de\s+\w+\s+de\s+20\d\d$', s): return True
        if re.match(r'^_{3,}$', s): return True
        if re.match(r'^\d{1,2}\s+ISBA/', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        return False
    kept=[s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR=re.compile(r'^(Parte|Artículo|Sección|Cláusula|Anexo|Apéndice)\s+([0-9]+|[IVXLC]+)\s*$')
    HDRT=re.compile(r'^(Parte|Artículo|Sección|Cláusula|Anexo|Apéndice)\s+([0-9]+|[IVXLC]+)\s+(.+)$')
    STANDALONE=re.compile(r'^(Preámbulo|Introducción|Cláusulas uniformes.*)$')
    NUM=re.compile(r'^\(?\d{1,2}(\.\d{1,2})?\.?(\s|$)|^\([a-z]{1,3}\)\s|^[a-z]\)\s')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not HDRT.match(kept[i+1]) and not NUM.match(kept[i+1]) and not STANDALONE.match(kept[i+1]) and len(kept[i+1])<95:
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=(s+(". "+title if title else "")).strip()
        elif HDRT.match(s) or STANDALONE.match(s):
            if cur: paras.append(cur)
            cur=s
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+" "+s) if cur else s
        i+=1
    if cur: paras.append(cur)
    paras=[re.sub(r'\s+',' ',p).strip() for p in paras if p.strip()]
    return title_line+"\n\n"+"\n\n".join(paras)+"\n"

def clean_agr_es(raw, title_line):
    lines=raw.splitlines()
    start=next(i for i,l in enumerate(lines) if l.strip().startswith("ACUERDO RELATIVO A LA APLICACIÓN"))
    body=lines[start:]
    def art(s):
        if re.match(r'^A/RES/\S+$', s): return True
        if re.match(r'^Página \d+$', s): return True
        if s=='/...': return True
        if re.match(r'^Vol\. ', s): return True
        if s in ("United Nations -","Nations Unies -","Treaty Series","Recueil des Traités","United Nations","Nations Unies"): return True
        if re.match(r'^\d{1,3}[ªaºo]?\.?\s*sesión', s): return True
        if re.match(r'^\d{1,2}\s+de\s+\w+\s+de\s+19\d\d$', s): return True
        if re.match(r'^\d{4}$', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        if re.match(r'^_{3,}$', s): return True
        return False
    kept=[s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR=re.compile(r'^(Artículo)\s+\d+\s*$'); HDRT=re.compile(r'^(Artículo)\s+\d+\s+(.+)$')
    SEC=re.compile(r'^SECCIÓN\s+\d+\.?\s*$'); SECT=re.compile(r'^SECCIÓN\s+\d+\.\s+(.+)$')
    NUM=re.compile(r'^\(?\d{1,2}\.(\s|$)|^\([a-z]\)\s|^[a-z]\)\s')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s) or SEC.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not SEC.match(kept[i+1]) and not NUM.match(kept[i+1]) and len(kept[i+1])<95 and not kept[i+1].endswith(':'):
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=(s+(". "+title if title else "")).strip()
        elif HDRT.match(s) or SECT.match(s):
            if cur: paras.append(cur)
            cur=s
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+" "+s) if cur else s
        i+=1
    if cur: paras.append(cur)
    paras=[re.sub(r'\s+',' ',p).strip() for p in paras if p.strip()]
    return title_line+"\n\n"+"\n\n".join(paras)+"\n"

CJK='一-鿿'

def clean_isa_ru(raw, title_line):
    lines=raw.splitlines()
    start=find_anchor(lines, lambda i,l: l.strip()=="Приложение" and i+1<len(lines)
                      and lines[i+1].strip().startswith("Правила поиска"),
                      "'Приложение' followed by 'Правила поиска'", title_line)
    body=lines[start+1:]
    def art(s):
        if re.match(r'^\d{2}-\d{5}(\s|$)', s): return True
        if re.match(r'^\*\d+\*$', s): return True
        if re.match(r'^\d{6}$', s): return True
        if re.match(r'^ISBA/\S+$', s): return True
        if re.match(r'^\d{1,3}-?е?\s*заседание', s): return True
        if re.match(r'^\d{1,2}\s+\w+\s+20\d\d\s+года', s): return True
        if re.match(r'^_{3,}$', s): return True
        if re.match(r'^\d{1,2}\s+ISBA/', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        return False
    kept=[s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR=re.compile(r'^(Часть|Правило|Раздел|Приложение|Добавление)\s+([0-9]+|[IVXLC]+)\s*$')
    HDRT=re.compile(r'^(Часть|Правило|Раздел|Приложение|Добавление)\s+([0-9]+|[IVXLC]+)\s+(.+)$')
    STANDALONE=re.compile(r'^(Преамбула|Введение|Стандартные условия.*)$')
    NUM=re.compile(r'^\(?\d{1,2}(\.\d{1,2})?\.?(\s|$)|^\([a-zа-я]{1,3}\)\s|^[a-zа-я]\)\s')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not HDRT.match(kept[i+1]) and not NUM.match(kept[i+1]) and not STANDALONE.match(kept[i+1]) and len(kept[i+1])<95:
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=(s+(". "+title if title else "")).strip()
        elif HDRT.match(s) or STANDALONE.match(s):
            if cur: paras.append(cur)
            cur=s
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+" "+s) if cur else s
        i+=1
    if cur: paras.append(cur)
    paras=[re.sub(r'\s+',' ',p).strip() for p in paras if p.strip()]
    return title_line+"\n\n"+"\n\n".join(paras)+"\n"

def clean_isa_zh(raw, title_line):
    lines=raw.splitlines()
    # preamble marks the start of the annexed Regulations body. NOTE: this is the most fragile of the
    # four anchors - a bare equality on the heading with no confirming second line, unlike fr/es/ru.
    # If it ever fails to match, find_anchor raises rather than silently keeping the whole document.
    start=find_anchor(lines, lambda i,l: l.strip()=="序言" and i>0, "'序言' on its own line",
                      title_line)
    body=lines[start:]
    def art(s):
        if re.match(r'^\d{2}-\d{5}(\s|$)', s): return True
        if re.match(r'^\*\d+\*$', s): return True
        if re.match(r'^ISBA/\S+$', s): return True
        if re.match(r'^第\s?\d{1,4}\s?次会议$', s): return True
        if re.match(r'^20\d\d\s*年', s): return True
        if re.match(r'^\d{1,2}\s+ISBA/', s): return True
        if re.fullmatch(r'\d{1,3}', s): return True
        if re.match(r'^_{3,}$', s): return True
        return False
    kept=[re.sub(r'\s+',' ',s.strip()) for s in body if s.strip() and not art(s.strip())]
    def norm_hdr(s): return re.sub(r'^第\s?(\d+)\s?条', r'第\1条', s)
    HDR=re.compile(r'^第\s?\d{1,3}\s?条$'); HDRT=re.compile(r'^第\s?\d{1,3}\s?条\s+(.+)$')
    PART=re.compile(r'^第[一二三四五六七八九十]+部分$')
    ANX=re.compile(r'^(附件[一二三四五六七八九十]?|附录[一二三四五六七八九十]?)$')
    STAND=re.compile(r'^(序言|导言|标准条款.*)$')
    NUM=re.compile(r'^\(?\d{1,2}(\.\d{1,2})?\.?(\s|$)|^（[一二三四五六七八九十]+）|^\([a-z]\)|^[a-z]\)')
    paras=[]; cur=None; i=0; n=len(kept)
    while i<n:
        s=kept[i]
        if HDR.match(s):
            title=""
            if i+1<n and not HDR.match(kept[i+1]) and not PART.match(kept[i+1]) and not NUM.match(kept[i+1]) and len(kept[i+1])<40:
                title=kept[i+1]; i+=1
            if cur: paras.append(cur)
            cur=norm_hdr(s)+(" "+title if title else "")
        elif HDRT.match(s) or PART.match(s) or ANX.match(s) or STAND.match(s):
            if cur: paras.append(cur)
            cur=norm_hdr(s)
        elif NUM.match(s):
            if cur: paras.append(cur)
            cur=s
        else:
            cur=(cur+s) if cur else s     # CJK: join WITHOUT spaces
        i+=1
    if cur: paras.append(cur)
    out=[]
    for p in paras:
        p=re.sub(r'(?<=['+CJK+r'])\s+(?=['+CJK+r'])','',p)   # drop spaces between CJK chars
        p=re.sub(r'\s+',' ',p).strip()
        if p: out.append(p)
    return title_line+"\n\n"+"\n\n".join(out)+"\n"

def clean_unclos(raw, title_line, lang):
    """UNCLOS Part XI (arts 133-191) from the EUR-Lex OJ PDF (pdftotext -raw). Slices Part XI,
    strips OJ running heads, de-hyphenates soft wraps, rebuilds Part/Section/Sub-section/Article
    structure. NFC-normalised so combining-diacritic running heads match and output is canonical."""
    raw = unicodedata.normalize('NFC', raw)
    partw = "PARTIE" if lang == "fr" else "PARTE"
    secw  = "SECTION" if lang == "fr" else "SECCIÓN"
    subw  = "Sous-section" if lang == "fr" else "Subsección"
    artw  = "Article" if lang == "fr" else "Artículo"
    L = raw.splitlines()
    a133 = next(i for i, l in enumerate(L) if l.strip() == f"{artw} 133")
    pxi  = max(i for i, l in enumerate(L[:a133]) if l.strip() == f"{partw} XI")
    a191 = next(i for i, l in enumerate(L) if l.strip() == f"{artw} 191")
    pxii = next(i for i, l in enumerate(L[a191:], a191) if l.strip() == f"{partw} XII")
    seg = L[pxi:pxii]
    def furn(x):
        x = x.strip()
        return (bool(re.match(r'^L \d+/\d+', x)) or 'Journal officiel' in x or 'Diario Oficial' in x
                or bool(re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{2}', x)) or bool(re.fullmatch(r'(FR|ES)', x)) or x == '')
    lines = [l.rstrip() for l in seg if not furn(l)]
    ART = re.compile(rf'^{artw} (\d+)$'); SEC = re.compile(rf'^{secw} (\d+)$')
    SUB = re.compile(rf'^{subw} ([A-Z])$'); PART = re.compile(rf'^{partw} XI$')
    NEW = re.compile(r'^(\d+\.|[a-z]\)|[ivx]+\))(\s|$)')
    paras = []; cur = None
    def flush():
        nonlocal cur
        if cur is not None: paras.append(cur); cur = None
    i = 0; n = len(lines)
    while i < n:
        s0 = lines[i]
        mA = ART.match(s0); mS = SEC.match(s0); mU = SUB.match(s0); mP = PART.match(s0)
        if mP:
            flush(); t = lines[i+1] if i+1 < n else ""; i += 1; paras.append(f"{partw} XI. {t}")
        elif mS:
            flush(); t = lines[i+1] if i+1 < n else ""; i += 1; paras.append(f"{secw} {mS.group(1)}. {t}")
        elif mU:
            flush(); t = lines[i+1] if i+1 < n else ""; i += 1; paras.append(f"{subw} {mU.group(1)}. {t}")
        elif mA:
            flush(); t = lines[i+1] if i+1 < n else ""; i += 1; paras.append(f"{artw} {mA.group(1)}. {t}")
        elif NEW.match(s0):
            flush(); cur = s0
        else:
            if cur is None: cur = s0
            elif cur.endswith('-') and cur[-2:-1].islower(): cur = cur[:-1] + s0
            else: cur = cur + " " + s0
        i += 1
    flush()
    return title_line + "\n\n" + "\n\n".join(paras) + "\n"

PDF_RAW = {"un/convention/unclos-partxi-1982-fr", "un/convention/unclos-partxi-1982-es"}
# Records whose text must be read with the printed layout preserved, not in the default reading order.
PDF_LAYOUT = {"ton/statute/seabed-minerals-act-2014"}

# ---- registry: corpus_id -> how to re-derive text from original.* ----------------------------
PDF_EXTRACTORS = {
  "itlos/advisory-opinion/sdc-area-2011": lambda raw: clean_ao(raw),
  "itlos/advisory-opinion/sdc-area-2011-fr": lambda raw: clean_ao_fr(raw),
  "un/agreement/unclos-partxi-impl-1994-fr": lambda raw: clean_agr_fr(raw,
      "Accord relatif à l’application de la partie XI de la Convention des Nations Unies sur le droit de la mer du 10 décembre 1982 [FR]"),
  "isa/regulation/nodules-2013-fr": lambda raw: clean_isa_fr(raw,
      "Règlement relatif à la prospection et à l’exploration des nodules polymétalliques dans la Zone (tel que modifié en 2013) — ISBA/19/C/17, annexe [FR]"),
  "isa/regulation/sulphides-2010-fr": lambda raw: clean_isa_fr(raw,
      "Règlement relatif à la prospection et à l’exploration des sulfures polymétalliques dans la Zone — ISBA/16/A/12/Rev.1, annexe [FR]"),
  "isa/regulation/crusts-2012-fr": lambda raw: clean_isa_fr(raw,
      "Règlement relatif à la prospection et à l’exploration des encroûtements cobaltifères de ferromanganèse dans la Zone — ISBA/18/A/11, annexe [FR]"),
  "un/agreement/unclos-partxi-impl-1994-es": lambda raw: clean_agr_es(raw,
      "Acuerdo relativo a la aplicación de la Parte XI de la Convención de las Naciones Unidas sobre el Derecho del Mar de 10 de diciembre de 1982 [ES]"),
  "isa/regulation/nodules-2013-es": lambda raw: clean_isa_es(raw,
      "Reglamento sobre Prospección y Exploración de Nódulos Polimetálicos en la Zona (en su forma enmendada en 2013) — ISBA/19/C/17, anexo [ES]"),
  "isa/regulation/sulphides-2010-es": lambda raw: clean_isa_es(raw,
      "Reglamento sobre Prospección y Exploración de Sulfuros Polimetálicos en la Zona — ISBA/16/A/12/Rev.1, anexo [ES]"),
  "isa/regulation/crusts-2012-es": lambda raw: clean_isa_es(raw,
      "Reglamento sobre Prospección y Exploración de Costras de Ferromanganeso con Alto Contenido de Cobalto en la Zona — ISBA/18/A/11, anexo [ES]"),
  "isa/regulation/nodules-2013-ru": lambda raw: clean_isa_ru(raw, "Правила поиска и разведки полиметаллических конкреций в Районе (с поправками 2013 года) — ISBA/19/C/17, приложение [RU]"),
  "isa/regulation/sulphides-2010-ru": lambda raw: clean_isa_ru(raw, "Правила поиска и разведки полиметаллических сульфидов в Районе — ISBA/16/A/12/Rev.1, приложение [RU]"),
  "isa/regulation/crusts-2012-ru": lambda raw: clean_isa_ru(raw, "Правила поиска и разведки кобальтоносных железомарганцевых корок в Районе — ISBA/18/A/11, приложение [RU]"),
  "isa/regulation/nodules-2013-zh": lambda raw: clean_isa_zh(raw, "“区域”内多金属结核探矿和勘探规章（2013年修正） — ISBA/19/C/17，附件 [ZH]"),
  "isa/regulation/sulphides-2010-zh": lambda raw: clean_isa_zh(raw, "“区域”内多金属硫化物探矿和勘探规章 — ISBA/16/A/12/Rev.1，附件 [ZH]"),
  "isa/regulation/crusts-2012-zh": lambda raw: clean_isa_zh(raw, "“区域”内富钴铁锰结壳探矿和勘探规章 — ISBA/18/A/11，附件 [ZH]"),
  "un/convention/unclos-partxi-1982-fr": lambda raw: clean_unclos(raw, "Convention des Nations Unies sur le droit de la mer — Partie XI : La Zone (articles 133 à 191)", "fr"),
  "un/convention/unclos-partxi-1982-es": lambda raw: clean_unclos(raw, "Convención de las Naciones Unidas sobre el Derecho del Mar — Parte XI: La Zona (artículos 133 a 191)", "es"),
  "usa/regulation/cfr15-970-2026": lambda raw: clean_cfr(raw, "970",
      "15 CFR Part 970 — Deep Seabed Mining Regulations for Exploration Licenses (up to date as of 1 July 2026)"),
  "usa/regulation/cfr15-971-2026": lambda raw: clean_cfr(raw, "971",
      "15 CFR Part 971 — Deep Seabed Mining Regulations for Commercial Recovery Permits (up to date as of 1 July 2026)"),
  "isa/draft/exploitation-code-2025": lambda raw:
      clean_draft(raw, "Draft Regulations on Exploitation of Mineral Resources in the Area — "
                       "Further Revised Consolidated Text (ISBA/31/C/CRP.2, 23 December 2025) [DRAFT, NOT IN FORCE]"),
  # ITLOS born-digital documents (issue #9). The Tribunal's own text layer, no OCR anywhere, so
  # these are reproducible from the committed extractor under the pinned toolchain - which is why
  # the three scan-based ITLOS orders are absent from this registry and declared excluded instead.
  "itlos/order/case34-order-18jul2026": lambda raw: clean_itlos_text_layer(raw, r"SEABED DISPUTES CHAMBER OF THE"),
  "itlos/order/case35-order-18jul2026": lambda raw: clean_itlos_text_layer(raw, r"SEABED DISPUTES CHAMBER OF THE"),
  "itlos/declaration/case34-35-kittichaisaree-18jul2026":
      lambda raw: clean_itlos_text_layer(raw, r"DECLARATION OF JUDGE KITTICHAISAREE"),
  "itlos/declaration/case34-brown-18jul2026": lambda raw: clean_itlos_text_layer(raw, r"DECLARATION OF JUDGE BROWN"),
  "itlos/declaration/case35-brown-18jul2026": lambda raw: clean_itlos_text_layer(raw, r"DECLARATION OF JUDGE BROWN"),
  "nru/statute/international-seabed-minerals-act-2015": lambda raw: clean_nru_ism_2015(raw, TITLE_NRU_ISM),
  "nru/statute/seabed-minerals-authority-act-2024": lambda raw: clean_nru_ronlaw(raw, TITLE_NRU_SBMA, _NRU_FIRST_PART),
  "nru/regulation/seabed-minerals-authority-regulations-2025": lambda raw: clean_nru_ronlaw(
      raw, TITLE_NRU_REGS, _NRU_FIRST_PART, stop_at=_NRU_SCHEDULE),
  "ton/statute/seabed-minerals-act-2014": lambda raw: clean_ton_sma_2014(raw, TITLE_TON_SMA),
  }

# ---- sponsoring-State national law (issue #13) ------------------------------------------------
# The title line of each national record, in the same form the extraction convention uses: what the
# instrument is, its own number and date, and the status a reader must not have to guess at.
TITLE_NRU_ISM = ("International Seabed Minerals Act 2015 (No. 26 of 2015, certified 23 October 2015) "
                 "— Republic of Nauru [REPEALED by the Nauru Seabed Minerals Authority Act 2024, s.70]")
TITLE_NRU_SBMA = ("Nauru Seabed Minerals Authority Act 2024 (No. 13 of 2024) — Republic of Nauru "
                  "[consolidated service copy of the official text, RONLAW]")
TITLE_NRU_REGS = ("Nauru Seabed Minerals Authority Regulations 2025 (SL No. 32 of 2025, notified "
                  "22 June 2025) — Republic of Nauru")
TITLE_TON_SMA = ("Seabed Minerals Act 2014 (Act 10 of 2014) — Kingdom of Tonga, 2020 Revised Edition "
                 "(CAP 20.07)")

# ---- sponsoring-State national statutes and regulations (issue #13) --------------------------
# Four born-digital official PDFs: Nauru's own register copies (RONLAW service copies, as submitted
# by Nauru to the ISA) and Tonga's 2016 Revised Edition. Their page furniture is POSITIONAL -
# running heads, a marginal "Section" column, RONLAW service stamps, printed page numbers - and in
# the Nauru documents the page number is a BARE NUMBER that looks exactly like a section number.
# It is removed by name and by its own page sequence, never by guessing at prose, and a registration
# in PDF_EXTRACTORS below fails loudly if a document stops matching its shape.
def _pages(raw: str) -> list:
    """pdftotext's page chunks: the extractor calls it without -nopgbrk, so \f separates pages."""
    return raw.split("\f")


_NRU_FURN = re.compile(
    r"^(LAWS OF THE REPUBLIC OF NAURU|Service \d+|Section|Table of Provisions|Table of Contents|"
    r"Table of Amendments|Principal|Job: .*|Page: \d+ Date: .*|bwpageid::.*|bwservice::.*|"
    r"\[The next page is [\d,]+\]|\d{3},\d{3}|s \d+[A-Z]?|Nauru Seabed Minerals Authority "
    r"(Act 2024|Regulations 2025)|NAURU SEABED MINERALS AUTHORITY (ACT 2024|REGULATIONS 2025))$")

# Furniture by NAME. The last three alternatives matter: `-layout` prints the two running heads on ONE
# line (in either order), and the AGO's 2020 Revised Edition drops the year from the instrument name
# ("Seabed Minerals Act") - so the name and the edition year are both optional here.
_TON_FURN = re.compile(
    r"^(C|T|to|Page \d+|CAP \d+\.\d+( Section \d+)?|Section \d+ to|Seabed Minerals Act( 2014(A1)?)?|"
    r"SEABED MINERALS ACT( 2014(A1)?)?|\d{4} Revised Edition|Endnotes|Act \d+ of 2014"
    r"|Seabed Minerals Act( 2014)?\s+CAP \d+\.\d+ (Section \d+|Arrangement of Sections|Endnotes)"
    r"|Section \d+ CAP \d+\.\d+\s+Seabed Minerals Act( 2014)?)$")
def _assemble_numbered(lines, title_line, part_re, stats=None, stop_at=None, inline_title=False):
    """Numbered sections: 'N' alone, the section title on the next line, then its body.

    A bare number counts as a section marker only when it continues the section sequence (a gap of
    one is allowed, for a section revoked or renumbered by an amendment). Any other bare number is
    page furniture: it is dropped and counted, never left in the text and never guessed at.

    `inline_title` covers a document that prints the number and the title on ONE line ('100 Duties
    on parties conducting Marine Scientific Research', Tonga's 2016 Revised Edition, where the margin
    block puts them together): same sequence rule, and the title comes off the same line. A line that
    merely begins with a number is ordinary text unless it continues the sequence - only a BARE number
    is ever dropped as furniture, because dropping a line of prose would lose wording.

    `stop_at` is where the numbered body ends and non-sectioned material begins (a SCHEDULE). From
    that heading on, the printed line breaks are kept as paragraph breaks and no bare number is read
    as a section - a form's own item numbers carry on the section sequence, so item '64' in Schedule 3
    of the Nauru SBMA Regulations 2025 minted a Section 64 that does not exist. Everything after the
    heading is retained, as printed: a schedule is part of the instrument, not apparatus.
    """
    paras, cur, expect, dropped = [], None, 1, []
    tail = 0
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if stop_at is not None and stop_at.match(s):
            if cur:
                paras.append(cur)
                cur = None
            for tail_line in lines[i:]:
                t = re.sub(r"\s+", " ", tail_line).strip()
                if t:
                    paras.append(t)
                    tail += 1
            break
        m = re.fullmatch(r"(\d{1,3})([A-Z]{0,2})", s)
        mi = re.match(r"^(\d{1,3})\s+(\S.*)$", s) if inline_title else None
        if m and expect <= int(m.group(1)) <= expect + 1:
            if cur: paras.append(cur)
            num, suff = int(m.group(1)), m.group(2)
            expect = num + 1
            title = lines[i + 1].strip() if i + 1 < n else ""
            cur = f"Section {num}{suff}. {title}".rstrip(" .") + "."
            i += 1
        elif mi and expect <= int(mi.group(1)) <= expect + 1:
            if cur: paras.append(cur)
            expect = int(mi.group(1)) + 1
            cur = f"Section {mi.group(1)}. {mi.group(2).strip()}"
        elif part_re.match(s):
            if cur: paras.append(cur); cur = None
            paras.append(s)
        elif re.fullmatch(r"\d{1,3}", s):
            dropped.append(int(s))
        else:
            cur = (cur + " " + s) if cur else s
        i += 1
    if cur: paras.append(cur)
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]
    if stats is not None:
        stats["sections"] = expect - 1
        stats["bare_numbers_dropped"] = dropped
        if stop_at is not None:
            stats["schedule_paragraphs"] = tail
    return title_line + "\n\n" + "\n\n".join(paras) + "\n"
_NRU_SCHEDULE = re.compile(r"^SCHEDULE \d+ [—–-] .+$")
_NRU_PARTS = re.compile(r"^PART \d+ [—–-] .+$")
_TON_PARTS = re.compile(r"^PART (\d+|[IVX]+) [—–-] .+$")
_NRU_FIRST_PART = re.compile(r"^PART 1 [—–-] PRELIMINARY$")
_TON_FIRST_PART = re.compile(r"^PART (1|I) [—–-] PRELIMINARY$")


def _body_start(lines, first_part_re):
    """The Act's body starts at its FIRST Part heading - the last such line, the TOC being above."""
    idx = [i for i, l in enumerate(lines) if first_part_re.match(l)]
    if not idx:
        raise SystemExit("national-law extractor: first Part heading not found — shape changed")
    return idx[-1]


def clean_nru_ism_2015(raw, title_line, stats=None):
    """Nauru International Seabed Minerals Act 2015 (No. 26 of 2015, certified 23 Oct 2015).

    Its only page furniture is the printed page number, standing alone as the last line of its page.
    It is dropped only when it is the NEXT number in the printed sequence, so no section number can
    be mistaken for it; the sequence is recorded in stats.
    """
    lines, expect, dropped = [], 1, []
    for ci, page in enumerate(_pages(raw)):
        L = [l.strip() for l in page.splitlines() if l.strip()]
        if ci >= 4 and L and re.fullmatch(r"\d{1,3}", L[-1]) and int(L[-1]) == expect:
            dropped.append(expect)
            expect += 1
            L = L[:-1]
        lines.extend(L)
    if stats is not None:
        stats["page_numbers"] = dropped
    return _assemble_numbered(lines[_body_start(lines, _NRU_FIRST_PART):], title_line, _NRU_PARTS, stats)


def clean_nru_ronlaw(raw, title_line, first_part_re, stats=None, stop_at=None):
    """RONLAW service copies (Nauru): the furniture is named - service stamps, marginal 'Section'
    column, running heads - so it is dropped by name and the body is assembled from the Part heading.
    The SBMA Regulations 2025 end in three SCHEDULEs of forms, so `stop_at` hands them to the
    assembler as non-sectioned material instead of letting a form's item numbers mint sections.
    """
    lines = [l.strip() for page in _pages(raw) for l in page.splitlines()
             if l.strip() and not _NRU_FURN.match(l.strip())]
    return _assemble_numbered(lines[_body_start(lines, first_part_re):], title_line, _NRU_PARTS, stats,
                              stop_at=stop_at)


def clean_ton_sma_2014(raw, title_line, stats=None):
    """Tonga, Seabed Minerals Act 2014 - 2016 Revised Edition (CAP 46.05).

    The Revised Edition prints an Arrangement of Sections before the Act and the AGO's ENDNOTES
    (amendment history) after it: both are apparatus, and both are dropped. The Arrangement lists
    ENDNOTES as its own last entry, so the FIRST 'ENDNOTES' in the file sits in the front matter:
    cutting there discarded the entire Act and left the table of contents as the "text" (it read as
    'Section 1. 2. 3. ...' with a gap of two between every section). The Act's own endnotes heading
    is the LAST one, and that is where the cut belongs.

    This record is read with `-layout` (see PDF_LAYOUT) and that is not cosmetic. Its margin block
    typesets each section's number and title together, and the default reading order interleaves them
    wrongly: it emitted '9', then '10', then the title belonging to 9 - so a number/title pairing
    taken from the running order is not evidence. With the layout preserved, every section reads as
    'N  Title' on one line, hence `inline_title=True`; the body of each section stays on the lines
    below, indented as printed. Sections 1-99 and 100+ differ only in whether the number and title fit
    the line, not in structure, and the sequence rule treats both the same way.
    """
    lines = [l.strip() for page in _pages(raw) for l in page.splitlines()
             if l.strip() and not _TON_FURN.match(l.strip())]
    cut = [i for i, l in enumerate(lines) if l.upper() == "ENDNOTES"]
    if not cut:
        raise SystemExit("Tonga extractor: ENDNOTES heading not found — shape changed")
    lines = lines[:cut[-1]]
    return _assemble_numbered(lines[_body_start(lines, _TON_FIRST_PART):], title_line, _TON_PARTS, stats,
                              inline_title=True)


# ---- Word-form-sourced texts (issue #15) -----------------------------------------------------
# A record whose text is resolved from the official Word form keeps original_format: pdf, because
# the PDF is the artefact a reader opens and the citation anchor. The docx sits beside it as
# original.docx (recorded in capture_history with its own hash), and the text is derived from THAT.
# The generated text is therefore fully reproducible - the resolver is committed code and the docx
# is byte-exact - so no repro-policy.json exclusion is needed for it: the gate re-derives it and
# compares, like any other record. That is a strict improvement on "declare it excluded and move on".
TITLE_REV3 = ("Draft Regulations on Exploitation of Mineral Resources in the Area — Further Revised "
              "Consolidated Text (Revision 3, ISBA/31/C/CRP.1/Rev.3, 19 June 2026) [DRAFT, NOT IN FORCE]")
DOCX_EXTRACTORS = {
    "isa/draft/exploitation-code-2026": lambda p: clean_draft_docx(p, TITLE_REV3),
}

# ---- per-record toolchain attestation (issue #7, option (e)) ---------------------------------
# The global PINNED_POPPLER above is a statement about the PRESENT: the version NEW derivations are
# calibrated against. The reproducibility claim, though, is per record and HISTORICAL — "this dated
# text re-derives from that original" — and the toolchain is part of that claim. One constant cannot
# express "records 1–26 came from 22.02.0 and record 27 from 22.02.0-2ubuntu0.13", and moving it
# silently restates the claim for every historical record at once. The portable form is per record,
# in the same file convention space law already uses:
#
#     extraction/<corpus_id>/<version_id>.json   →   extractor: {tool, args, toolchain}
#
# AN ATTESTATION IS WRITTEN ONLY WHERE THE TEXT ACTUALLY RE-DERIVED BYTE-EXACT. Attesting a text that
# does not reproduce would be a false provenance claim, so the records that legitimately do not
# reproduce (the OCR-derived ITLOS orders, declared in repro-policy.json) get no file at all. That
# absence is itself informative and is reported by --attest and by the CI assertion.
ATTEST = os.path.join(REPO, "extraction")


def attestation_for(meta: dict, got: bytes, ver: str) -> dict:
    """The attestation record for one reproduced text: which toolchain re-derived it, and to what."""
    cid = meta["corpus_id"]
    if cid in DOCX_EXTRACTORS:
        import platform
        extractor = {"tool": "python-stdlib-docx-tracked",
                     "args": ["word/document.xml", "w:ins kept, w:del dropped"],
                     "toolchain": f"CPython {platform.python_version()}"}
    elif meta.get("original_format") == "pdf":
        args = (["-enc", "UTF-8"] + (["-raw"] if cid in PDF_RAW else [])
                + (["-layout"] if cid in PDF_LAYOUT else []))
        extractor = {"tool": "pdftotext", "args": args, "toolchain": f"poppler {ver}"}
    else:
        extractor = {"tool": "passthrough", "toolchain": None}
    return {
        "corpus_id": cid,
        "version_id": str(meta["version_id"]),
        "extractor": extractor,
        "text_sha256": "sha256:" + hashlib.sha256(got).hexdigest(),
        "note": ("Toolchain under which this record's text.txt re-derives, proven by scripts/extract.py. "
                 "Written only for records that reproduce byte-exact, and the hash beside it is the one "
                 "that re-derivation produced. The byte-exact original.* and its recorded sha256 remain "
                 "the authoritative anchor; this attests the DERIVATION, not the source."),
    }


def write_attestation(rec: dict) -> bool:
    """Write the attestation file only if it would actually change.

    A rebuild must not churn these. An attestation whose toolchain and text hash are unchanged is left
    exactly as it is — no date stamp, no rewrite — so the files stay stable and a real change to one of
    them means something. (A 'generated on' field here would make every run dirty for no gain, which is
    the trap that once left this portfolio's derived layer permanently modified.)
    """
    p = os.path.join(ATTEST, rec["corpus_id"], f"{rec['version_id']}.json")
    if os.path.isfile(p):
        try:
            if json.load(open(p, encoding="utf-8")) == rec:
                return False
        except Exception:
            pass
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return True


def rederive(meta: dict, d: str) -> bytes | None:
    """Return the reproduced text.txt bytes, or None if this record has no stored text."""
    if meta.get("authoritative_status") == "authoritative_missing" or not meta.get("text_sha256"):
        return None
    cid = meta["corpus_id"]; fmt = meta.get("original_format")
    if cid in DOCX_EXTRACTORS:
        # Word-form-sourced: the PDF's text layer fuses old and new wording, so the text is
        # resolved from the tracked changes in the official Word document beside it.
        return norm(DOCX_EXTRACTORS[cid](os.path.join(d, "original.docx")))
    if fmt == "pdf":
        fn = PDF_EXTRACTORS.get(cid)
        if not fn: raise SystemExit(f"no committed PDF extractor for {cid}")
        return norm(fn(pdftotext(os.path.join(d, meta["original_filename"]),
                                  raw=(cid in PDF_RAW), layout=(cid in PDF_LAYOUT))))
    # txt-sourced: canonical normalisation of the stored original (raw HTML capture was cleaned pre-ingest)
    return norm(open(os.path.join(d, meta["original_filename"]), encoding="utf-8").read())

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite text.txt from the extractor")
    ap.add_argument("--attest", action="store_true",
                    help="write/refresh per-record toolchain attestations under extraction/")
    args = ap.parse_args()
    ver = poppler_version()
    print(f"pdftotext (Poppler) {ver}" + ("" if ver == PINNED_POPPLER else f"  ⚠ pinned {PINNED_POPPLER} — PDF bytes may differ"))
    pdf_ok = pdf_tot = txt_ok = txt_tot = docx_ok = docx_tot = 0; fails = []
    att_new, att_same, att_no_extractor, att_nomatch = [], [], [], []
    for mp in sorted(glob.glob(os.path.join(AUTH, "**", "metadata.yaml"), recursive=True)):
        meta = yaml.safe_load(open(mp, encoding="utf-8")); d = os.path.dirname(mp)
        if meta.get("original_format") == "pdf" and meta["corpus_id"] not in PDF_EXTRACTORS \
                and meta["corpus_id"] not in DOCX_EXTRACTORS:
            # No committed extractor, so rederive() would SystemExit here — the defect that once
            # aborted a whole run on the first OCR-derived record. Skipped BY DESIGN, under --write as
            # well as --attest: there is no committed code to re-derive the text from, so there is
            # nothing to rewrite; and such a text gets NO attestation file, because committed,
            # deterministic code cannot re-derive it. The absence is the honest record.
            att_no_extractor.append(meta["corpus_id"]); continue
        got = rederive(meta, d)
        if got is None: continue
        is_docx = meta["corpus_id"] in DOCX_EXTRACTORS
        is_pdf = meta.get("original_format") == "pdf" and not is_docx
        if is_docx: docx_tot += 1
        elif is_pdf: pdf_tot += 1
        else: txt_tot += 1
        committed = re.fullmatch(r"sha256:[0-9a-f]{64}", str(meta.get("text_sha256") or ""))
        match = ("sha256:" + hashlib.sha256(got).hexdigest()) == meta["text_sha256"]
        # NEVER write over a committed text with one that does not reproduce it. Writing first and
        # comparing afterwards replaced the pinned-toolchain text of isa/regulation/sulphides-2010-zh
        # with a locally-derived variant on a box whose poppler was not the pin - caught only because
        # the mismatch was reported. A record with no committed hash (a new one) still writes; to
        # re-derive deliberately under a new pin, clear text_sha256 first and let this rewrite it.
        if args.write and (match or not committed):
            open(os.path.join(d, "text.txt"), "wb").write(got)
        if match:
            docx_ok += is_docx; pdf_ok += is_pdf; txt_ok += (not is_pdf and not is_docx)
        else:
            fails.append(meta["corpus_id"])
        if args.attest:
            if match:
                (att_new if write_attestation(attestation_for(meta, got, ver)) else att_same).append(meta["corpus_id"])
            else:
                att_nomatch.append(meta["corpus_id"])
    print(f"PDF-sourced reproduced byte-exact: {pdf_ok}/{pdf_tot}")
    print(f"txt-sourced reproduced (normaliser): {txt_ok}/{txt_tot}")
    if docx_tot:
        print(f"docx-sourced reproduced (tracked-changes resolver): {docx_ok}/{docx_tot}")
    if att_no_extractor:
        print(f"not re-derived, no committed extractor ({len(att_no_extractor)}, expected for the "
              f"declared OCR-derived records), left untouched: " + ", ".join(att_no_extractor))
    if args.attest:
        print(f"attestations written: {len(att_new)}   already correct: {len(att_same)}")
        print(f"NOT attested: {len(att_no_extractor)} without a committed extractor, "
              f"{len(att_nomatch)} that did not reproduce")
        if att_nomatch:
            print("  did NOT reproduce, so NOT attested: " + ", ".join(att_nomatch))
    if fails:
        print("DIFFERS: " + ", ".join(fails)); return 1
    print("RESULT: OK — every stored text re-derives from its committed original.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
