# STATUS

Project: **The Family History with AI Guide** — a manual for preserving
family stories with AI help (interviewing, photos, verification, privacy,
writing self-voiced memoir chapters, self-publishing), built as Markdown docs
plus a generated static HTML site.

Owner: Asdale Dynamics, LLC — Copyright (c) 2026 Asdale Dynamics, LLC

## What was built

- **Manual (docs/, 8 pages):** welcome/how-to-use, six chapters
  (01-interviewing, 02-photos, 03-verification, 04-privacy,
  05-memoir-writing, 06-publishing) plus glossary (17 terms).
- **Worksheets (worksheets/, 7 pages):** ready question bank,
  interview worksheet, photo inventory, source log,
  **verification checklist**, privacy log, and a worksheets index.
- **Static site generator (scripts/build.py):** stdlib-only converter
  (headings, paragraphs, bold/italic/code/links, bullet/numbered/checkbox
  lists, blockquotes, tables, fenced code, horizontal rules), shared warm
  stylesheet (assets/style.css), nav header with active-page highlight,
  cross-folder link normalization, build-date stamp, and MIT license footer.
- **Site output (site/, 15 pages):** self-contained, opens from `file://`
  with no server. Regenerate any time; the folder is rebuilt from source.
- **Tests (tests/test_build.py, 25 tests):** converter unit tests, full
  build into a temp dir (page set, stylesheet, internal-link resolution),
  glossary/verification content assertions, and repo policy tests
  (LICENSE line exact, README credit, no secrets/API-key-shaped strings,
  no personal-looking emails or phone numbers anywhere).
- **README.md** (usage + design promises) and **LICENSE** (MIT,
  exact line: `Copyright (c) 2026 Asdale Dynamics, LLC`).

## How to run it

```bash
# build the site (Python 3.10+, stdlib only, no pip installs)
python3 scripts/build.py              # -> site/
python3 scripts/build.py --out /tmp/out   # optional custom output dir

# open the site
# (open site/index.html in any browser; works offline)

# run the tests
python3 -m unittest discover -s tests -v
```

## Verification results

- `python3 scripts/build.py` → builds 15 pages + stylesheet, exit 0.
- `python3 -m unittest discover -s tests` → **Ran 25 tests, OK**.
- All internal `<a href>` links across the built site resolve (test-enforced).
- Built HTML tag-balance spot-checked with Python `html.parser`: clean.
- Repo policy tests pass: exact LICENSE line, README credit present,
  no secret/personal-data patterns in tracked text files.

## Known gaps / honest limits

- The Markdown converter is deliberately small: no nested list indentation
  (dotted sub-lists), no image syntax `![]()`, no autolinks, no footnote or
  definition-list syntax, no setext headings. If a future chapter needs
  images, either extend the converter (add an `!` inline image rule) or
  reference site images via plain HTML.
- No search box on the site; navigation is chapter-list based. Fine at this
  size; revisit if the manual grows past ~20 chapters.
- Content coverage is broad rather than deep: regional records (UK, EU,
  non-English archives) get only generic pointers rather than country-by-
  country how-tos; the publishing chapter compares print paths generically
  instead of auditing specific vendors' current pricing/privacy terms.
- Local transcription/AI tooling is described conceptually (e.g., "local
  transcription"); the manual doesn't ship its own transcription utility.
- Accessibility basics are in (semantic headings, viewport, print styles),
  but a formal WCAG audit and screen-reader pass haven't been run.

## House rules honored here

Local-first (no cloud requirement, no accounts), no secrets or personal data
in any file, MIT license with the exact Asdale Dynamics, LLC copyright line,
README credited to Asdale Dynamics, LLC. Committed locally only; nothing is
pushed, published, or hosted anywhere.
