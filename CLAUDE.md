# Working notes for Claude — deep-seabed-mining-law-corpus

## Session preamble (ALWAYS)

Every block of shell commands given for this repo must begin with these two lines. No exceptions —
omitting them has already caused commands to run in the wrong repo and against the wrong Python.

```
& "$env:USERPROFILE\.venvs\crawl4ai\Scripts\Activate.ps1"
cd "C:\Users\dache\Claude\Projects\Project Deep\deep-seabed-mining-law-corpus"
```

Why both, every time:

- **The venv** holds `crawl4ai` on Python 3.13. System Python is 3.14, where `lxml` has no wheel and
  the install fails. Without the venv the monitor silently degrades to whole-page mode for every
  source — it does not error, so a missing venv looks like a successful run that quietly did less.
- **The `cd`** because several sibling repos live under `C:\Users\dache\Claude\Projects\`. Running
  from the wrong one produces confusing "did not match any files" errors at best, and stages the
  wrong repo at worst.

Confirm the prompt reads `(crawl4ai)` and the correct path before running anything live.

## Repo workflow

- **Write locally, the user pushes.** Never `git commit`, `git push`, or change git config from the
  agent sandbox.
- Stage **only** files explicitly created or changed, **each named individually**. Never `git add .`
  or `git add -A`.
- Name the target branch explicitly in the push command. Default branch: `main`.
- Commit messages: `type: short imperative summary`, double-quoted, no `$`, backticks or nested
  quotes.

## Layer-1 boundary (non-negotiable)

`authoritative/` stores official files byte-for-byte. Crawl4AI output is **never** stored as
`text.txt`; `scripts/extract.py` is the sole version-pinned extractor, so reproducibility checks stay
valid. No stealth/magic/proxy modes against official sources, ever. Full rules:
`scripts/crawl/README.md`.

## Monitoring quick reference

```
python scripts\watch_sources.py --selftest    # offline, stdlib only
python scripts\watch_sources.py               # live run (needs the venv)
python scripts\watch_sources.py --tally       # measured whole-page false-alarm rate
```

Schema-mode sources carry a `schema` in `monitoring/sources.json`; the rest fall back to whole-page
hashing. A `SCHEMA SUSPECT` flag means selectors have probably broken — the baseline is deliberately
not advanced. Verify the schema against the live page before the next run.

LINE ENDINGS — deliberate scope (2026-07-22, task: pin LF on CRLF-risk write sites)
-----------------------------------------------------------------------------------
Every script that writes a TRACKED file pins newline="\n". Python text mode translates "\n" to
"\r\n" on Windows, and .gitattributes governs CHECKOUT, not what a script writes — verified: a
CRLF working file under `* text=auto eol=lf` is still reported modified, with an empty diff. That
churn is what made the derived layer permanently "modified" after a rebuild.

DELIBERATELY NOT PINNED (writes nothing tracked, or never re-run):
  * build_site.py            -> writes site/, which is gitignored (built fresh in CI for Pages).
                                CRLF there reaches no repository and no consumer.
  * migrate_metadata_layer.py -> one-shot 2026-07 migration, already run, kept only as a record of
                                what was executed. If it is ever re-run, pin it first.
