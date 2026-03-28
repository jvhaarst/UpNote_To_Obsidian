# UpNote to Obsidian Converter — Design Spec

## Overview

A Python script (`convert.py`) that converts UpNote exports into an Obsidian-compatible vault. It uses two input sources — an HTML export for rich content and a Markdown export for metadata — to produce the best possible representation in Obsidian.

## Inputs

- **HTML bulk export** (`UpNote_2026-03-28_10-58-09/General Space/`): 1,799 `.html` files with rich formatting (`<pre>`, `<table>`, styling). Contains a `Files/` directory with images and attachments, plus a `styles.css` (ignored).
- **MD bulk export** (`UpNote_2026-03-26_22-58-26/General Space/`): 1,799 `.md` files with YAML frontmatter containing `date`, `created`, and `categories`. Contains a `Files/` directory (not used) and empty `notebooks/` directories (not used).

Filenames match 1:1 between exports (same basename, different extension).

## Output Structure

A flat notebook-per-folder Obsidian vault:

```
obsidian_vault/
  raspi/
    GPS module PPS op Raspberry Pi/
      GPS module PPS op Raspberry Pi.md
      attachments/
        File.jpeg
        File 2.png
    simple-note-no-images.md
  Sysop/
    ...
  _uncategorized/
    ...
```

- Each notebook becomes a top-level folder.
- Notes with attachments get their own subfolder containing the `.md` file and an `attachments/` directory.
- Notes without attachments sit directly in the notebook folder (no subfolder).
- Notes with no notebook category go in `_uncategorized/`.

## Pipeline (per note)

1. Parse YAML frontmatter from the `.md` file to extract `date`, `created`, and `categories`.
2. Parse the `.html` file with BeautifulSoup.
3. Convert HTML to Obsidian markdown using `markdownify` with custom converters.
4. Build YAML frontmatter for the output note.
5. Determine target folder from categories.
6. Copy referenced images/attachments to the note's `attachments/` directory.
7. Rewrite image/attachment paths in content.
8. Write the final `.md` file.

## HTML to Markdown Conversion

Using `markdownify` with custom converters:

| HTML element | Obsidian output |
|---|---|
| `<pre>` | Fenced code block (triple backticks, no language tag) |
| `<table>` | Markdown table with `\|` and `---` separators |
| `<strong>` / `<b>` | `**bold**` |
| `<em>` / `<i>` | `*italic*` |
| `<a href="...">` | `[text](url)` |
| `<img src="Files/...">` | `![](attachments/filename)` with rewritten path |
| `<ul>` / `<ol>` / `<li>` | Markdown lists with proper nesting |
| `<h1>` through `<h6>` | `#` through `######` |
| `<br>` | Newline; consecutive `<br>` tags collapse to max 2 newlines |
| `<div>` with styling | Drop styling, keep content |
| `<code>` (inline) | Backtick-wrapped inline code |

### Internal link handling

- **UpNote tag links** (`upnote://x-callback-url/tag/view?tag=kubernetes`): Converted to plain `#tag` hashtags. These are UpNote's inline hashtag references — in Obsidian they render as native tags.
- **Legacy Evernote note links** (`evernote:///view/<account>/<space>/<note-id>/`): Link text is preserved, the unresolvable `evernote:///` URL is removed. These are note-to-note links from notes originally imported from Evernote into UpNote. Since the links use Evernote note IDs (not note names), they cannot be automatically mapped to Obsidian `[[wikilinks]]`.

Both link types are resolved during HTML preprocessing, before the markdownify conversion runs.

### Edge cases

- **Consecutive `<br>` tags:** Collapse to a maximum of 2 newlines to avoid excessive whitespace.
- **URL-encoded image paths:** File paths with spaces (e.g. `File%20160.jpeg`) stay URL-encoded in markdown references for Obsidian compatibility. The actual files are copied with decoded names — Obsidian decodes the `%20` when resolving the path.
- **`<pre>` blocks with `<br>` inside:** Convert `<br>` to actual newlines within code blocks, not markdown line breaks.
- **Empty links or image-only links:** Preserve as-is.

## Metadata & Frontmatter

### Output frontmatter format

```yaml
---
date: 2014-07-09T16:47:38
tags:
  - p1
  - raspi
aliases: []
---
```

- `date`: the `created` value from the UpNote MD export (note creation date).
- `tags`: all `categories` values except the UpNote space name (auto-detected as the category present in every note — in this case `jvhaarst's notebook`). Dropped because it carries no information.
- `aliases`: empty list, ready for user to populate.

## Folder Placement Logic

1. Strip the auto-detected space name (the category present in every single note) from the categories list.
2. Remaining categories become tags in frontmatter.
3. The **first remaining category** determines the folder (UpNote's ordering).
4. If no categories remain, place in `_uncategorized/`.

## Image & Attachment Handling

Images and attachments come from the **HTML export's `Files/` directory** (matching the HTML content references).

Per note:
1. Find all `<img src="...">` and `<a href="...">` pointing to `Files/...`.
2. URL-decode the path.
3. Copy each file to `<note-subfolder>/attachments/`.
4. Rewrite the reference in the output markdown to `attachments/<filename>`.

Non-image attachments (PDFs, JSON, `.bin`) are handled identically.

Filename collisions within a single note are not a concern — UpNote already ensures unique names per note.

## Error Handling

The script processes all notes in one run, logging issues and continuing rather than failing on the first error.

- **Missing HTML/MD match:** Log warning, skip note, report at end.
- **Missing image file:** Log warning, keep reference as-is in markdown, continue.
- **Unparseable HTML:** Log error with filename, skip note.
- **Output filename conflicts** (two notes with same name in same folder): Append numeric suffix.

### End-of-run summary (stdout)

```
Converted: 1795 notes
Skipped: 4 notes (see warnings above)
Images copied: 312
Output: ./obsidian_vault/
```

No log file — stdout only.

## Dependencies & Tooling

### Package management: uv

Use `uv` for dependency management and virtual environment. The project will have a `pyproject.toml` with dependencies declared there.

```bash
uv init
uv add beautifulsoup4 markdownify python-frontmatter
uv add --dev ruff
```

### Runtime dependencies

- Python 3.8+
- `beautifulsoup4` — HTML parsing
- `markdownify` — HTML to markdown conversion
- `python-frontmatter` — YAML frontmatter parsing from MD files
- Standard library: `os`, `shutil`, `re`, `urllib.parse`, `pathlib`

### Linting: ruff

Use `ruff` for linting and formatting. Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
```

All code must pass `uv run ruff check` and `uv run ruff format --check` before committing.
