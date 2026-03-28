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
    assert "![](attachments/File%20160.jpeg)" in result
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
