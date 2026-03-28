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
    assert fm == ("---\ndate: 2014-07-09T16:47:38\ntags:\n  - p1\n  - raspi\naliases: []\n---\n")


def test_build_frontmatter_no_tags():
    fm = build_frontmatter(
        created="2020-01-01 12:00:00",
        categories=["space"],
        space_name="space",
    )
    assert fm == ("---\ndate: 2020-01-01T12:00:00\ntags: []\naliases: []\n---\n")


def test_build_frontmatter_no_space_name():
    fm = build_frontmatter(
        created="2020-01-01 12:00:00",
        categories=["notebook-a", "notebook-b"],
        space_name=None,
    )
    assert "notebook-a" in fm
    assert "notebook-b" in fm
