# The Playbook — building a provenance-first corpus for any domain

This is the repeatable method behind the Space Law Corpus, stripped of the space content. Follow it
to build the same kind of neutral, auditable, machine-readable record for a different body of law or
regulation — maritime, environmental, export-control/sanctions, AML, financial regulation, medical
device rules, or anything with primary source texts that change over time.

The whole thing rests on one principle: **provenance and version integrity override convenience,
always.** Every stored text can be traced to its official source and checked for tampering; every
change is a new dated version; nothing generated is ever passed off as authoritative.

The work splits into two kinds. The **mechanical** part — hashing, packaging, validating, building
the site, monitoring — is done by the scripts and never changes between domains. The **judgement**
part — scope, sources, the concept vocabulary, language rules, fidelity calls — is where you (and an
AI agent working under this playbook) do the thinking. You are never pressing one button, and you are
never starting from scratch.

## What you need

Git (or GitHub Desktop), Python 3.11+, and this toolkit. Install dependencies with
`pip install -r scripts/requirements.txt`, then run `python3 scripts/validate_corpus.py` — an empty
corpus should validate. That confirms the machinery works.

## Step 0 — Lock the design (half a day of decisions)

Open `design-templates/` and turn the six templates into your real design documents, filling every
`[DOMAIN]` placeholder. You are deciding, once and for all: the provenance fields every document must
carry (doc 01), your identifier shape and how change is recorded (doc 02), what counts as
authoritative and which languages are authentic (doc 03), the rights position for each source type
(doc 04), what is in and out of scope (doc 05), and the wall between authoritative and derived (doc
06). Record every non-obvious decision as a dated "judgement call" with the options and your reason.
These documents are the constitution; freeze them before ingesting anything.

## Step 1 — Map your sources honestly

Write a short source-coverage report: for each official source in your domain, what it publishes, in
what formats and languages, under what terms, and — the important part — where authentic texts are
missing or only unofficial translations exist. This is where "gaps are flagged, not papered over"
earns its keep. The output is a plan for ingestion order (start with the cleanest, most canonical
sources to prove the pipeline).

## Step 2 — Define your concept vocabulary

Edit `scripts/concepts.py` — the one file that carries all your domain-specific derived-layer logic.
Write a **neutral** vocabulary of 10–20 concepts (what a provision is *about*, taking no side), a
keyword fallback for each, and the header words your domain uses for provisions ("Section", "Article",
"Regulation", "Rule"…). You can start with just the keyword fallback and upgrade important instruments
to curated tags later.

## Step 3 — Ingest, instrument by instrument

For each document: **capture** it from the most official source, then **ingest** it. Capture and
ingest are deliberately separate. Prefer the issuer or official gazette/registry. If the automated
fetcher can't reach a source, escalate: a real browser, then a human-downloaded official file stored
byte-for-byte (this is a provenance *upgrade*, not a compromise). Never bypass bot-protection or
CAPTCHAs — have a human download the file instead.

Store only the **authentic-language** text as authoritative. Any translation is derived and unofficial
(see Step 5). If you can only find a translation and no authentic text, ingest an
`authoritative_missing` placeholder rather than faking it. Reproduce the official source faithfully —
including its typos — and flag the fidelity honestly (`extracted_unverified` until you've checked it).

Mechanically: write a manifest (JSON) pointing at your captured original and cleaned text, then run
`python3 scripts/ingest.py --manifest your.json`. It stores the files, computes hashes, writes
`metadata.yaml`, validates, and **refuses to overwrite** an existing version. Commit.

## Step 4 — Verify fidelity against the official source

For each `extracted_unverified` text, compare it against the official PDF or page, catch defects,
and upgrade the flag to `extracted_verified` with a dated `verification` record. Corrections are dated
`corrections` entries — the mistake and its fix both stay visible in Git. (On the space corpus this
step caught real typos in official UN and French government documents, and confirmed that some
apparent defects were actually in the official source.)

## Step 5 — Build the derived layer

Run `python3 scripts/build_derived.py`. It parses each text into provisions, tags them with your
concepts, builds a cross-instrument concept index, and writes a provenance record for every derived
artifact — each traceable to the authoritative text hash it came from. Translations you author go in
`derived/<id>/<ver>/translations/<lang>.md` and are picked up automatically, labelled unofficial.
Everything here is regenerable and clearly quarantined from the authoritative layer.

## Step 6 — Publish, then let it maintain itself

Run `python3 scripts/build_site.py` (configure the name/tagline in `site.json`) to generate a
static, dependency-free browsable site — each instrument shown beside its full provenance. Push to
GitHub; the included workflows give you a CI **integrity gate** on every change (`validate.yml`), a
monthly **source watcher** that opens an issue when a monitored page changes (`watch-sources.yml`),
and an **annual review** checklist. List the pages to watch in `monitoring/sources.json`.

## The rules you never break

The two-layer wall (authoritative vs derived) is enforced by folder, schema, and validator — never
put generated content under `authoritative/`. The authoritative layer is append-only — corrections
and amendments are new dated states, never overwrites. Gaps are recorded, not hidden. And you never
claim more fidelity than you actually checked. If you keep these, a competent stranger can take the
corpus over from the documents alone — which is exactly what makes it valuable and transferable.

## What's automated vs what needs you

The scripts do all the hashing, packaging, validation, structure parsing, keyword tagging, site
generation, and monitoring. You (or an AI agent following this playbook) do the judgement: scoping,
finding and vetting official sources, designing the neutral vocabulary, handling awkward sourcing,
and verifying fidelity. That judgement is the expertise you're bringing — the toolkit just makes it
fast, consistent, and provably rigorous.
