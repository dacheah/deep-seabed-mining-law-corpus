# Publishing to GitHub (dacheah/deep-seabed-mining-law-corpus)

The repository is built with full history in a git **bundle** that ships in this folder:
`deep-seabed-mining-law-corpus.bundle` (all commits, branch `main`). Git can't run inside the
synced Cowork folder, so reconstruct the repo from the bundle on your own machine, then push.

## 1. Reconstruct the repo (preserves the full commit history)
```bash
# pick any working location on your computer
git clone "…/Project Deep/deep-seabed-mining-law-corpus/deep-seabed-mining-law-corpus.bundle" \
  deep-seabed-mining-law-corpus
cd deep-seabed-mining-law-corpus     # branch 'main', all commits present
```
On Windows (Git Bash), the path is:
`"C:/Users/dache/Claude/Projects/Project Deep/deep-seabed-mining-law-corpus/deep-seabed-mining-law-corpus.bundle"`

## 2. Create the GitHub repo and push

**Easiest — GitHub CLI (if `gh` is installed and you're logged in):**
```bash
gh repo create dacheah/deep-seabed-mining-law-corpus --public --source=. --push \
  --description "Neutral, provenance-first corpus of deep seabed mining law (UNCLOS Part XI, ISA regime, US DSHMRA track)."
```

**Or manual:** create an EMPTY repo at https://github.com/new named
`deep-seabed-mining-law-corpus` (do NOT add a README, .gitignore, or licence), then:
```bash
git remote add origin https://github.com/dacheah/deep-seabed-mining-law-corpus.git
git push -u origin main
```

## 3. After the first push (one-time settings)
- **Actions** run automatically: the CI integrity gate (`validate.yml`) checks every change; it must be green.
- **Enable Pages:** Settings → Pages → Build and deployment → Source = **GitHub Actions**. The
  `pages.yml` workflow then builds and serves the site at
  https://dacheah.github.io/deep-seabed-mining-law-corpus/ (the URL already referenced by the dataset card).
- The **monthly source-watch** (`watch-sources.yml`) and **annual review** (`annual-review.yml`) are
  scheduled automatically; the watcher opens an issue when a monitored ISA/UN/US page changes.

## 4. Then Hugging Face (optional, next)
```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload dacheah/deep-seabed-mining-law-corpus ./hf-dataset . --repo-type dataset
```
