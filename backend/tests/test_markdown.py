import pytest

from app.utils.markdown import render_markdown


@pytest.mark.no_db
def test_render_markdown_supports_code_and_dollar_math():
    rendered = render_markdown(
        "```python\nprint('ok')\n```\n\nInline $x^2$ and:\n\n$$y = mx + b$$"
    )

    assert 'class="language-python"' in rendered
    assert 'class="math inline"' in rendered
    assert 'data-tex="x^2" data-display="false"' in rendered
    assert 'class="math block"' in rendered
    assert 'data-tex="y = mx + b" data-display="true"' in rendered


@pytest.mark.no_db
def test_render_markdown_sanitizes_html_and_dangerous_urls():
    rendered = render_markdown(
        '<img src="javascript:alert(1)" onerror="alert(1)">'
        '<script>alert(1)</script>'
        '[unsafe](javascript:alert(1))'
    )

    assert '<script' not in rendered.lower()
    assert 'onerror' not in rendered.lower()
    assert 'href="javascript:' not in rendered.lower()
