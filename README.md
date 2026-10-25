# The Family History with AI Guide

**Preserving family stories with AI help — verified, private, and warm.**

This project is a beginner-friendly manual for capturing your family's
history with the help of AI tools: interviewing relatives with ready question
banks, scanning and organizing photos, verifying every AI claim against real
records, protecting living relatives' privacy, writing memoir chapters in
your own voice, and self-publishing the finished book.

The content ships as Markdown documents plus a static HTML site the build
script generates — all local-first, using nothing but the Python standard
library. No accounts, no uploads, no secrets.

## What's inside

| Path | Contents |
| --- | --- |
| `docs/` | The manual's chapters: interviewing, photos, verification, privacy, writing, publishing, plus the glossary |
| `worksheets/` | Print-ready question bank, interview worksheet, photo inventory, source log, verification checklist, privacy log |
| `assets/` | The site stylesheet |
| `scripts/build.py` | Static-site build script (Markdown → HTML) |
| `tests/` | Test suite (`unittest`, stdlib only) |
| `site/` | The generated static site (safe to delete; rebuilt any time) |

## Requirements

- Python 3.10+ (standard library only — no pip installs needed)

## Build the site

```bash
python3 scripts/build.py            # builds into site/
python3 scripts/build.py --out DIR  # build anywhere you like
```

Then open `site/index.html` in a browser. Everything works offline from a
`file://` URL — no server required.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

## Creating content

- Add a chapter to `docs/` or a worksheet to `worksheets/` as Markdown, then
  rebuild. Register new page titles in `scripts/build.py` (`CHAPTER_TITLES`).
- The converter supports headings, paragraphs, bold/italic, inline code and
  fenced code blocks, bullet/numbered/checkbox lists, blockquotes, tables, and
  horizontal rules.

## Design promises

- **Verify everything:** no AI-produced fact enters the book until a real
  record confirms it; the source log and verification checklist make that
  practical.
- **Protect the living:** no details of living relatives — no addresses,
  phone numbers, full birth dates, medical or legal details, nothing about
  children — unless they consented, logged in the privacy log.
- **Keep your voice:** AI organizes and points; you write the sentences.
- **Local-first:** your family's photos, audio, and drafts stay on your
  machine. Cloud is optional and your call.

This project contains no personal data and no private information — it's a
manual, not an archive.

## License

[MIT](LICENSE) — Copyright (c) 2026 Asdale Dynamics, LLC

Part of Asdale Dynamics, LLC's beginner-friendly AI education series: books,
guides, and tools that explain AI like a friend would.
