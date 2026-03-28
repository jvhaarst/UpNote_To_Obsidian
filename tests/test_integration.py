from pathlib import Path

from convert import find_notes, process_note

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
