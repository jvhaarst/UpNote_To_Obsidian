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


def test_detect_space_name_majority():
    """Space name detected even when not in every note."""
    all_categories = [
        ["jvhaarst's notebook", "p1"],
        ["jvhaarst's notebook", "raspi"],
        ["Sysop"],  # note without space name
        ["jvhaarst's notebook"],
    ]
    assert detect_space_name(all_categories) == "jvhaarst's notebook"


def test_detect_space_name_no_common():
    all_categories = [
        ["notebook-a", "p1"],
        ["notebook-b", "raspi"],
    ]
    assert detect_space_name(all_categories) is None
