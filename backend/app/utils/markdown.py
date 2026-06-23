from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

md = MarkdownIt("commonmark", {"html": True, "typographer": True})
md.enable("table")
front_matter_plugin(md)
footnote_plugin(md)


def render_markdown(text: str) -> str:
    return md.render(text)
