"""Runtime registry for locations (entities + letterheads + policy handbooks).

The hardcoded data in ``entities.py`` and ``policy_handbooks.py`` are the FACTORY
DEFAULTS. They are seeded into the ``locations`` DB table on first run, after
which the database is the single source of truth — so the Locations admin page
can edit letterheads, legal wording and handbooks, and add whole new countries,
all without touching code.

Everything else in the app (builder, pdf, docx, compliance, routes) reads
entities through this module, never from the raw dicts, so edits and additions
made in the UI flow straight through to generated documents.
"""
import json

from . import entities as _e
from . import policy_handbooks as _ph
from . import letterhead as _lh
from .. import db

# Signatories are not user-managed — pass them straight through.
SIGNATORIES = _e.SIGNATORIES
get_signatory = _e.get_signatory

# The full set of entity fields a location record carries.
ENTITY_FIELDS = (
    "legal_name", "brand", "tagline", "is_fouress", "address_lines",
    "contact_line", "currency", "country", "policy_law_title",
    "policy_law_short", "policy_law_updates", "ncnda_governing_law",
    "ncnda_courts", "restricted_territory_html", "extra_clauses",
)


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------
def seed_if_empty(app):
    """On first run (empty table) seed the 6 built-in entities so they become
    editable. Never re-seeds afterwards, so user edits and deletions persist."""
    with app.app_context():
        if db.count_locations() > 0:
            return
        for i, key in enumerate(_e.ENTITY_ORDER):
            ent = dict(_e.ENTITIES[key])
            label = ent.get("label", key)
            data = {k: ent.get(k) for k in ENTITY_FIELDS if k in ent}
            data.setdefault("extra_clauses", [])
            lh_ref = "static:" + _lh.MASTHEAD_FILE.get(key, "")
            db.upsert_location(key, label, json.dumps(data), letterhead_ref=lh_ref,
                               handbook_html="", is_system=1, sort_order=i,
                               updated_by="seed")


# --------------------------------------------------------------------------
# Entity access
# --------------------------------------------------------------------------
def _row_to_entity(row):
    d = json.loads(row["data_json"])
    d["key"] = row["key"]
    d["label"] = row["label"]
    d["is_system"] = bool(row["is_system"])
    d["letterhead_ref"] = row["letterhead_ref"] or ""
    d["handbook_html"] = row["handbook_html"] or ""
    d.setdefault("extra_clauses", [])
    # defensive defaults so a partially-filled custom location never crashes
    d.setdefault("brand", "fouress")
    d.setdefault("tagline", "")
    d.setdefault("address_lines", [])
    d.setdefault("contact_line", "")
    d.setdefault("currency", "")
    d.setdefault("country", row["key"])
    for k in ("policy_law_title", "policy_law_short", "policy_law_updates",
              "ncnda_governing_law", "ncnda_courts", "restricted_territory_html"):
        d.setdefault(k, "")
    d.setdefault("legal_name", row["label"])
    d.setdefault("is_fouress", d.get("brand") != "estel")
    return d


def _factory_entity(key):
    ent = dict(_e.ENTITIES[key])
    ent["is_system"] = True
    ent["letterhead_ref"] = "static:" + _lh.MASTHEAD_FILE.get(key, "")
    ent["handbook_html"] = ""
    ent.setdefault("extra_clauses", [])
    return ent


def all_entities():
    """Ordered list of entity dicts from the DB (falls back to factory if the
    table has not been seeded yet, e.g. outside an app context)."""
    try:
        rows = db.list_locations()
    except Exception:
        rows = []
    if rows:
        return [_row_to_entity(r) for r in rows]
    return [_factory_entity(k) for k in _e.ENTITY_ORDER]


def get_entity(key):
    try:
        row = db.get_location(key)
    except Exception:
        row = None
    if row:
        return _row_to_entity(row)
    if key in _e.ENTITIES:          # fallback for un-seeded / deleted built-ins
        return _factory_entity(key)
    raise KeyError(f"Unknown entity '{key}'")


def entity_choices():
    return [(e["key"], e["label"]) for e in all_entities()]


def entity_currency_map():
    return {e["key"]: e.get("currency", "") for e in all_entities()}


def entity_country_map():
    return {e["key"]: (e.get("country") or e["key"]) for e in all_entities()}


# --------------------------------------------------------------------------
# Policy handbooks
# --------------------------------------------------------------------------
def policy_locations():
    """Dropdown list: built-in country handbooks + any custom location that
    carries its own handbook, with 'Other — custom' kept last."""
    base = [(k, l) for k, l in _ph.POLICY_LOCATIONS if k != "other"]
    seen = {k for k, _ in base}
    for e in all_entities():
        if e.get("handbook_html") and e["key"] not in seen:
            base.append((e["key"], e["label"]))
            seen.add(e["key"])
    base.append(("other", "Other — custom"))
    return base


def policy_html(location_key, ctx, custom_label=None):
    """Handbook HTML for a policy location. A custom location's own handbook
    wins; otherwise fall back to the built-in country handbooks."""
    if location_key:
        try:
            row = db.get_location(location_key)
        except Exception:
            row = None
        if row and (row["handbook_html"] or "").strip():
            html = row["handbook_html"]
            return (html.replace("__PERSON__", ctx.get("person_noun", "Employee"))
                        .replace("__PAYCAP__", ctx.get("pay_noun_cap", "Salary"))
                        .replace("__PAY__", ctx.get("pay_noun", "salary")))
    return _ph.get_policy_html(location_key, ctx, custom_label)
