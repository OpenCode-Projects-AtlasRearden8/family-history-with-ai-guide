"""Tests for the Family History with AI Guide.

Run with:
    python3 -m unittest discover -s tests -v
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build  # noqa: E402


class MarkdownConverterTests(unittest.TestCase):
    def test_headings(self):
        html_out = build.md_to_html("# Hello\n\n## Sub section\n")
        self.assertIn("<h1>Hello</h1>", html_out)
        self.assertIn("<h2>Sub section</h2>", html_out)

    def test_bold_italic_code(self):
        html_out = build.md_to_html("Say **bold** and *soft* and `code here`.")
        self.assertIn("<strong>bold</strong>", html_out)
        self.assertIn("<em>soft</em>", html_out)
        self.assertIn("<code>code here</code>", html_out)

    def test_bullet_and_numbered_lists(self):
        html_out = build.md_to_html("- one\n- two\n\n1. first\n2. second\n")
        self.assertEqual(html_out.count("<li>"), 4)
        self.assertIn("<ul>", html_out)
        self.assertIn("<ol>", html_out)

    def test_continuation_lines_join_list_item(self):
        html_out = build.md_to_html("- story starts\n  and continues\n- next item\n")
        self.assertIn("<li>story starts and continues</li>", html_out)
        self.assertIn("<li>next item</li>", html_out)

    def test_checkboxes(self):
        html_out = build.md_to_html("- [ ] box one\n- [x] box two\n")
        self.assertEqual(html_out.count('class="task"'), 2)
        self.assertIn("checked", html_out)

    def test_table(self):
        md = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
        html_out = build.md_to_html(md)
        self.assertIn("<th>a</th>", html_out)
        self.assertIn("<td>2</td>", html_out)

    def test_table_preserves_empty_cells(self):
        md = "| a | b |\n| --- | --- |\n| 1 | |\n"
        html_out = build.md_to_html(md)
        self.assertIn("<td></td>", html_out)

    def test_blockquote_and_hr_and_fence(self):
        html_out = build.md_to_html("> a wise line\n\n---\n\n```\ncode\nblock\n```\n")
        self.assertIn("<blockquote>", html_out)
        self.assertIn("<hr>", html_out)
        self.assertIn("<pre><code>code\nblock</code></pre>", html_out)

    def test_bullet_list_with_blank_lines_stays_one_list(self):
        html_out = build.md_to_html("- one\n\n- two\n\n- three\n")
        self.assertEqual(html_out.count("<ul>"), 1)
        self.assertEqual(html_out.count("<li>"), 3)

    def test_consecutive_blockquote_lines_merge(self):
        html_out = build.md_to_html("> line one\n> line two\n")
        self.assertEqual(html_out.count("<blockquote>"), 1)
        self.assertIn("line one line two", html_out)

    def test_table_separator_not_confused_with_empty_rows(self):
        md = "| a | b |\n| --- | --- |\n| | |\n| 1 | 2 |\n"
        html_out = build.md_to_html(md)
        self.assertEqual(html_out.count("<tr>"), 3)  # header + 2 body rows

    def test_inline_html_is_escaped(self):
        html_out = build.md_to_html("Text with <script>alert(1)</script> inside.")
        self.assertNotIn("<script>", html_out)
        self.assertIn("&lt;script&gt;", html_out)


class BuildTests(unittest.TestCase):
    EXPECTED_PAGES = [
        "01-interviewing.html",
        "02-photos.html",
        "03-verification.html",
        "04-privacy.html",
        "05-memoir-writing.html",
        "06-publishing.html",
        "glossary.html",
        "index.html",
        "interview-questions.html",
        "interview-worksheet.html",
        "photo-inventory.html",
        "privacy-log.html",
        "source-log.html",
        "verification-checklist.html",
    ]

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="fh-build-")
        cls.out = Path(cls._tmp.name) / "site"
        build.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_all_expected_pages_built(self):
        for page in self.EXPECTED_PAGES:
            with self.subTest(page=page):
                self.assertTrue((self.out / page).is_file())

    def test_stylesheet_copied(self):
        css = self.out / "assets" / "style.css"
        self.assertTrue(css.is_file())
        self.assertIn("--accent", css.read_text(encoding="utf-8"))

    def test_pages_contain_license_line_and_nav(self):
        html_out = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", html_out)
        self.assertIn("masthead", html_out)
        self.assertIn('href="03-verification.html"', html_out)

    def test_all_internal_links_resolve(self):
        local = re.compile(r'href="([^"#]+\.html)"')
        broken = []
        for page in self.EXPECTED_PAGES:
            html_out = (self.out / page).read_text(encoding="utf-8")
            for target in local.findall(html_out):
                if not (self.out / target).is_file():
                    broken.append(f"{page} -> {target}")
        self.assertEqual(broken, [])

    def test_checklist_page_has_front_and_rear_checks(self):
        html_out = (self.out / "verification-checklist.html").read_text(encoding="utf-8")
        self.assertIn('class="task"', html_out)
        self.assertGreaterEqual(html_out.count('class="task"'), 10)

    def test_no_unresolved_cross_folder_links(self):
        for page in self.EXPECTED_PAGES:
            html_out = (self.out / (self.out / page)).read_text(encoding="utf-8")
            self.assertNotIn('../docs/', html_out, page)
            self.assertNotIn('../worksheets/', html_out, page)

    def test_glossary_terms_present(self):
        html_out = (self.out / "glossary.html").read_text(encoding="utf-8")
        for term in ("Living-person rule", "Hallucination", "Source log",
                     "Local-first", "Proof copy", "Census record"):
            with self.subTest(term=term):
                self.assertIn(term, html_out)

    def test_safety_notes_present_in_chapters(self):
        verification = (self.out / "03-verification.html").read_text(encoding="utf-8")
        self.assertIn("UNVERIFIED", verification)
        privacy = (self.out / "04-privacy.html").read_text(encoding="utf-8")
        self.assertIn("consent", privacy.lower())


class ContentPolicyTests(unittest.TestCase):
    """The repo must stay clean: no secrets, no personal data, license intact."""

    TEXT_SUFFIXES = {".md", ".py", ".css", ".txt", ".gitignore", ".py"}

    def _repo_text_files(self):
        allowed = {"docs", "worksheets", "scripts", "tests", "assets"}
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if ".git" in rel.parts or (rel.parts and rel.parts[0] == "site"):
                continue
            if rel.suffix in self.TEXT_SUFFIXES or rel.name in {
                ".gitignore", "LICENSE", "STATUS.md"
            }:
                if rel.parts and rel.parts[0] not in allowed | {"."}:
                    continue
                yield path

    def test_no_secrets_or_keys(self):
        secret_patterns = [
            re.compile(r"(api[_-]?key|apikey|secret|password|token)\s*[:=]\s*['\"]?\w", re.I),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
            re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
            re.compile(r"sk-[A-Za-z0-9]{20,}"),
        ]
        for path in self._repo_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in secret_patterns:
                with self.subTest(file=str(path.relative_to(ROOT)), pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(text))

    def test_no_real_looking_emails(self):
        email = re.compile(r"[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com|example)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        offenders = []
        for path in self._repo_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            if email.search(text):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_no_phone_number_patterns(self):
        phone = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
        offenders = [str(p.relative_to(ROOT)) for p in self._repo_text_files()
                     if phone.search(p.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(offenders, [])

    def test_license_line_is_exact(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", license_text)
        self.assertIn("The MIT License", license_text)

    def test_readme_credits_llc(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", readme)
        self.assertIn("MIT", readme)


if __name__ == "__main__":
    unittest.main()
