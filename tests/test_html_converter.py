from src.html_converter import convert_html


def test_basic_heading():
    html = "<h2>My Title</h2>"
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


def test_table_pipe_in_cell():
    html = "<table><tbody><tr><th>Name</th><th>Value</th></tr><tr><td>a | b</td><td>1</td></tr></tbody></table>"
    result = convert_html(html)
    assert "| a \\| b | 1 |" in result


def test_table_extra_cells_truncated():
    html = "<table><tbody><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td><td>3</td></tr></tbody></table>"
    result = convert_html(html)
    assert "| 1 | 2 |" in result
    assert "3" not in result


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
