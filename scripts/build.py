#!/usr/bin/env python3
"""Build the Family History with AI Guide static site.

Converts the markdown in docs/ and worksheets/ into a self-contained
static HTML site (site/), using only the Python standard library.

Usage:
    python3 scripts/build.py            # build into site/
    python3 scripts/build.py --out DIR  # build into a custom directory
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
WORKSHEETS = ROOT / "worksheets"
ASSETS = ROOT / "assets"
DEFAULT_OUT = ROOT / "site"

TITLE = "The Family History with AI Guide"
SUBTITLE = "Preserving family stories with AI help — verified, private, and warm"
COPYRIGHT = "Copyright (c) 2026 Asdale Dynamics, LLC"

CHAPTER_TITLES = {
    "index": "Welcome",
    "01-interviewing": "Interviewing Relatives",
    "02-photos": "Photos",
    "03-verification": "Verification",
    "04-privacy": "Privacy",
    "05-memoir-writing": "Writing",
    "06-publishing": "Publishing",
    "glossary": "Glossary",
    "worksheets": "Worksheets",
    "interview-questions": "Question Bank",
    "interview-worksheet": "Interview Worksheet",
    "photo-inventory": "Photo Inventory",
    "source-log": "Source Log",
    "verification-checklist": "Verification Checklist",
    "privacy-log": "Privacy Log",
}

NAV_MAIN = [
    ("index.html", "Welcome"),
    ("01-interviewing.html", "Interviewing"),
    ("02-photos.html", "Photos"),
    ("03-verification.html", "Verification"),
    ("04-privacy.html", "Privacy"),
    ("05-memoir-writing.html", "Writing"),
    ("06-publishing.html", "Publishing"),
]
NAV_REF = [
    ("worksheets.html", "Worksheets"),
    ("glossary.html", "Glossary"),
]


# --------------------------------------------------------------------------
# A small, honest Markdown-to-HTML converter (stdlib only)
# --------------------------------------------------------------------------

BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
CHECK = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$")
NUMBER = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
ATX = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE = re.compile(r"^```(.*)$")
QUOTE = re.compile(r"^>\s?(.*)$")
TABLE_ROW = re.compile(r"^\|(.+)\|$")
SEP_ROW = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
HR = re.compile(r"^\s*(?:(?:-{3,})|(?:\*{3,}))\s*$")
INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), r'<a href="\2">\1</a>'),
]


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    for pattern, repl in INLINE:
        out = pattern.sub(repl, out)
    return out


def md_to_html(md: str) -> str:
    out: list[str] = []
    para: list[str] = []
    list_stack: list[str] = []  # "ul" | "ol"

    def close_list() -> None:
        while list_stack:
            out.append("</ul>" if list_stack.pop() == "ul" else "</ol>")

    def _flush_paragraph(lines: list[str], out: list[str]) -> None:
        if lines:
            close_list()
            out.append(f"<p>{inline(' '.join(lines))}</p>")
            lines.clear()

    in_code = False
    code_lines: list[str] = []
    rows: list[tuple[bool, list[str]]] = []  # (is_header, cells)
    quote_buffer: list[str] = []

    def _flush_quotes() -> None:
        if quote_buffer:
            close_list()
            out.append("<blockquote>" + " ".join(inline(q) for q in quote_buffer) + "</blockquote>")
            quote_buffer.clear()

    def _flush_all() -> None:
        _flush_paragraph(para, out)
        _flush_quotes()
        close_list()

    def _flush_soft() -> None:
        # Blank lines keep the current list open so items with blank lines
        # between them stay in one list.
        _flush_paragraph(para, out)
        _flush_quotes()

    def _open_list(kind: str) -> None:
        if list_stack and list_stack[-1] != kind:
            close_list()
        if not list_stack:
            list_stack.append(kind)
            out.append("<ul>" if kind == "ul" else "<ol>")

    def close_table() -> None:
        if not rows:
            return
        header, body = rows[0], rows[1:]
        out.append("<table>")
        out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header[1]) + "</tr></thead>")
        if body:
            out.append("<tbody>")
            for _, cells in body:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            out.append("</tbody>")
        out.append("</table>")
        rows.clear()

    first_h1: str | None = None
    for raw in md.splitlines():
        line = raw.rstrip()
        if in_code:
            if FENCE.match(line.strip()):
                out.append('<pre><code>' + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                code_lines.append(line)
            continue
        fence = FENCE.match(line.strip())
        if fence:
            _flush_all()
            close_table()
            in_code = True
            continue
        if SEP_ROW.match(line.strip()) and "-" in line.strip() and rows and rows[-1][0]:
            continue  # separator row inside table
        m_row = TABLE_ROW.match(line.strip())
        if m_row:
            _flush_all()
            cells = [c.strip() for c in m_row.group(1).split("|")]
            if not rows or rows[0][0] is False:
                rows.clear()
                rows.append((True, cells))
            else:
                rows.append((False, cells))
            continue
        close_table()
        if not line.strip():
            _flush_soft()
            continue
        if HR.match(line.strip()):
            _flush_all()
            out.append("<hr>")
            continue
        m = ATX.match(line)
        if m:
            _flush_all()
            level = len(m.group(1))
            text = inline(m.group(2).strip())
            if level == 1 and first_h1 is None:
                first_h1 = m.group(2).strip()
            out.append(f"<h{level}>{text}</h{level}>")
            continue
        m = QUOTE.match(line)
        if m:
            _flush_paragraph(para, out)
            close_list()
            quote_buffer.append(m.group(1))
            continue
        m = CHECK.match(line)
        if m:
            _flush_soft()
            _open_list("ul")
            if out and out[-1] == "<ul>":
                out[-1] = '<ul class="checklist">'
            checked = "checked" if m.group(1).lower() == "x" else ""
            out.append(
                f'<li class="task"><input type="checkbox" disabled {checked}> '
                f'<span>{inline(m.group(2))}</span></li>'
            )
            continue
        m = BULLET.match(line)
        if m:
            _flush_soft()
            _open_list("ul")
            out.append(f"<li>{inline(m.group(2))}</li>")
            continue
        m = NUMBER.match(line)
        if m:
            _flush_soft()
            _open_list("ol")
            out.append(f"<li>{inline(m.group(3))}</li>")
            continue
        if list_stack and (line.startswith("  ") or line.startswith("\t")):
            continuation = line.strip()
            if continuation and out and out[-1].startswith("<li"):
                out[-1] = out[-1][: -len("</li>")] + " " + inline(continuation) + "</li>"
            elif continuation:
                _flush_all()
                para.append(continuation)
            continue
        para.append(line.strip())
    if in_code and code_lines:
        out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    _flush_all()
    close_table()
    return "\n".join(out)


def extract_title(md: str) -> str:
    for line in md.splitlines():
        m = ATX.match(line.strip())
        if m and len(m.group(1)) == 1:
            return m.group(2).strip()
    return "Untitled"


CROSS_LINK = re.compile(r'(href=")\.\./(?:docs|worksheets)/([a-z0-9-]+\.html)"')


def normalize_links(body_html: str) -> str:
    """Rewrite in-markdown cross-folder links (../docs/x.html) for the flat site."""
    return CROSS_LINK.sub(r'\1\2"', body_html)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def render_page(slug: str, title: str, body_html: str, out_pages: set[str]) -> str:
    current = f"{slug}.html"

    def nav_link(href: str, label: str) -> str:
        cls = ' class="active"' if href == current else ""
        return f'<a href="{href}"{cls}>{label}</a>'

    main_nav = "".join(f"<li>{nav_link(h, l)}</li>" for h, l in NAV_MAIN)
    ref_nav = "".join(f"<li>{nav_link(h, l)}</li>" for h, l in NAV_REF)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — {TITLE}</title>
<meta name="description" content="{SUBTITLE}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="masthead">
  <p class="masthead-title"><a href="index.html">{TITLE}</a></p>
  <p class="masthead-sub">{SUBTITLE}</p>
</header>
<nav class="site-nav">
  <ul class="nav-main">{main_nav}</ul>
  <ul class="nav-ref">{ref_nav}</ul>
</nav>
<main id="content">
<article>
{body_html}
</article>
</main>
<footer class="site-footer">
  <p>{COPYRIGHT}</p>
  <p>Built from Markdown, locally, on {date.today().isoformat()}.
     Verify every fact against real records — the <a href="03-verification.html">Verification chapter</a> shows how.</p>
</footer>
</body>
</html>
"""


def compile_sources() -> dict[str, tuple[Path, str]]:
    """Return {slug: (markdown_path, title)} for every markdown page.

    docs/index.md keeps slug "index"; worksheets/index.md becomes "worksheets"
    so the welcome page and the worksheets index cannot collide.
    """
    pages: dict[str, tuple[Path, str]] = {}
    for folder in (DOCS, WORKSHEETS):
        for md_path in sorted(folder.glob("*.md")):
            slug = "worksheets" if (folder == WORKSHEETS and md_path.stem == "index") else md_path.stem
            md = md_path.read_text(encoding="utf-8")
            pages[slug] = (md_path, extract_title(md))
    return pages


def build(out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_out = out_dir / "assets"
    assets_out.mkdir(exist_ok=True)
    style_src = ASSETS / "style.css"
    (assets_out / "style.css").write_text(style_src.read_text(encoding="utf-8"), encoding="utf-8")

    sources = compile_sources()
    slugs = sorted(sources)
    out_pages = {f"{slug}.html" for slug in slugs}

    built: list[str] = []
    for slug in slugs:
        md_path, _title_from_md = sources[slug]
        md = md_path.read_text(encoding="utf-8")
        body = normalize_links(md_to_html(md))
        title = CHAPTER_TITLES.get(slug, extract_title(md))
        html_text = render_page(slug, title, body, out_pages)
        (out_dir / f"{slug}.html").write_text(html_text, encoding="utf-8")
        built.append(f"{slug}.html")

    print(f"Built {len(built)} pages into {out_dir}")
    for page_name in built:
        print(f"  {page_name}")
    return built


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    args = parser.parse_args(argv)
    build(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
