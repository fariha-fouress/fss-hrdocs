"""Letterhead header/footer generation, shared by preview + PDF + DOCX.

The header is the ACTUAL letterhead masthead, cropped from each entity's supplied
letterhead file (app/static/logos/lh_<entity>.png) and placed, as-is, at the top
of every page. The footer is a light single-line address strip for page
continuity. This keeps the on-page letterhead identical to the source documents.
"""
import base64
from pathlib import Path

from flask import current_app
from markupsafe import escape

LOGO_DIR = Path(__file__).resolve().parent.parent / "static" / "logos"

# Bundled masthead image per built-in entity (seeded as "static:<file>").
MASTHEAD_FILE = {
    "fss_usa": "lh_usa.png",
    "fss_hk": "lh_hk.png",
    "fss_uae": "lh_uae.png",
    "fss_korea": "lh_korea.png",
    "estel": "lh_estel.png",
    "estel_usa": "lh_estel_usa.png",
}

_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".gif": "image/gif", ".webp": "image/webp"}


def brand_class(ent):
    return f'brand-{ent.get("brand", "fouress")}'


def _upload_dir():
    return Path(current_app.config["UPLOAD_DIR"])


def masthead_path(ent):
    """Resolve the masthead image path from the entity's letterhead_ref.
    'static:<file>' -> bundled logo; 'upload:<file>' -> file on the data volume.
    Falls back to the bundled file for the entity key if no ref is set."""
    ref = ent.get("letterhead_ref") or ""
    if ref.startswith("upload:"):
        return _upload_dir() / ref[len("upload:"):]
    if ref.startswith("static:"):
        return LOGO_DIR / ref[len("static:"):]
    fname = MASTHEAD_FILE.get(ent.get("key"))
    return LOGO_DIR / fname if fname else None


def masthead_data_uri(ent):
    p = masthead_path(ent)
    if not p or not p.exists():
        return ""
    mime = _MIME.get(p.suffix.lower(), "image/png")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def header_html(ent, masthead_src):
    return (f'<div class="letterhead-header" id="running-header">'
            f'<img class="lh-band" src="{masthead_src}" alt="{escape(ent["legal_name"])} letterhead">'
            f'</div>')


def footer_html(ent):
    parts = [ent["legal_name"]] + ent["address_lines"] + [ent["contact_line"]]
    line = "  |  ".join(escape(p) for p in parts)
    return f'<div class="letterhead-footer" id="running-footer">{line}</div>'
