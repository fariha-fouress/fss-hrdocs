"""
Compliance guards applied at finalise time, before any PDF/DOCX is produced.

1. required-tag check  -> every compliance clause generated for this document
   (locked clauses like probation / FLSA / independent-contractor, plus the
   annexure acknowledgements and any required-editable clause such as the NCNDA
   restricted territory) must still be present in the submitted HTML. If a user
   somehow strips one out, the render is refused.

2. ESTEL isolation     -> a document for the independent ESTEL brand must never
   contain the string "fouress" anywhere.

3. light sanitisation  -> strip <script> tags and inline event handlers from the
   user-edited HTML before it is stored / rendered.
"""
import re

from .registry import get_entity

_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)
_ON_ATTR_RE = re.compile(r'\son\w+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', re.I)
_JS_HREF_RE = re.compile(r'(href|src)\s*=\s*("|\')\s*javascript:[^"\']*(\2)', re.I)


def sanitize(html):
    html = _SCRIPT_RE.sub("", html or "")
    html = _ON_ATTR_RE.sub("", html)
    html = _JS_HREF_RE.sub(r'\1=\2#\2', html)
    return html


def validate(entity_key, required_tags, body_html):
    """Return (ok: bool, errors: list[str])."""
    errors = []
    html = body_html or ""

    for tag in required_tags:
        if f'data-comp="{tag}"' not in html:
            errors.append(f"Required compliance clause '{tag}' is missing — it may not be "
                          f"deleted from the document.")

    ent = get_entity(entity_key)
    if not ent["is_fouress"]:
        if re.search(r"fouress", html, re.I):
            errors.append("ESTEL documents must not reference 'Fouress Synergy' anywhere. "
                          "Please remove the reference before downloading.")

    return (len(errors) == 0, errors)
