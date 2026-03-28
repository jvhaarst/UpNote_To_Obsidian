# UpNote to Obsidian Converter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert UpNote HTML+MD exports into a well-structured Obsidian vault with proper frontmatter, fenced code blocks, markdown tables, and organized attachments.

**Architecture:** A Python script reads metadata from UpNote's MD export (YAML frontmatter with dates and categories) and content from the HTML export (parsed with BeautifulSoup, converted via markdownify with custom converters). Output is an Obsidian vault organized by notebook folders with per-note attachment directories.

**Tech Stack:** Python 3.8+, uv (package management), beautifulsoup4, markdownify, python-frontmatter, ruff (linting)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Project config, dependencies, ruff settings |
| `convert.py` | CLI entry point: argument parsing, orchestration loop, summary output |
| `src/metadata.py` | Parse MD frontmatter, detect space name, extract dates/categories |
| `src/html_converter.py` | Custom markdownify subclass for HTML→Obsidian markdown conversion |
| `src/attachments.py` | Find, copy, and rewrite paths for images and file attachments |
| `src/writer.py` | Determine output paths, build frontmatter, write final .md files |
| `src/__init__.py` | Empty package init |
| `tests/test_metadata.py` | Tests for metadata extraction |
| `tests/test_html_converter.py` | Tests for HTML→markdown conversion |
| `tests/test_attachments.py` | Tests for attachment detection and path rewriting |
| `tests/test_writer.py` | Tests for output path logic and frontmatter building |
| `tests/test_integration.py` | End-to-end test with fixture files |

---

### Task 1: Project Setup with uv

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`

- [ ] **Step 1: Initialize the project with uv**

Run:
```bash
cd /Users/jvhaarst/code/UpNote_To_Obsidian && uv init --no-readme
```

- [ ] **Step 2: Add dependencies**

Run:
```bash
uv add beautifulsoup4 markdownify python-frontmatter
uv add --dev ruff pytest
```

- [ ] **Step 3: Configure ruff in pyproject.toml**

Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
```

- [ ] **Step 4: Create the src package**

Create `src/__init__.py` as an empty file.

- [ ] **Step 5: Verify setup**

Run:
```bash
uv run python -c "import frontmatter; import markdownify; import bs4; print('OK')"
```
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock src/__init__.py
git commit -m "chore: initialize project with uv, add dependencies and ruff config"
```

---

### Task 2: Metadata Extraction Module

**Files:**
- Create: `src/metadata.py`
- Create: `tests/test_metadata.py`

- [ ] **Step 1: Write failing tests for metadata extraction**

Create `tests/test_metadata.py`:
```python
import frontmatter

from src.metadata import detect_space_name, extract_metadata


def test_extract_metadata_basic():
    md_content = """\
---
date: 2014-07-09 16:47:38
created: 2014-07-09 16:47:38
categories:
- jvhaarst's notebook
- p1
---

## Some note
"""
    meta = extract_metadata(md_content)
    assert meta["created"] == "2014-07-09 16:47:38"
    assert meta["date"] == "2014-07-09 16:47:38"
    assert meta["categories"] == ["jvhaarst's notebook", "p1"]


def test_extract_metadata_no_categories():
    md_content = """\
---
date: 2020-01-01 12:00:00
created: 2020-01-01 12:00:00
---

## Note without categories
"""
    meta = extract_metadata(md_content)
    assert meta["categories"] == []


def test_detect_space_name():
    all_categories = [
        ["jvhaarst's notebook", "p1"],
        ["jvhaarst's notebook", "raspi"],
        ["jvhaarst's notebook"],
        ["jvhaarst's notebook", "Sysop"],
    ]
    assert detect_space_name(all_categories) == "jvhaarst's notebook"


def test_detect_space_name_no_common():
    all_categories = [
        ["notebook-a", "p1"],
        ["notebook-b", "raspi"],
    ]
    assert detect_space_name(all_categories) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_metadata.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.metadata'`

- [ ] **Step 3: Implement metadata module**

Create `src/metadata.py`:
```python
from __future__ import annotations

import frontmatter


def extract_metadata(md_content: str) -> dict:
    """Parse YAML frontmatter from UpNote MD export content.

    Returns dict with 'date', 'created', and 'categories' keys.
    """
    post = frontmatter.loads(md_content)
    return {
        "date": str(post.get("date", "")),
        "created": str(post.get("created", "")),
        "categories": list(post.get("categories", [])),
    }


def detect_space_name(all_categories: list[list[str]]) -> str | None:
    """Find the category that appears in every single note.

    This is the UpNote 'space' name which carries no useful information.
    Returns None if no universal category exists.
    """
    if not all_categories:
        return None
    common = set(all_categories[0])
    for cats in all_categories[1:]:
        common &= set(cats)
    if len(common) == 1:
        return common.pop()
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_metadata.py -v`
Expected: all 4 tests PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/metadata.py tests/test_metadata.py && uv run ruff format src/metadata.py tests/test_metadata.py`

- [ ] **Step 6: Commit**

```bash
git add src/metadata.py tests/test_metadata.py
git commit -m "feat: add metadata extraction from UpNote MD frontmatter"
```

---

### Task 3: HTML to Markdown Converter Module

**Files:**
- Create: `src/html_converter.py`
- Create: `tests/test_html_converter.py`

- [ ] **Step 1: Write failing tests for HTML conversion**

Create `tests/test_html_converter.py`:
```python
from src.html_converter import convert_html


def test_basic_heading():
    html = '<h2>My Title</h2>'
    result = convert_html(html)
    assert "## My Title" in result


def test_bold_and_italic():
    html = "<p><strong>bold</strong> and <em>italic</em></p>"
    result = convert_html(html)
    assert "**bold**" in result
    assert "*italic*" in result


def test_link():
    html = '<a href="http://example.com">click here</a>'
    result = convert_html(html)
    assert "[click here](http://example.com)" in result


def test_unordered_list():
    html = "<ul><li>one</li><li>two</li></ul>"
    result = convert_html(html)
    assert "* one" in result or "- one" in result
    assert "* two" in result or "- two" in result


def test_pre_block_to_fenced_code():
    html = '<pre spellcheck="false">print("hello")<br>print("world")</pre>'
    result = convert_html(html)
    assert "```" in result
    assert 'print("hello")' in result
    assert 'print("world")' in result
    # Must not contain <br> inside code blocks
    assert "<br>" not in result.split("```")[1]


def test_pre_block_br_becomes_newline():
    html = "<pre>line1<br><br>line2<br>line3</pre>"
    result = convert_html(html)
    code_content = result.split("```")[1].strip("\n")
    lines = code_content.split("\n")
    assert "line1" in lines[0]
    assert "line2" in lines[2] or "line2" in lines[1]
    assert "line3" in lines[-1] or "line3" in lines[-2]


def test_table_conversion():
    html = (
        "<table><tbody>"
        "<tr><th>Name</th><th>Value</th></tr>"
        "<tr><td>A</td><td>1</td></tr>"
        "<tr><td>B</td><td>2</td></tr>"
        "</tbody></table>"
    )
    result = convert_html(html)
    assert "| Name | Value |" in result
    assert "| A | 1 |" in result
    assert "---" in result


def test_image_tag():
    html = '<img src="Files/File%20160.jpeg">'
    result = convert_html(html)
    assert "![](Files/File%20160.jpeg)" in result or "![](Files/File 160.jpeg)" in result


def test_consecutive_br_collapse():
    html = "<p>Hello<br><br><br><br><br>World</p>"
    result = convert_html(html)
    # Should not have more than 2 consecutive newlines (1 blank line)
    assert "\n\n\n" not in result


def test_styled_div_drops_styling():
    html = '<div style="color: rgb(0,0,0); background-color: rgb(255,204,51);">content here</div>'
    result = convert_html(html)
    assert "content here" in result
    assert "background-color" not in result
    assert "style=" not in result


def test_html_entities_decoded():
    html = "<pre>if x &lt; 20 &amp;&amp; y &gt; 10:</pre>"
    result = convert_html(html)
    assert "x < 20" in result
    assert "&& y > 10" in result


def test_full_page_wrapper_stripped():
    html = (
        '<head><title></title><meta charset="utf-8"></head>'
        '<body class="light-theme blue_sky" style="padding: 20px;">'
        '<div class="shine-editor"><h2>Title</h2><p>Body text</p></div>'
        "</body>"
    )
    result = convert_html(html)
    assert "## Title" in result
    assert "Body text" in result
    assert "<head>" not in result
    assert "shine-editor" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_html_converter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.html_converter'`

- [ ] **Step 3: Implement the HTML converter**

Create `src/html_converter.py`:
```python
from __future__ import annotations

import re

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter


class UpNoteConverter(MarkdownConverter):
    """Custom markdownify converter for UpNote HTML → Obsidian markdown."""

    def convert_pre(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        """Convert <pre> blocks to fenced code blocks with <br> as newlines."""
        # Extract raw text content, converting <br> to newlines
        lines = []
        for child in el.children:
            if isinstance(child, NavigableString):
                lines.append(str(child))
            elif isinstance(child, Tag) and child.name == "br":
                lines.append("\n")
            else:
                lines.append(child.get_text())
        code = "".join(lines).strip("\n")
        return f"\n\n```\n{code}\n```\n\n"

    def convert_table(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        """Convert <table> to markdown table."""
        rows = el.find_all("tr")
        if not rows:
            return text

        table_data: list[list[str]] = []
        has_header = False

        for row in rows:
            cells = row.find_all(["th", "td"])
            if row.find("th"):
                has_header = True
            row_data = []
            for cell in cells:
                # Get cell text, collapse internal whitespace and <br>
                cell_text = cell.get_text(separator=" ").strip()
                cell_text = re.sub(r"\s+", " ", cell_text)
                row_data.append(cell_text)
            table_data.append(row_data)

        if not table_data:
            return text

        # If no explicit header row, treat first row as header anyway
        result_lines = []
        header = table_data[0]
        result_lines.append("| " + " | ".join(header) + " |")
        result_lines.append("| " + " | ".join("---" for _ in header) + " |")

        for row in table_data[1:]:
            # Pad row if needed
            while len(row) < len(header):
                row.append("")
            result_lines.append("| " + " | ".join(row) + " |")

        return "\n\n" + "\n".join(result_lines) + "\n\n"

    # Prevent markdownify from processing table internals
    def convert_td(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return text

    def convert_th(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return text

    def convert_tr(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return text

    def convert_thead(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return text

    def convert_tbody(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return text

    def convert_colgroup(self, el: Tag, text: str, convert_as_inline: bool = False) -> str:
        return ""


def convert_html(html_content: str) -> str:
    """Convert UpNote HTML export to Obsidian-compatible markdown.

    Extracts the content from the <div class="shine-editor"> wrapper if present,
    strips styling, and converts to clean markdown.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract content from shine-editor wrapper if present
    editor = soup.find("div", class_="shine-editor")
    if editor:
        target = editor
    elif soup.body:
        target = soup.body
    else:
        target = soup

    # Strip style attributes from all elements
    for tag in target.find_all(True):
        if tag.attrs:
            tag.attrs = {k: v for k, v in tag.attrs.items() if k not in ("style", "class", "data-keep-colors")}

    # Convert to markdown
    md = UpNoteConverter(
        heading_style="atx",
        bullets="*",
        strip=["head", "colgroup"],
    ).convert(str(target))

    # Collapse excessive newlines (more than 2 consecutive) to max 2
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip() + "\n"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_html_converter.py -v`
Expected: all 12 tests PASS

- [ ] **Step 5: Iterate on any failing tests**

Some edge cases in the converter may need tuning. Adjust `convert_html` or `UpNoteConverter` methods until all tests pass. Common issues:
- Table cell whitespace handling
- Nested `<br>` inside `<pre>` producing extra blank lines
- `markdownify` adding extra whitespace around elements

- [ ] **Step 6: Lint**

Run: `uv run ruff check src/html_converter.py tests/test_html_converter.py && uv run ruff format src/html_converter.py tests/test_html_converter.py`

- [ ] **Step 7: Commit**

```bash
git add src/html_converter.py tests/test_html_converter.py
git commit -m "feat: add HTML to Obsidian markdown converter with custom handlers"
```

---

### Task 4: Attachment Handling Module

**Files:**
- Create: `src/attachments.py`
- Create: `tests/test_attachments.py`

- [ ] **Step 1: Write failing tests for attachment extraction and path rewriting**

Create `tests/test_attachments.py`:
```python
from src.attachments import extract_attachment_refs, rewrite_attachment_paths


def test_extract_image_refs():
    html = '<img src="Files/File%20160.jpeg"><img src="Files/File.png">'
    refs = extract_attachment_refs(html)
    assert refs == ["Files/File 160.jpeg", "Files/File.png"]


def test_extract_link_refs():
    html = '<a href="Files/SAMv1.pdf">SAMv1.pdf</a>'
    refs = extract_attachment_refs(html)
    assert refs == ["Files/SAMv1.pdf"]


def test_extract_ignores_external_links():
    html = '<a href="http://example.com">link</a><img src="https://img.com/pic.png">'
    refs = extract_attachment_refs(html)
    assert refs == []


def test_extract_mixed():
    html = (
        '<img src="Files/File.jpeg">'
        '<a href="http://example.com">link</a>'
        '<a href="Files/doc.pdf">doc</a>'
        '<img src="https://remote.com/img.png">'
    )
    refs = extract_attachment_refs(html)
    assert refs == ["Files/File.jpeg", "Files/doc.pdf"]


def test_rewrite_image_paths():
    md = "![](Files/File%20160.jpeg)\n![](Files/File.png)\n"
    result = rewrite_attachment_paths(md)
    assert "![](attachments/File 160.jpeg)" in result
    assert "![](attachments/File.png)" in result


def test_rewrite_link_paths():
    md = "[SAMv1.pdf](Files/SAMv1.pdf)\n"
    result = rewrite_attachment_paths(md)
    assert "[SAMv1.pdf](attachments/SAMv1.pdf)" in result


def test_rewrite_preserves_external():
    md = "[link](http://example.com)\n![](https://remote.com/img.png)\n"
    result = rewrite_attachment_paths(md)
    assert "[link](http://example.com)" in result
    assert "![](https://remote.com/img.png)" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_attachments.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.attachments'`

- [ ] **Step 3: Implement attachment module**

Create `src/attachments.py`:
```python
from __future__ import annotations

import re
from urllib.parse import unquote

from bs4 import BeautifulSoup


def extract_attachment_refs(html_content: str) -> list[str]:
    """Extract all local attachment references from HTML.

    Finds <img src="Files/..."> and <a href="Files/..."> references.
    Returns URL-decoded file paths.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    refs: list[str] = []

    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("Files/"):
            refs.append(unquote(src))

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("Files/"):
            refs.append(unquote(href))

    return refs


def rewrite_attachment_paths(md_content: str) -> str:
    """Rewrite Files/ references in markdown to attachments/ paths.

    Handles both ![](Files/...) image refs and [text](Files/...) link refs.
    URL-decodes the filenames during rewriting.
    """

    def replace_files_ref(match: re.Match) -> str:
        prefix = match.group(1)  # "![...](" or "[...]("
        path = match.group(2)  # "Files/..."
        suffix = match.group(3)  # ")"
        decoded = unquote(path)
        new_path = decoded.replace("Files/", "attachments/", 1)
        return f"{prefix}{new_path}{suffix}"

    # Match ![...](Files/...) and [...](Files/...)
    pattern = r"(!?\[[^\]]*\]\()(Files/[^)]+)(\))"
    return re.sub(pattern, replace_files_ref, md_content)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_attachments.py -v`
Expected: all 7 tests PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/attachments.py tests/test_attachments.py && uv run ruff format src/attachments.py tests/test_attachments.py`

- [ ] **Step 6: Commit**

```bash
git add src/attachments.py tests/test_attachments.py
git commit -m "feat: add attachment extraction and path rewriting"
```

---

### Task 5: Writer Module (Output Path Logic + Frontmatter)

**Files:**
- Create: `src/writer.py`
- Create: `tests/test_writer.py`

- [ ] **Step 1: Write failing tests for output path determination and frontmatter building**

Create `tests/test_writer.py`:
```python
from pathlib import Path

from src.writer import build_frontmatter, determine_output_path


def test_determine_path_single_notebook():
    path = determine_output_path(
        note_name="My Note",
        categories=["space", "raspi"],
        space_name="space",
        has_attachments=False,
        output_dir=Path("/vault"),
    )
    assert path == Path("/vault/raspi/My Note.md")


def test_determine_path_with_attachments():
    path = determine_output_path(
        note_name="My Note",
        categories=["space", "raspi"],
        space_name="space",
        has_attachments=True,
        output_dir=Path("/vault"),
    )
    assert path == Path("/vault/raspi/My Note/My Note.md")


def test_determine_path_multiple_notebooks_uses_first():
    path = determine_output_path(
        note_name="My Note",
        categories=["space", "ntp", "pico", "raspi"],
        space_name="space",
        has_attachments=False,
        output_dir=Path("/vault"),
    )
    assert path == Path("/vault/ntp/My Note.md")


def test_determine_path_uncategorized():
    path = determine_output_path(
        note_name="My Note",
        categories=["space"],
        space_name="space",
        has_attachments=False,
        output_dir=Path("/vault"),
    )
    assert path == Path("/vault/_uncategorized/My Note.md")


def test_determine_path_empty_categories():
    path = determine_output_path(
        note_name="My Note",
        categories=[],
        space_name="space",
        has_attachments=False,
        output_dir=Path("/vault"),
    )
    assert path == Path("/vault/_uncategorized/My Note.md")


def test_build_frontmatter_basic():
    fm = build_frontmatter(
        created="2014-07-09 16:47:38",
        categories=["space", "p1", "raspi"],
        space_name="space",
    )
    assert fm == (
        "---\n"
        "date: 2014-07-09T16:47:38\n"
        "tags:\n"
        "  - p1\n"
        "  - raspi\n"
        "aliases: []\n"
        "---\n"
    )


def test_build_frontmatter_no_tags():
    fm = build_frontmatter(
        created="2020-01-01 12:00:00",
        categories=["space"],
        space_name="space",
    )
    assert fm == (
        "---\n"
        "date: 2020-01-01T12:00:00\n"
        "tags: []\n"
        "aliases: []\n"
        "---\n"
    )


def test_build_frontmatter_no_space_name():
    fm = build_frontmatter(
        created="2020-01-01 12:00:00",
        categories=["notebook-a", "notebook-b"],
        space_name=None,
    )
    assert "notebook-a" in fm
    assert "notebook-b" in fm
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_writer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.writer'`

- [ ] **Step 3: Implement writer module**

Create `src/writer.py`:
```python
from __future__ import annotations

from pathlib import Path


def determine_output_path(
    note_name: str,
    categories: list[str],
    space_name: str | None,
    has_attachments: bool,
    output_dir: Path,
) -> Path:
    """Determine the output file path for a note.

    Uses the first non-space category as the folder name.
    Notes with attachments get their own subfolder.
    Notes with no category go to _uncategorized/.
    """
    tags = [c for c in categories if c != space_name]
    folder = tags[0] if tags else "_uncategorized"

    if has_attachments:
        return output_dir / folder / note_name / f"{note_name}.md"
    return output_dir / folder / f"{note_name}.md"


def build_frontmatter(
    created: str,
    categories: list[str],
    space_name: str | None,
) -> str:
    """Build YAML frontmatter string for an Obsidian note."""
    # Convert date format: "2014-07-09 16:47:38" -> "2014-07-09T16:47:38"
    date_str = created.replace(" ", "T") if created else ""

    tags = [c for c in categories if c != space_name]

    lines = ["---"]
    lines.append(f"date: {date_str}")

    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
    else:
        lines.append("tags: []")

    lines.append("aliases: []")
    lines.append("---")

    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_writer.py -v`
Expected: all 8 tests PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/writer.py tests/test_writer.py && uv run ruff format src/writer.py tests/test_writer.py`

- [ ] **Step 6: Commit**

```bash
git add src/writer.py tests/test_writer.py
git commit -m "feat: add output path determination and frontmatter builder"
```

---

### Task 6: CLI Entry Point & Orchestration

**Files:**
- Create: `convert.py`

- [ ] **Step 1: Write the CLI entry point and orchestration loop**

Create `convert.py`:
```python
#!/usr/bin/env python3
"""UpNote to Obsidian converter.

Usage:
    uv run python convert.py --html-dir <path> --md-dir <path> --output-dir <path>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

from src.attachments import extract_attachment_refs, rewrite_attachment_paths
from src.html_converter import convert_html
from src.metadata import detect_space_name, extract_metadata
from src.writer import build_frontmatter, determine_output_path


def find_notes(html_dir: Path, md_dir: Path) -> list[tuple[str, Path, Path]]:
    """Find matching HTML/MD pairs. Returns list of (name, html_path, md_path)."""
    html_files = {p.stem: p for p in html_dir.glob("*.html")}
    md_files = {p.stem: p for p in md_dir.glob("*.md")}
    common = sorted(html_files.keys() & md_files.keys())
    return [(name, html_files[name], md_files[name]) for name in common]


def detect_space(notes: list[tuple[str, Path, Path]]) -> str | None:
    """Read all MD files to detect the universal space name."""
    all_categories = []
    for _name, _html_path, md_path in notes:
        meta = extract_metadata(md_path.read_text(encoding="utf-8"))
        if meta["categories"]:
            all_categories.append(meta["categories"])
    return detect_space_name(all_categories)


def process_note(
    name: str,
    html_path: Path,
    md_path: Path,
    html_files_dir: Path,
    space_name: str | None,
    output_dir: Path,
) -> dict:
    """Process a single note. Returns stats dict."""
    stats = {"converted": False, "images_copied": 0, "warnings": []}

    # 1. Extract metadata from MD
    md_content = md_path.read_text(encoding="utf-8")
    meta = extract_metadata(md_content)

    # 2. Read and convert HTML
    html_content = html_path.read_text(encoding="utf-8")
    markdown = convert_html(html_content)

    # 3. Extract attachment references from HTML
    attachment_refs = extract_attachment_refs(html_content)
    has_attachments = len(attachment_refs) > 0

    # 4. Determine output path
    out_path = determine_output_path(
        note_name=name,
        categories=meta["categories"],
        space_name=space_name,
        has_attachments=has_attachments,
        output_dir=output_dir,
    )

    # 5. Handle filename conflicts
    if out_path.exists():
        counter = 2
        while True:
            stem = f"{name} ({counter})"
            if has_attachments:
                candidate = out_path.parent.parent / stem / f"{stem}.md"
            else:
                candidate = out_path.parent / f"{stem}.md"
            if not candidate.exists():
                out_path = candidate
                break
            counter += 1

    # 6. Create output directories
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 7. Copy attachments
    if has_attachments:
        attachments_dir = out_path.parent / "attachments"
        attachments_dir.mkdir(exist_ok=True)
        for ref in attachment_refs:
            src_file = html_files_dir / ref.replace("Files/", "", 1)
            if src_file.exists():
                shutil.copy2(src_file, attachments_dir / src_file.name)
                stats["images_copied"] += 1
            else:
                stats["warnings"].append(f"Missing attachment: {ref} for note {name}")

    # 8. Rewrite attachment paths in markdown
    markdown = rewrite_attachment_paths(markdown)

    # 9. Build frontmatter and write
    frontmatter = build_frontmatter(
        created=meta["created"],
        categories=meta["categories"],
        space_name=space_name,
    )

    out_path.write_text(frontmatter + "\n" + markdown, encoding="utf-8")
    stats["converted"] = True
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert UpNote exports to Obsidian vault")
    parser.add_argument("--html-dir", type=Path, required=True, help="Path to HTML export General Space/ directory")
    parser.add_argument("--md-dir", type=Path, required=True, help="Path to MD export General Space/ directory")
    parser.add_argument("--output-dir", type=Path, default=Path("obsidian_vault"), help="Output directory for vault")
    args = parser.parse_args()

    html_dir = args.html_dir
    md_dir = args.md_dir
    output_dir = args.output_dir

    # Validate inputs
    if not html_dir.is_dir():
        print(f"Error: HTML directory not found: {html_dir}", file=sys.stderr)
        sys.exit(1)
    if not md_dir.is_dir():
        print(f"Error: MD directory not found: {md_dir}", file=sys.stderr)
        sys.exit(1)

    html_files_dir = html_dir / "Files"

    # Find matching note pairs
    notes = find_notes(html_dir, md_dir)
    if not notes:
        print("No matching HTML/MD pairs found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(notes)} notes to convert")

    # Detect space name
    space_name = detect_space(notes)
    if space_name:
        print(f"Detected space name: '{space_name}' (will be excluded from tags)")

    # Process each note
    total_converted = 0
    total_skipped = 0
    total_images = 0
    all_warnings: list[str] = []

    for name, html_path, md_path in notes:
        try:
            stats = process_note(name, html_path, md_path, html_files_dir, space_name, output_dir)
            if stats["converted"]:
                total_converted += 1
            total_images += stats["images_copied"]
            all_warnings.extend(stats["warnings"])
        except Exception as e:
            total_skipped += 1
            print(f"WARNING: Failed to convert '{name}': {e}", file=sys.stderr)

    # Print warnings
    for warning in all_warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    # Summary
    print(f"\nConverted: {total_converted} notes")
    if total_skipped:
        print(f"Skipped: {total_skipped} notes (see warnings above)")
    print(f"Images copied: {total_images}")
    print(f"Output: {output_dir}/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Lint**

Run: `uv run ruff check convert.py && uv run ruff format convert.py`

- [ ] **Step 3: Commit**

```bash
git add convert.py
git commit -m "feat: add CLI entry point with orchestration loop"
```

---

### Task 7: Integration Test

**Files:**
- Create: `tests/test_integration.py`
- Create: `tests/fixtures/html/test note.html`
- Create: `tests/fixtures/html/Files/test-image.png`
- Create: `tests/fixtures/html/Files/doc.pdf`
- Create: `tests/fixtures/md/test note.md`

- [ ] **Step 1: Create test fixtures**

Create `tests/fixtures/md/test note.md`:
```markdown
---
date: 2023-06-15 10:30:00
created: 2023-06-15 10:30:00
categories:
- my space
- raspi
- electronics
---

## Test Note
```

Create `tests/fixtures/html/test note.html`:
```html
<head><title></title><meta charset="utf-8"></head><body class="light-theme blue_sky" style="padding: 20px;"><div class="shine-editor"><h2>Test Note</h2><p>Some <strong>bold</strong> text and a <a href="http://example.com">link</a>.</p><img src="Files/test-image.png"><a href="Files/doc.pdf">doc.pdf</a><pre spellcheck="false">print("hello")<br>print("world")</pre><table><tbody><tr><th>Name</th><th>Value</th></tr><tr><td>A</td><td>1</td></tr></tbody></table></div></body>
```

Create `tests/fixtures/html/Files/test-image.png` — a 1-byte dummy file:
```bash
echo -n "x" > tests/fixtures/html/Files/test-image.png
```

Create `tests/fixtures/html/Files/doc.pdf` — a 1-byte dummy file:
```bash
echo -n "x" > tests/fixtures/html/Files/doc.pdf
```

- [ ] **Step 2: Write integration test**

Create `tests/test_integration.py`:
```python
from pathlib import Path

from convert import detect_space, find_notes, process_note


FIXTURES = Path(__file__).parent / "fixtures"
HTML_DIR = FIXTURES / "html"
MD_DIR = FIXTURES / "md"


def test_find_notes():
    notes = find_notes(HTML_DIR, MD_DIR)
    assert len(notes) == 1
    assert notes[0][0] == "test note"


def test_full_conversion(tmp_path: Path):
    notes = find_notes(HTML_DIR, MD_DIR)
    # Simulate space detection with a single note
    space_name = "my space"
    html_files_dir = HTML_DIR / "Files"

    name, html_path, md_path = notes[0]
    stats = process_note(name, html_path, md_path, html_files_dir, space_name, tmp_path)

    assert stats["converted"] is True
    assert stats["images_copied"] == 2  # test-image.png + doc.pdf

    # Check output file exists in correct location (has attachments -> subfolder)
    out_file = tmp_path / "raspi" / "test note" / "test note.md"
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")

    # Check frontmatter
    assert "date: 2023-06-15T10:30:00" in content
    assert "- raspi" in content
    assert "- electronics" in content
    assert "my space" not in content
    assert "aliases: []" in content

    # Check content conversion
    assert "## Test Note" in content
    assert "**bold**" in content
    assert "[link](http://example.com)" in content
    assert "```" in content
    assert 'print("hello")' in content
    assert "| Name | Value |" in content

    # Check attachment paths rewritten
    assert "attachments/test-image.png" in content
    assert "attachments/doc.pdf" in content

    # Check attachments copied
    attachments_dir = tmp_path / "raspi" / "test note" / "attachments"
    assert (attachments_dir / "test-image.png").exists()
    assert (attachments_dir / "doc.pdf").exists()
```

- [ ] **Step 3: Run integration test**

Run: `uv run pytest tests/test_integration.py -v`
Expected: all 2 tests PASS

- [ ] **Step 4: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: all tests PASS

- [ ] **Step 5: Run full lint check**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: no errors

- [ ] **Step 6: Commit**

```bash
git add tests/
git commit -m "test: add integration test with fixtures for end-to-end conversion"
```

---

### Task 8: Smoke Test on Real Data

**Files:** None (verification only)

- [ ] **Step 1: Run the converter on the real UpNote export**

Run:
```bash
uv run python convert.py \
  --html-dir "Upnote Export/UpNote_2026-03-28_10-58-09/General Space" \
  --md-dir "Upnote Export/UpNote_2026-03-26_22-58-26/General Space" \
  --output-dir obsidian_vault
```

Expected: Summary showing ~1,799 notes converted with minimal warnings.

- [ ] **Step 2: Verify a known complex note**

Check the gejanssen.com smart meter note:
```bash
cat "obsidian_vault/p1/gejanssen.com - Uitlezen slimme meter met Raspberry Pi/gejanssen.com - Uitlezen slimme meter met Raspberry Pi.md" | head -30
```

Verify:
- Frontmatter has `date:` and `tags: [p1]`
- Content starts with `## gejanssen.com - Uitlezen slimme meter met Raspberry Pi`
- Code blocks use triple backticks
- Images reference `attachments/` not `Files/`

- [ ] **Step 3: Verify attachments were copied**

```bash
ls "obsidian_vault/p1/gejanssen.com - Uitlezen slimme meter met Raspberry Pi/attachments/"
```

Expected: Image files present (`.jpeg`, `.png`)

- [ ] **Step 4: Verify uncategorized notes**

```bash
ls obsidian_vault/_uncategorized/ | head -10
```

Verify notes that only had the space name category land here.

- [ ] **Step 5: Spot-check a few other notes**

Check a note with tables, a note with no attachments (should be directly in folder, no subfolder), and a note with multiple categories (should have all as tags but be in the first category's folder).

- [ ] **Step 6: Fix any issues found and re-run**

If conversion issues are found, fix the relevant module, update tests, re-run, and commit.

- [ ] **Step 7: Commit any fixes**

```bash
git add -A
git commit -m "fix: address issues found during smoke test on real data"
```
