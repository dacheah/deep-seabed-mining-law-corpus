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
"""
from __future__ import annotations
import argparse, glob, hashlib, os, re, subprocess, sys
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH = os.path.join(REPO, "authoritative")
PINNED_POPPLER = "22.02.0"

def pdftotext(pdf: str) -> str:
    return subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"],
                          capture_output=True, text=True, check=True).stdout

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

def clean_draft(raw: str, title_line: str) -> str:
    lines = raw.splitlines()
    # body starts at the operative Preamble (after the ~14-page front matter / TOC)
    start = next(i for i, l in enumerate(lines) if l.strip() == "Preamble" and i > 480)
    body = lines[start:]
    def art(s):
        if re.match(r"^\d{1,3} of 194$", s): return True
        if s == "ISBA/31/C/CRP.2": return True
        if re.search(r"\.{6,}\s*\d+$", s): return True
        return False
    kept = [s.strip() for s in body if s.strip() and not art(s.strip())]
    HDR = re.compile(r"^(Part|Regulation|Schedule|Annex|Appendix|Section)\s+([0-9]+|[IVXLCDM]+)(\s+bis)?\s*$")
    HDRT = re.compile(r"^(Part|Regulation|Schedule|Annex|Appendix|Section)\s+([0-9]+|[IVXLCDM]+)(\s+bis)?\s+(.+)$")
    NUM = re.compile(r"^\d{1,2}\.(\s+bis)?\s"); LET = re.compile(r"^\([a-z0-9]{1,4}\)\s")
    paras = []; cur = None; i = 0; n = len(kept)
    while i < n:
        s = kept[i]; mh = HDR.match(s)
        if mh:
            title = ""
            if (i + 1 < n and not HDR.match(kept[i + 1]) and not HDRT.match(kept[i + 1])
                    and not NUM.match(kept[i + 1]) and not LET.match(kept[i + 1]) and len(kept[i + 1]) < 90):
                title = kept[i + 1]; i += 1
            if cur: paras.append(cur)
            cur = (s + (". " + title if title else "")).strip()
        elif HDRT.match(s):
            if cur: paras.append(cur)
            cur = s
        elif NUM.match(s) or LET.match(s):
            if cur: paras.append(cur)
            cur = s
        else:
            cur = (cur + " " + s) if cur else s
        i += 1
    if cur: paras.append(cur)
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]
    return title_line + "\n\n" + "\n\n".join(paras) + "\n"


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

def clean_isa_fr(raw, title_line):
    lines=raw.splitlines()
    start=None
    for i,l in enumerate(lines):
        if l.strip()=="Annexe" and i+1<len(lines) and lines[i+1].strip().startswith("Règlement relatif"):
            start=i; break
    body=lines[start+1:] if start is not None else lines
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
  "usa/regulation/cfr15-970-2026": lambda raw: clean_cfr(raw, "970",
      "15 CFR Part 970 — Deep Seabed Mining Regulations for Exploration Licenses (up to date as of 1 July 2026)"),
  "usa/regulation/cfr15-971-2026": lambda raw: clean_cfr(raw, "971",
      "15 CFR Part 971 — Deep Seabed Mining Regulations for Commercial Recovery Permits (up to date as of 1 July 2026)"),
  "isa/draft/exploitation-code-2025": lambda raw:
      clean_draft(raw, "Draft Regulations on Exploitation of Mineral Resources in the Area — "
                       "Further Revised Consolidated Text (ISBA/31/C/CRP.2, 23 December 2025) [DRAFT, NOT IN FORCE]"),
}

def rederive(meta: dict, d: str) -> bytes | None:
    """Return the reproduced text.txt bytes, or None if this record has no stored text."""
    if meta.get("authoritative_status") == "authoritative_missing" or not meta.get("text_sha256"):
        return None
    cid = meta["corpus_id"]; fmt = meta.get("original_format")
    if fmt == "pdf":
        fn = PDF_EXTRACTORS.get(cid)
        if not fn: raise SystemExit(f"no committed PDF extractor for {cid}")
        return norm(fn(pdftotext(os.path.join(d, meta["original_filename"]))))
    # txt-sourced: canonical normalisation of the stored original (raw HTML capture was cleaned pre-ingest)
    return norm(open(os.path.join(d, meta["original_filename"]), encoding="utf-8").read())

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite text.txt from the extractor")
    args = ap.parse_args()
    ver = poppler_version()
    print(f"pdftotext (Poppler) {ver}" + ("" if ver == PINNED_POPPLER else f"  ⚠ pinned {PINNED_POPPLER} — PDF bytes may differ"))
    pdf_ok = pdf_tot = txt_ok = txt_tot = 0; fails = []
    for mp in sorted(glob.glob(os.path.join(AUTH, "**", "metadata.yaml"), recursive=True)):
        meta = yaml.safe_load(open(mp, encoding="utf-8")); d = os.path.dirname(mp)
        got = rederive(meta, d)
        if got is None: continue
        is_pdf = meta.get("original_format") == "pdf"
        if is_pdf: pdf_tot += 1
        else: txt_tot += 1
        match = ("sha256:" + hashlib.sha256(got).hexdigest()) == meta["text_sha256"]
        if args.write: open(os.path.join(d, "text.txt"), "wb").write(got)
        if match:
            pdf_ok += is_pdf; txt_ok += (not is_pdf)
        else:
            fails.append(meta["corpus_id"])
    print(f"PDF-sourced reproduced byte-exact: {pdf_ok}/{pdf_tot}")
    print(f"txt-sourced reproduced (normaliser): {txt_ok}/{txt_tot}")
    if fails:
        print("DIFFERS: " + ", ".join(fails)); return 1
    print("RESULT: OK — every stored text re-derives from its committed original.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
