"""Server-side PDF rendering with WeasyPrint.

Offer letters and service agreements render on the entity letterhead (masthead
banner + footer). NCNDAs render as a plain document (no letterhead) with normal
margins, matching the supplied sample NCNDAs.
"""
from pathlib import Path

from ..documents.registry import get_entity
from ..documents import letterhead as lh

CSS_PATH = Path(__file__).resolve().parent.parent / "static" / "css" / "document.css"

# override applied for plain (no-letterhead) documents like the NCNDA
PLAIN_PAGE_CSS = """
@page {
    margin: 18mm 18mm 20mm 18mm;
    @top-center    { content: none; }
    @bottom-center { content: none; }
    @bottom-right  { content: none; }
}
"""


def _shell(ent, body_html, page_size="A4", letterhead=True):
    css = CSS_PATH.read_text(encoding="utf-8")
    if page_size.lower() == "letter":
        css = css.replace("size: A4;", "size: Letter;")
    if not letterhead:
        css += PLAIN_PAGE_CSS
        head = footer = ""
    else:
        masthead = lh.masthead_data_uri(ent)
        head = lh.header_html(ent, masthead)
        footer = lh.footer_html(ent)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{css}</style></head>
<body class="{lh.brand_class(ent)}{'' if letterhead else ' plain'}">
{head}
{footer}
<div class="doc-shell"><div id="document">{body_html}</div></div>
</body></html>"""


def render_pdf(entity_key, body_html, page_size="A4", letterhead=True):
    from weasyprint import HTML  # imported lazily so the app boots without it
    ent = get_entity(entity_key)
    html = _shell(ent, body_html, page_size, letterhead)
    return HTML(string=html).write_pdf()
