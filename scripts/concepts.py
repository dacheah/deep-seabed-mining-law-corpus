"""
concepts.py -- THE DOMAIN CONFIG FILE. This is the main file you edit for a new domain.

Everything domain-specific about the derived layer lives here:
  * VOCAB            -- your neutral concept vocabulary (concept -> plain-English definition)
  * TAGS             -- optional curated/model tags: corpus_id -> [ [unit_label, [concepts]], ... ]
  * KW               -- keyword fallback: concept -> [substrings]. Used when a doc has no TAGS entry.
  * UNIT_HEADERS     -- how provisions are labelled in your domain (for structure extraction)
  * CITATION_PATTERNS-- regexes for cross-references you want detected

Rules of thumb:
  * Keep concepts NEUTRAL: describe what a provision is ABOUT, take no side.
  * Start with KW (cheap, mechanical). Upgrade high-value docs to curated TAGS later.
  * Nothing here is authoritative -- it all lands in the derived/ layer, labelled unofficial.

The example below is a tiny, generic illustration. DELETE it and write your own.
"""

# ---- your neutral concept vocabulary -----------------------------------------
VOCAB = {
    "scope_and_definitions": "What the instrument covers; defined terms.",
    "obligations": "Duties imposed on regulated parties.",
    "authority_and_supervision": "Powers of the regulator; authorisation, licensing, oversight.",
    "liability_and_penalties": "Consequences of breach; damages, fines, sanctions.",
    "rights_and_entitlements": "Rights or entitlements granted.",
    "procedure_and_process": "How things are done; applications, timelines, appeals.",
    "international_and_cooperation": "Cross-border effect; cooperation, mutual recognition.",
    # ... add the concepts your domain actually needs (10-20 is typical).
}

# ---- optional curated tags (corpus_id -> [ [unit, [concepts]] ]) --------------
# Fill this in for your most important instruments; leave others to the KW fallback.
TAGS = {
    # "nat/xxx/example-2020": [
    #   ["Section 1", ["scope_and_definitions"]],
    #   ["Section 2", ["obligations", "authority_and_supervision"]],
    # ],
}

# ---- keyword fallback (concept -> substrings, lower-case) ---------------------
KW = {
    "obligations": ["shall", "must", "is required to", "obligation"],
    "liability_and_penalties": ["liable", "liability", "penalty", "fine", "damages", "sanction"],
    "authority_and_supervision": ["authoris", "authoriz", "licen", "supervis", "competent authority"],
    "procedure_and_process": ["application", "shall submit", "within", "appeal", "procedure"],
    "international_and_cooperation": ["cooperation", "mutual", "cross-border", "international"],
}

# ---- structure extraction: how provisions are headed in your domain ----------
# e.g. ["Article", "Section", "Rule", "Guideline", "Principle", "Clause"]
UNIT_HEADERS = ["Article", "Section", "Rule", "Guideline", "Principle", "Clause", "Regulation"]

# ---- cross-references to detect (regexes) ------------------------------------
CITATION_PATTERNS = [
    r"[Ss]ection\s+\d+[A-Za-z\-]*",
    r"[Aa]rticle\s+([IVXLCDM]+|\d+)",
    r"[Rr]egulation\s+\d+",
]
