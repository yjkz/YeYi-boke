from html import escape
from html.parser import HTMLParser
import re

import bleach
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin


ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {
        "a", "abbr", "br", "code", "div", "h1", "h2", "h3", "h4", "h5", "h6",
        "hr", "img", "li", "ol", "p", "pre", "s", "section", "span", "sub", "sup",
        "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
    }
)
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


def _allowed_attribute(tag: str, name: str, value: str) -> bool:
    if name in {"class", "id", "title", "aria-label", "aria-hidden"}:
        return True
    if tag == "a" and name == "href":
        return True
    if tag == "img" and name in {"src", "alt", "width", "height"}:
        return True
    if tag == "code" and name == "class":
        return True
    if tag in {"div", "span"} and name in {"data-tex", "data-display"}:
        return True
    return False


def _render_math(content: str, options: dict[str, bool]) -> str:
    display = "true" if options.get("display_mode") else "false"
    return f'<span data-tex="{escape(content.strip(), quote=True)}" data-display="{display}"></span>'


md = MarkdownIt("commonmark", {"html": True, "typographer": True})
md.enable(["table", "strikethrough"])
front_matter_plugin(md)
footnote_plugin(md)
dollarmath_plugin(md, allow_space=True, allow_digits=True, renderer=_render_math)


def render_markdown(text: str) -> str:
    rendered = md.render(text)
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=_allowed_attribute,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


class _PlainTextParser(HTMLParser):
    """Extract readable text from the already-sanitized Markdown HTML."""

    _ignored_tags = {"script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._ignored_tags:
            self._ignored_depth += 1
            return
        if tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.parts.append(alt)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._ignored_tags and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def excerpt_from_markdown(text: str, limit: int = 200) -> str:
    """Return a compact plain-text excerpt without Markdown syntax."""
    if not text:
        return ""
    parser = _PlainTextParser()
    parser.feed(render_markdown(text))
    plain_text = re.sub(r"\s+", " ", "".join(parser.parts)).strip()
    return plain_text[:limit]
