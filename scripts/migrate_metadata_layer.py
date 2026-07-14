#!/usr/bin/env python3
"""Metadata-layer migration (Deep Seabed Mining corpus).
Adds binding_force + issuing_authority + administering_authority to every record.
Metadata-only; never touches text or hashes. Idempotent. See migration plan."""
from __future__ import annotations
import glob, json, os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schema", "authoritative-metadata.schema.json")

BINDING = {"isa_draft":"non_binding","isa_regulation":"binding","advisory_opinion":"non_binding",
           "implementing_agreement":"binding","convention":"binding",
           "national_regulation":"binding","national_statute":"binding"}
ISSUER_BY_TYPE = {
    "isa_draft":"International Seabed Authority",
    "isa_regulation":"International Seabed Authority",
    "advisory_opinion":"International Tribunal for the Law of the Sea (Seabed Disputes Chamber)",
    "implementing_agreement":"United Nations General Assembly",
    "convention":"Third United Nations Conference on the Law of the Sea",
    "national_statute":"United States Congress",
    "national_regulation":"National Oceanic and Atmospheric Administration (NOAA)"}
ISSUER_BY_ID = {}
ADMIN_BY_ID = {"usa/statute/dshmra-1980":"National Oceanic and Atmospheric Administration (NOAA)"}

def patch_schema():
    txt = open(SCHEMA, encoding="utf-8").read()
    if "binding_force" in txt:
        print("schema: already patched"); return
    req = '    "provenance_note"\n  ],'
    if req not in txt: raise SystemExit("required-array anchor not found")
    txt = txt.replace(req, '    "provenance_note",\n    "binding_force",\n    "issuing_authority"\n  ],', 1)
    anchor = '    "provenance_note": {\n      "type": "string",\n      "minLength": 1\n    },\n'
    if anchor not in txt: raise SystemExit("provenance_note property anchor not found")
    add = (anchor +
      '    "binding_force": {\n      "type": "string",\n      "enum": [\n        "binding",\n        "non_binding"\n      ],\n'
      '      "description": "Legal force of the instrument on its own accord: binding or non_binding (recommendatory soft law). Orthogonal to authoritative_status; tier is DERIVED from jurisdiction downstream."\n    },\n'
      '    "issuing_authority": {\n      "type": "string",\n      "description": "Body that made/adopted the instrument. Distinct from source_publisher (where the text was obtained)."\n    },\n'
      '    "administering_authority": {\n      "type": [\n        "string",\n        "null"\n      ],\n      "description": "Body that administers/enforces the instrument where different from the issuer; null if not applicable."\n    },\n')
    txt = txt.replace(anchor, add, 1)
    json.loads(txt)
    open(SCHEMA, "w", encoding="utf-8").write(txt)
    print("schema: patched")

def yq(v): return '"' + v.replace('\\','\\\\').replace('"','\\"') + '"'

def backfill():
    changed = skipped = 0
    for f in sorted(glob.glob(os.path.join(ROOT,"authoritative","**","metadata.yaml"), recursive=True)):
        raw = open(f, encoding="utf-8").read()
        d = yaml.safe_load(raw)
        if "binding_force" in d and "issuing_authority" in d:
            skipped += 1; continue
        cid, dt = d.get("corpus_id"), d.get("document_type")
        bf = BINDING.get(dt)
        issuer = ISSUER_BY_ID.get(cid) or ISSUER_BY_TYPE.get(dt)
        admin = ADMIN_BY_ID.get(cid)
        if not bf or not issuer: raise SystemExit(f"no mapping for {dt} / {cid}")
        new = raw if raw.endswith("\n") else raw + "\n"
        new += f"binding_force: {bf}\n"
        new += f"issuing_authority: {yq(issuer)}\n"
        new += f"administering_authority: {yq(admin) if admin else 'null'}\n"
        d2 = yaml.safe_load(new)
        assert d2["binding_force"] == bf and d2["issuing_authority"] == issuer
        open(f, "w", encoding="utf-8").write(new)
        changed += 1
        print(f"  {cid:40} {dt:20} | {bf:11} | {issuer[:38]}"+(f" | admin={admin[:30]}" if admin else ""))
    print(f"backfill: {changed} changed, {skipped} skipped")

if __name__ == "__main__":
    patch_schema(); backfill()
