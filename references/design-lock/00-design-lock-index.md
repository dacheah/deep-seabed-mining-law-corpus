# Design Lock — index (TEMPLATE)

These six documents are the **constitution** of your corpus. Fill in the `[DOMAIN]` and
bracketed placeholders, agree them once, and freeze them ("lock"). Everything downstream —
scripts, schemas, folder layout — serves these decisions. Change them only by a dated
decision note, never silently.

The one principle everything serves: **provenance and version integrity override convenience,
always.**

1. `01-provenance-schema.md` — what metadata every authoritative document must carry.
2. `02-versioning-scheme.md` — identifiers, and how change is recorded (append-only).
3. `03-authoritative-text-policy.md` — what counts as authoritative; authentic language; fidelity flags.
4. `04-licensing-policy.md` — rights to store/redistribute each source type.
5. `05-scope-boundary.md` — what is in and out of scope for [DOMAIN].
6. `06-two-layer-separation.md` — the wall between authoritative and derived.

**Judgement calls.** Record every non-obvious decision (a "JC") with its options, the choice,
and the reason, dated. The first ones usually are: which languages are authoritative (JC:
authentic-language rule); how to handle a source you can only find as a translation; whether to
store third-party copyrighted full text or link+cite.
