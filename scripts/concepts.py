"""
concepts.py -- THE DOMAIN CONFIG FILE for the Deep Seabed Mining Law Corpus.

Everything domain-specific about the derived layer lives here. All output lands in derived/,
labelled unofficial; nothing here is authoritative. Concepts are NEUTRAL: they describe what a
provision is ABOUT, taking no side (never "pro-mining"/"pro-moratorium"). See docs/design/06.
"""

GENERATOR = "dsm-corpus-toolkit build_derived (neutral keyword pass)"

# ---- neutral concept vocabulary (what a provision is ABOUT) -------------------
VOCAB = {
    "the_area_and_common_heritage":
        "The Area and its resources as the common heritage of mankind; non-appropriation; vesting of rights in mankind as a whole.",
    "definitions_and_scope":
        "Defined terms (\"resources\", \"minerals\", \"activities in the Area\") and the scope/application of the instrument.",
    "sponsoring_state_responsibility_and_liability":
        "Responsibility of States (and sponsoring States) to ensure compliance, and liability for damage arising from activities in the Area.",
    "isa_institutional_structure":
        "The International Seabed Authority's organs (Assembly, Council, Legal and Technical Commission, Secretariat, Enterprise): composition, powers, procedure, voting.",
    "exploration_and_exploitation_system":
        "The system of exploration and exploitation: plans of work, contracts, qualifications of applicants, security of tenure.",
    "reserved_areas_and_the_enterprise":
        "Reserved areas, the Enterprise, joint arrangements, and parallel-system access to the Area.",
    "benefit_sharing_and_financial_regime":
        "Equitable sharing of financial and other economic benefits; payments, contributions, royalties, financial terms of contracts.",
    "production_policy_and_economic_effects":
        "Production policies, production authorizations/ceilings, commodity markets, and protection of affected (esp. developing) economies.",
    "marine_environmental_protection":
        "Protection and preservation of the marine environment from activities in the Area; the precautionary approach; best environmental practice.",
    "environmental_assessment_and_monitoring":
        "Environmental impact assessment, monitoring programmes, and environmental management/regional plans.",
    "marine_scientific_research":
        "Marine scientific research in the Area and dissemination of results.",
    "technology_transfer_and_capacity":
        "Transfer of technology and scientific knowledge, training, and capacity-building, especially for developing States.",
    "developing_states_special_interests":
        "Special interests and needs of developing, land-locked and geographically disadvantaged States.",
    "peaceful_use_and_general_conduct":
        "Use of the Area exclusively for peaceful purposes and the general conduct of States in relation to the Area.",
    "protection_of_human_life_and_safety":
        "Protection of human life and installation safety in the conduct of activities in the Area.",
    "compliance_inspection_and_enforcement":
        "Inspection, emergency orders, suspension/adjustment of operations, penalties and other compliance measures.",
    "dispute_settlement_and_advisory_opinions":
        "Jurisdiction of the Seabed Disputes Chamber, settlement of disputes, and advisory opinions.",
    "privileges_immunities_and_legal_status":
        "Legal status, privileges and immunities of the Authority, the Enterprise and connected persons.",
    "review_and_amendment":
        "Periodic review, the Review Conference, and procedures for amending the regime.",
    "us_non_unclos_parallel_regime":
        "Provisions of the US DSHMRA/OCSLA track operating outside the ISA regime (national parallel track).",
}

# ---- optional curated tags (corpus_id -> [ [unit, [concepts]] ]) --------------
# Curated provision-level tags are added for high-value instruments after review.
TAGS = {}

# ---- keyword fallback (concept -> substrings, lower-case) ---------------------
KW = {
    "the_area_and_common_heritage": ["common heritage", "the area and its resources", "vested in mankind",
        "appropriate any part", "sovereignty or sovereign rights over", "benefit of mankind", "patrimoine commun de l", "la zone et ses ressources", "ressources de la zone", "au nom de l’humanité", "dans l’intérêt de l’humanité"],
    "definitions_and_scope": ["use of terms", "for the purposes of this", "\"resources\"", "\"minerals\"",
        "scope of this part", "means all solid", "aux fins du présent", "on entend par", "termes utilisés dans la convention"],
    "sponsoring_state_responsibility_and_liability": ["responsibility to ensure", "liability for damage",
        "sponsored", "sponsoring", "joint and several liability", "shall have the responsibility", "liable", "état qui patronne", "états qui patronnent", "état patronnant", "qui patronnent des", "responsabilité", "obligation de diligence", "diligence requise", "obligations de l’état"],
    "isa_institutional_structure": ["the assembly", "the council", "legal and technical commission",
        "secretariat", "secretary-general", "the enterprise", "powers and functions", "composition, procedure and voting",
        "economic planning commission", "organs of the authority", "autorité internationale des fonds marins", "l’autorité", "le conseil", "l’assemblée", "commission juridique et technique", "secrétaire général", "l’entreprise", "organes de l’autorité"],
    "exploration_and_exploitation_system": ["plan of work", "plans of work", "system of exploration and exploitation",
        "qualifications of applicants", "security of tenure", "contract", "prospecting, exploration", "plan de travail", "contrat d’exploration", "exploration et d’exploitation", "prospection", "contractant"],
    "reserved_areas_and_the_enterprise": ["reserved area", "the enterprise", "joint arrangement", "parallel", "secteur réservé", "coentreprise"],
    "benefit_sharing_and_financial_regime": ["equitable sharing", "financial and other economic benefits",
        "payments and contributions", "financial terms", "funds of the authority", "royalt", "fee", "avantages financiers", "partage des avantages", "redevance"],
    "production_policy_and_economic_effects": ["production authorization", "production ceiling", "production polic",
        "commodity", "nickel", "adverse effects", "export earnings", "economic adjustment", "politique de production", "autorisation de production"],
    "marine_environmental_protection": ["protection of the marine environment", "protection for the marine environment",
        "precautionary", "harmful effects", "pollution", "ecological balance", "flora and fauna", "best environmental", "protection du milieu marin", "milieu marin", "approche de précaution", "principe de précaution", "préservation du milieu marin", "effets nocifs"],
    "environmental_assessment_and_monitoring": ["environmental impact", "assessment", "monitoring programme",
        "monitor", "environmental management", "environmental implications", "évaluation de l’impact", "étude d’impact sur l’environnement"],
    "marine_scientific_research": ["marine scientific research", "scientific research in the area", "recherche scientifique marine"],
    "technology_transfer_and_capacity": ["transfer of technology", "transfer to developing", "training",
        "scientific knowledge", "capacity", "transfert des techniques", "transfert de technologie", "formation du personnel"],
    "developing_states_special_interests": ["developing states", "developing countries", "land-locked",
        "geographically disadvantaged", "special interests", "special need", "états en développement", "pays en développement", "sans littoral", "géographiquement désavantagés"],
    "peaceful_use_and_general_conduct": ["peaceful purposes", "general conduct of states", "fins pacifiques", "exclusivement pacifiques"],
    "protection_of_human_life_and_safety": ["protection of human life", "safety zones", "safety of both navigation",
        "installations", "protection de la vie humaine", "sécurité de la navigation"],
    "compliance_inspection_and_enforcement": ["inspect", "emergency order", "suspension or adjustment",
        "penalt", "non-compliance", "compliance", "sanction", "veiller au respect", "assurer le respect", "mesures nécessaires pour assurer"],
    "dispute_settlement_and_advisory_opinions": ["seabed disputes chamber", "settlement of disputes", "dispute",
        "advisory opinion", "jurisdiction", "arbitration", "chambre pour le règlement des différends", "avis consultatif", "règlement des différends", "différend"],
    "privileges_immunities_and_legal_status": ["privileges and immunities", "immunity", "legal personality",
        "legal status", "inviolable", "exempt from", "privilèges et immunités", "personnalité juridique"],
    "review_and_amendment": ["periodic review", "review conference", "amendment", "shall undertake a general", "conférence de révision", "réexamen", "amendement"],
    "us_non_unclos_parallel_regime": ["dshmra", "deep seabed hard mineral", "hard mineral resources",
        "commercial recovery", "reciprocating state", "the administrator", "noaa", "outer continental shelf",
        "15 cfr", "hard mineral resources act"],
}

# ---- structure extraction: how provisions are headed in this domain ----------
UNIT_HEADERS = ["Article", "Section", "Regulation", "Annex", "Principle", "Rule", "Paragraph"]

# ---- cross-references to detect (regexes) ------------------------------------
CITATION_PATTERNS = [
    r"[Aa]rticle\s+(\d+[A-Za-z\-]*)",
    r"Annex\s+([IVXLCDM]+)",
    r"[Ss]ection\s+(\d+)",
    r"[Rr]egulation\s+(\d+)",
    r"paragraph\s+(\d+)",
]
