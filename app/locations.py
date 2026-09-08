"""Locations admin: add / edit / delete countries, their letterheads, policy
handbooks and legal rules — all from the browser, no code changes.

Design goals from the brief:
  * Non-technical users manage everything on one organised page.
  * Transparency: every field that flows into a document is shown and editable.
  * Safety: locked compliance clauses are never exposed for deletion here, and
    deleting a location requires typing its exact name to confirm.
  * Persistence: letterhead images are stored on the data volume; all config is
    stored in the database (see registry.py).
"""
import io
import json
import os
import re
import time

from flask import (Blueprint, current_app, render_template, request, redirect,
                   url_for, abort, flash, send_file, Response)

from .auth import login_required, current_user
from . import db
from .documents import registry as reg
from .documents import letterhead as lh

bp = Blueprint("locations", __name__)

ALLOWED_IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
ALLOWED_DOC = {".docx", ".pdf", ".txt", ".html", ".htm"}

DOC_TYPE_LABELS = [
    ("all", "All documents"),
    ("offer_letter", "Offer Letter only"),
    ("service_agreement", "Service Agreement only"),
    ("ncnda", "NCNDA only"),
]


def _slug(text):
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").strip().lower()).strip("_")
    return s or ("loc_" + str(int(time.time())))


def _unique_key(base):
    key = base
    n = 2
    while db.get_location(key) is not None:
        key = f"{base}_{n}"
        n += 1
    return key


def _extract_handbook(storage):
    """Turn an uploaded .docx/.pdf/.txt/.html handbook into simple editable HTML."""
    name = (storage.filename or "").lower()
    ext = os.path.splitext(name)[1]
    raw = storage.read()
    if ext == ".docx":
        from docx import Document
        d = Document(io.BytesIO(raw))
        out = []
        for p in d.paragraphs:
            t = p.text.strip()
            if not t:
                continue
            style = (p.style.name or "").lower() if p.style else ""
            if "heading" in style:
                out.append(f"<p><strong>{_esc(t)}</strong></p>")
            else:
                out.append(f"<p>{_esc(t)}</p>")
        return "\n".join(out)
    if ext == ".pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(stream=raw, filetype="pdf")
        out = []
        for page in doc:
            for line in page.get_text().splitlines():
                t = line.strip()
                if t:
                    out.append(f"<p>{_esc(t)}</p>")
        return "\n".join(out)
    if ext in (".html", ".htm"):
        return raw.decode("utf-8", "ignore")
    # plain text
    text = raw.decode("utf-8", "ignore")
    return "\n".join(f"<p>{_esc(l.strip())}</p>" for l in text.splitlines() if l.strip())


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --------------------------------------------------------------------------
@bp.route("/locations")
@login_required
def index():
    reg_list = reg.all_entities()
    return render_template("locations.html", locations=reg_list)


@bp.route("/locations/new")
@login_required
def new():
    blank = {
        "key": "", "label": "", "is_system": False, "brand": "fouress",
        "is_fouress": True, "legal_name": "", "tagline": "", "currency": "",
        "country": "", "address_lines": [], "contact_line": "",
        "policy_law_title": "", "policy_law_short": "", "policy_law_updates": "",
        "ncnda_governing_law": "", "ncnda_courts": "",
        "restricted_territory_html": "", "handbook_html": "", "extra_clauses": [],
        "letterhead_ref": "", "address_text": "",
    }
    return render_template("location_form.html", loc=blank, mode="new",
                           doc_types=DOC_TYPE_LABELS)


@bp.route("/locations/<key>/edit")
@login_required
def edit(key):
    row = db.get_location(key)
    if row is None:
        if key in reg._e.ENTITIES:          # un-seeded built-in — materialise it
            reg.seed_if_empty(current_app)
            row = db.get_location(key)
        if row is None:
            abort(404)
    loc = reg._row_to_entity(row)
    loc["address_text"] = "\n".join(loc.get("address_lines") or [])
    return render_template("location_form.html", loc=loc, mode="edit",
                           doc_types=DOC_TYPE_LABELS)


@bp.route("/locations/save", methods=["POST"])
@login_required
def save():
    f = request.form
    mode = f.get("mode", "new")
    label = (f.get("label") or "").strip()
    if not label:
        flash("Location name is required.", "error")
        return redirect(url_for("locations.new"))

    if mode == "edit":
        key = f.get("key", "").strip()
        existing = db.get_location(key)
        is_system = int(existing["is_system"]) if existing else 0
        sort_order = int(existing["sort_order"]) if existing else 100
        country = (f.get("country") or "").strip() or (
            json.loads(existing["data_json"]).get("country") if existing else key) or key
    else:
        key = _unique_key(_slug(f.get("key") or label))
        is_system = 0
        sort_order = (db.count_locations() or 0) + 100
        country = (f.get("country") or "").strip() or key

    brand = (f.get("brand") or "fouress").strip().lower()
    address_lines = [l.strip() for l in (f.get("address_lines") or "").splitlines() if l.strip()]

    extra = []
    for i in range(6):
        title = (f.get(f"extra_title_{i}") or "").strip()
        body = (f.get(f"extra_body_{i}") or "").strip()
        if title and body:
            extra.append({"doc": f.get(f"extra_doc_{i}", "all"), "title": title, "body": body})

    data = {
        "legal_name": (f.get("legal_name") or label).strip(),
        "brand": brand,
        "tagline": (f.get("tagline") or "").strip(),
        "is_fouress": brand != "estel",
        "currency": (f.get("currency") or "").strip(),
        "country": country,
        "address_lines": address_lines,
        "contact_line": (f.get("contact_line") or "").strip(),
        "policy_law_title": (f.get("policy_law_title") or "").strip(),
        "policy_law_short": (f.get("policy_law_short") or "").strip(),
        "policy_law_updates": (f.get("policy_law_updates") or "").strip(),
        "ncnda_governing_law": (f.get("ncnda_governing_law") or "").strip(),
        "ncnda_courts": (f.get("ncnda_courts") or "").strip(),
        "restricted_territory_html": (f.get("restricted_territory_html") or "").strip(),
        "extra_clauses": extra,
    }

    # handbook: uploaded file wins over the textarea, else keep existing on edit
    handbook_html = (f.get("handbook_html") or "").strip()
    hb_file = request.files.get("handbook_file")
    if hb_file and hb_file.filename:
        ext = os.path.splitext(hb_file.filename.lower())[1]
        if ext not in ALLOWED_DOC:
            flash(f"Handbook file type {ext} not supported. Use .docx, .pdf, .txt or .html.", "error")
            return redirect(url_for("locations.edit", key=key) if mode == "edit" else url_for("locations.new"))
        try:
            handbook_html = _extract_handbook(hb_file)
            flash("Handbook imported from file — review and edit the text as needed.", "success")
        except Exception as exc:  # noqa
            flash(f"Could not read the handbook file: {exc}", "error")

    # letterhead upload (optional)
    letterhead_ref = None
    up = request.files.get("letterhead_file")
    if up and up.filename:
        ext = os.path.splitext(up.filename.lower())[1]
        if ext not in ALLOWED_IMG:
            flash(f"Letterhead image type {ext} not supported. Use PNG or JPG.", "error")
            return redirect(url_for("locations.edit", key=key) if mode == "edit" else url_for("locations.new"))
        updir = current_app.config["UPLOAD_DIR"]
        os.makedirs(updir, exist_ok=True)
        fname = f"lh_{key}_{int(time.time())}{ext}"
        up.save(os.path.join(updir, fname))
        letterhead_ref = "upload:" + fname

    db.upsert_location(key, label, json.dumps(data), letterhead_ref=letterhead_ref,
                       handbook_html=handbook_html, is_system=is_system,
                       sort_order=sort_order, updated_by=current_user() or "")
    db.log_audit(current_user(), "LOCATION_SAVED", entity_label=label, detail=key)
    flash(f"Location “{label}” saved.", "success")
    return redirect(url_for("locations.index"))


@bp.route("/locations/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    row = db.get_location(key)
    if row is None:
        abort(404)
    typed = (request.form.get("confirm_name") or "").strip()
    if typed != row["label"]:
        flash("Deletion cancelled — the name you typed did not match exactly.", "error")
        return redirect(url_for("locations.edit", key=key))
    db.delete_location(key)
    db.log_audit(current_user(), "LOCATION_DELETED", entity_label=row["label"], detail=key)
    flash(f"Location “{row['label']}” deleted.", "success")
    return redirect(url_for("locations.index"))


@bp.route("/media/letterhead/<key>")
@login_required
def letterhead_media(key):
    try:
        ent = reg.get_entity(key)
    except KeyError:
        abort(404)
    p = lh.masthead_path(ent)
    if not p or not p.exists():
        abort(404)
    return send_file(str(p))
