"""Letterhead header/footer generation, shared by preview + PDF + DOCX.

The header is the ACTUAL letterhead masthead, cropped from each entity's supplied
letterhead file (app/static/logos/lh_<entity>.png) and placed, as-is, at the top
of every page. The footer is a light single-line address strip for page
continuity. This keeps the on-page letterhead identical to the source documents.
"""
import base64
from pathlib import Path

from markupsafe import escape

LOGO_DIR = Path(__file__).resolve().parent.parent / "static" / "logos"

# Full masthead image per entity (used at the top of every page).
MASTHEAD_FILE = {
    "fss_usa": "lh_usa.png",
    "fss_hk": "lh_hk.png",
    "fss_uae": "lh_uae.png",
    "fss_korea": "lh_korea.png",
    "estel": "lh_estel.png",
    "estel_usa": "lh_estel_usa.png",
}


def brand_class(ent):
    return f'brand-{ent["brand"]}'


def masthead_path(ent):
    return LOGO_DIR / MASTHEAD_FILE[ent["key"]]


def masthead_data_uri(ent):
    p = masthead_path(ent)
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def header_html(ent, masthead_src):
    return (f'<div class="letterhead-header" id="running-header">'
            f'<img class="lh-band" src="{masthead_src}" alt="{escape(ent["legal_name"])} letterhead">'
            f'</div>')


def footer_html(ent):
    parts = [ent["legal_name"]] + ent["address_lines"] + [ent["contact_line"]]
    line = "  |  ".join(escape(p) for p in parts)
    return f'<div class="letterhead-footer" id="running-footer">{line}</div>'
