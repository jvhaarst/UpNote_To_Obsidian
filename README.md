# UpNote to Obsidian Converter

Converts an UpNote export into an Obsidian-compatible vault, preserving rich formatting (code blocks, tables, images) and metadata (dates, notebooks/tags). Uses two UpNote export formats as input: **HTML** for content fidelity and **Markdown** for metadata.

Forked from [Adams141's UpNoteReorganizer](https://github.com/adams141/UpNote_Reorganizer).

## How It Works

UpNote's Markdown export loses code block formatting (rendered as bold text) and table structure. The HTML export preserves these but lacks structured metadata. This converter uses both:

- **HTML export** — rich content: code blocks (`<pre>`), tables, images, formatting
- **MD export** — YAML frontmatter: `date`, `created`, `categories` (notebook assignments)

The converter pairs files by name (they match 1:1 between exports), extracts the best of each, and produces clean Obsidian-compatible markdown.

## Step 1: Export from UpNote

You need two bulk exports from UpNote. The export dialog is under **UpNote > File > Export**.

### HTML export

1. In UpNote, select all notes (or the notebook you want to export)
2. **File > Export > HTML**
3. Select **Expand All** to ensure all content is included
4. Export to a folder — UpNote creates a directory like `UpNote_2026-03-28_10-58-09/General Space/`

This directory contains one `.html` file per note and a `Files/` subdirectory with all images and attachments.

### Markdown export

1. Same selection of notes
2. **File > Export > Markdown**
3. Export to a separate folder — UpNote creates a directory like `UpNote_2026-03-26_22-58-26/General Space/`

This directory contains one `.md` file per note with YAML frontmatter (dates and categories).

## Step 2: Place the exports

Put both export directories somewhere accessible. The converter expects paths to the `General Space/` directories inside each export. A typical layout:

```
UpNote_To_Obsidian/
  convert.py
  src/
  Upnote Export/                          # optional, any location works
    UpNote_2026-03-28_10-58-09/
      General Space/                      # <-- pass this as --html-dir
        note1.html
        note2.html
        Files/
          image1.jpeg
          image2.png
    UpNote_2026-03-26_22-58-26/
      General Space/                      # <-- pass this as --md-dir
        note1.md
        note2.md
```

## Step 3: Install dependencies

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Step 4: Run the conversion

```bash
uv run python convert.py \
  --html-dir "Upnote Export/UpNote_2026-03-28_10-58-09/General Space" \
  --md-dir "Upnote Export/UpNote_2026-03-26_22-58-26/General Space" \
  --output-dir obsidian_vault
```

The `--output-dir` defaults to `obsidian_vault/` if omitted.

### Output

```
Found 1799 notes to convert
Detected space name: 'users's notebook' (will be excluded from tags)

Converted: 1799 notes
Images copied: 2439
Output: obsidian_vault/
```

## Step 5: Open in Obsidian

Open the output directory as an Obsidian vault (**Open folder as vault**). All notes, images, tags, and folder structure are ready to use.

## Output Structure

Each UpNote notebook becomes a top-level folder. Notes with images/attachments get their own subfolder:

```
obsidian_vault/
  kubernetes/
    ArgoCD.md                             # note without attachments
    k3s op raspi5.md
  caravan/
    Verbeteringen aan caravan/            # note with attachments
      Verbeteringen aan caravan.md
      attachments/
        Evernote Snapshot 20130811 150709.jpg
    simple-note.md
  _uncategorized/                         # notes with no notebook category
    some-note.md
```

### Frontmatter

Each note gets Obsidian-native YAML frontmatter:

```yaml
---
date: 2014-07-09T16:47:38
tags:
  - caravan
  - vakantie
aliases: []
---
```

- `date` — note creation date from the UpNote MD export
- `tags` — UpNote notebook categories (the auto-detected space name is excluded since it's the same for every note)
- `aliases` — empty, ready for you to populate

### Folder placement

The first remaining category (after stripping the space name) determines the folder. Additional categories become tags. Notes with no category go in `_uncategorized/`.

## What Gets Converted

| Source | Output |
|---|---|
| `<pre>` code blocks | Fenced code blocks (triple backticks) |
| `<table>` | Markdown tables with pipe separators |
| `<strong>`, `<em>` | `**bold**`, `*italic*` |
| `<a href>` | `[text](url)` |
| `<img src="Files/...">` | `![](attachments/filename)` with file copied |
| `<ul>`, `<ol>` | Markdown lists with nesting |
| `<h1>` through `<h6>` | `#` through `######` |
| Inline styling/colors | Stripped (content preserved) |
| UpNote `#tag` links (`upnote://`) | Plain `#tag` hashtags |
| Legacy Evernote note links (`evernote:///`) | Plain text (link removed, text kept) |
| Images with spaces in filenames | URL-encoded paths for Obsidian compatibility |

## Development

### Running tests

```bash
uv run pytest tests/ -v
```

### Linting

```bash
uv run ruff check
uv run ruff format --check
```

### Project structure

```
convert.py              # CLI entry point — orchestrates the full pipeline
src/
  metadata.py           # YAML frontmatter parsing, space name detection
  html_converter.py     # HTML to Obsidian markdown (custom markdownify converter)
  attachments.py        # Attachment reference extraction and path rewriting
  writer.py             # Output path logic and frontmatter generation
tests/
  test_metadata.py      # 5 tests
  test_html_converter.py # 16 tests
  test_attachments.py   # 7 tests
  test_writer.py        # 8 tests
  test_integration.py   # 2 integration tests
```

### Dependencies

- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [markdownify](https://github.com/matthewwithanm/python-markdownify) — HTML to markdown conversion
- [python-frontmatter](https://github.com/eyeseast/python-frontmatter) — YAML frontmatter parsing
