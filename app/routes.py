"""Main application routes: form -> generate -> editable preview -> download."""
import json
from datetime import date

from flask import (Blueprint, current_app, render_template, request, redirect,
                   url_for, abort, Response, jsonify, flash)

from .auth import login_required, current_user
from .db import (save_document, get_document, update_document_body, log_audit,
                 recent_audit, recent_documents, list_custom_jds, get_custom_jd,
                 add_custom_jd)
from .documents.builder import build, DOC_TITLES
from .documents.entities import (entity_choices, get_entity, SIGNATORIES,
                                  ENTITIES, ENTITY_ORDER)
from .documents import annexures as annex
from .documents import job_descriptions as jd
from .documents import policy_handbooks as ph
from .documents import letterhead as lh
from .documents.compliance import validate, sanitize
from .emailer import send_download_notification

bp = Blueprint("main", __name__)


def _capture_custom_jd(form, body_html):
    """If this doc used a brand-new custom job title, save its (edited) Job
    Responsibilities so the title becomes reusable next time."""
    if form.get("job_key"):
        return
    role = (form.get("role") or "").strip()
    if not role or form.get("doc_type") not in ("offer_letter", "service_agreement"):
        return
    known = {t.lower() for _, t in jd.specific_choices()} | {t.lower() for _, t in jd.generic_choices()}
    if role.lower() in known:
        return
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(body_html, "html.parser")
        block = soup.select_one('.annex-body[data-jd-kind="responsibilities"] .doc-region')
        if block is None:
            return
        html = block.decode_contents().strip()
        if len(html) > 40:
            add_custom_jd(role, html, current_user())
    except Exception:
        pass



@bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    entity_currency = {k: ENTITIES[k]["currency"] for k in ENTITY_ORDER}
    entity_country = {k: ENTITIES[k].get("country", "other") for k in ENTITY_ORDER}
    return render_template(
        "dashboard.html",
        entities=entity_choices(),
        entity_currency=entity_currency,
        entity_country=entity_country,
        policy_locations=ph.POLICY_LOCATIONS,
        signatories=SIGNATORIES,
        annex_catalogue=annex.ANNEXURE_CATALOGUE,
        jd_groups=jd.grouped_choices(),
        jd_saved=[("saved::" + r["title"], r["title"]) for r in list_custom_jds()],
        jd_custom=jd.CUSTOM_VALUE,
        today=date.today().isoformat(),
        recent=recent_documents(10),
    )


def _parse_form():
    f = request.form
    doc_type = f.get("doc_type")
    # job title -> role + (optional) responsibilities html
    jtk = f.get("job_title_key", "")
    resp_html = None
    if not jtk or jtk == jd.CUSTOM_VALUE:
        role_val = f.get("role_custom", "").strip() or f.get("role", "").strip()
        job_key = ""
    elif jtk.startswith("saved::"):
        role_val = jtk[len("saved::"):]
        resp_html = get_custom_jd(role_val)
        job_key = jtk
    else:
        role_val = jd.get_title(jtk) or f.get("role_custom", "").strip()
        resp_html = jd.get_html(jtk)
        job_key = jtk
    entity_key = f.get("entity")
    policy_location = f.get("policy_location", "").strip() or (
        ENTITIES.get(entity_key, {}).get("country", "") if entity_key else "")
    employment = f.get("employment") or (
        "contractor" if doc_type == "service_agreement" else "employee")
    selected = f.getlist("annex")
    is_contractor = employment == "contractor"
    annexes = []
    for c in annex.ANNEXURE_CATALOGUE:
        if c["kind"] in selected:
            title = f.get(f"annex_title_{c['kind']}") or annex.default_title(
                c["kind"], is_contractor)
            annexes.append({"kind": c["kind"], "title": title})
    annexes = annexes[:5]
    return {
        "doc_type": doc_type,
        "entity": entity_key,
        "policy_location": policy_location,
        "candidate": f.get("candidate", "").strip(),
        "role": role_val,
        "job_key": job_key,
        "responsibilities_html": resp_html,
        "employment": employment,
        "pay_amount": f.get("pay_amount", "").strip(),
        "pay_currency": f.get("pay_currency", "").strip(),
        "start_date": f.get("start_date", "").strip(),
        "probation": f.get("probation", "").strip(),
        "reporting_manager": f.get("reporting_manager", "").strip(),
        "work_location": f.get("work_location", "").strip(),
        "work_mode": f.get("work_mode", "onsite"),
        "territory": (f.get("territory_custom", "").strip()
                      if f.get("territory", "").strip() == "__custom__"
                      else f.get("territory", "").strip()),
        "passport": f.get("passport", "").strip(),
        "industry": (f.get("industry_custom", "").strip() or "Other"
                     if f.get("industry", "").strip() == "Other"
                     else f.get("industry", "").strip()),
        "product_name": f.get("product_name", "").strip(),
        "id_number": f.get("id_number", "").strip(),
        "notice_period_days": f.get("notice_period_days", "").strip(),
        "expected_salary": f.get("expected_salary", "").strip(),
        "current_salary": f.get("current_salary", "").strip(),
        "signatory": f.get("signatory", "swarit"),
        "agreement_date": f.get("agreement_date", "").strip(),
        "letter_date": f.get("letter_date", "").strip() or date.today().isoformat(),
        "annexures": annexes,
    }


@bp.route("/generate", methods=["POST"])
@login_required
def generate():
    form = _parse_form()
    if not form["doc_type"] or not form["entity"] or not form["candidate"]:
        flash("Document type, entity and candidate name are required.", "error")
        return redirect(url_for("main.dashboard"))

    built = build(form)
    doc_id = save_document(current_user(), built["meta"], built["body_html"],
                           status="draft")
    log_audit(current_user(), "GENERATED", document_id=doc_id,
              doc_type=form["doc_type"], candidate=form["candidate"],
              entity_label=built["meta"]["entity_label"])

    ent = get_entity(form["entity"])
    lettered = built.get("letterhead", True)
    return render_template(
        "preview.html",
        doc_id=doc_id,
        title=built["title"],
        body_html=built["body_html"],
        required_tags=json.dumps(built["required_tags"]),
        filename_stub=built["filename_stub"],
        ent=ent,
        letterhead=lettered,
        brand_class=lh.brand_class(ent),
        header_html=(lh.header_html(ent, url_for(
            "static", filename=f"logos/{lh.MASTHEAD_FILE[ent['key']]}")) if lettered else ""),
        footer_html=(lh.footer_html(ent) if lettered else ""),
    )


@bp.route("/document/<int:doc_id>/download/<fmt>", methods=["POST"])
@login_required
def download(doc_id, fmt):
    doc = get_document(doc_id)
    if not doc:
        abort(404)
    if fmt not in ("pdf", "docx"):
        abort(400)

    form = json.loads(doc["form_json"])
    built = build(form)                      # deterministic -> required_tags + filename
    lettered = built.get("letterhead", True)
    posted = request.form.get("body_html") or doc["body_html"]
    posted = sanitize(posted)

    ok, errors = validate(form["entity"], built["required_tags"], posted)
    if not ok:
        return jsonify({"ok": False, "errors": errors}), 422

    update_document_body(doc_id, posted, status="finalised")
    _capture_custom_jd(form, posted)
    filename = f"{built['filename_stub']}.{fmt}"

    if fmt == "pdf":
        from .render.pdf import render_pdf
        data = render_pdf(form["entity"], posted, current_app.config["PAGE_SIZE"],
                          letterhead=lettered)
        mimetype = "application/pdf"
        log_audit(current_user(), "DOWNLOAD_PDF", document_id=doc_id,
                  doc_type=form["doc_type"], candidate=doc["candidate"],
                  entity_label=doc["entity_label"], detail=filename)
        sent, detail = send_download_notification(
            doc_type=form["doc_type"], candidate=doc["candidate"],
            entity_label=doc["entity_label"], downloaded_by=current_user(),
            filename=filename)
        log_audit(current_user(), "EMAIL_SENT" if sent else "EMAIL_FAILED",
                  document_id=doc_id, doc_type=form["doc_type"],
                  candidate=doc["candidate"], entity_label=doc["entity_label"],
                  detail=detail)
    else:
        from .render.docx_render import render_docx
        data = render_docx(form["entity"], posted, letterhead=lettered)
        mimetype = ("application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document")
        log_audit(current_user(), "DOWNLOAD_DOCX", document_id=doc_id,
                  doc_type=form["doc_type"], candidate=doc["candidate"],
                  entity_label=doc["entity_label"], detail=filename)

    return Response(data, mimetype=mimetype, headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })


@bp.route("/audit")
@login_required
def audit():
    return render_template("audit.html", rows=recent_audit(300))


@bp.route("/healthz")
def healthz():
    return {"status": "ok"}
