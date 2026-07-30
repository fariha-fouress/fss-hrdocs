"""
Document builder — turns a validated form dict into the editable document HTML
plus the list of compliance tags that must survive editing.

Returns a dict:
    {
      "title": str,
      "body_html": str,          # inner HTML for the #document content area
      "required_tags": [str],    # data-comp tags that must be present at finalise
      "letterhead": bool,        # False for NCNDA (plain document, per samples)
      "meta": {...},
      "filename_stub": str,
    }
"""
import re
from datetime import date

from .entities import get_entity, get_signatory
from . import annexures as annex
from . import job_descriptions as jd
from .render_blocks import (editable, locked, esc, h, p, numbered_term,
                            compensation_table, signature_block,
                            acknowledgement_block, ROMAN)

DOC_TITLES = {
    "offer_letter": "Offer Letter",
    "service_agreement": "Service Agreement",
    "ncnda": "Non-Disclosure & Non-Competition Agreement",
}
DOC_FILE = {
    "offer_letter": "OfferLetter",
    "service_agreement": "ServiceAgreement",
    "ncnda": "NCNDA",
}


def _first_name(candidate):
    toks = re.sub(r"^(Mr\.?|Ms\.?|Mrs\.?|Dr\.?)\s+", "", (candidate or "").strip(),
                  flags=re.I).split()
    return toks[0] if toks else (candidate or "Candidate")


def _sanitize(s):
    return re.sub(r"[^A-Za-z0-9]+", "", (s or "")) or "NA"


def _work_mode_line(form):
    mode = (form.get("work_mode") or "onsite").capitalize()
    loc = form.get("work_location") or "[work location]"
    return mode, loc


def build(form):
    doc_type = form["doc_type"]
    ent = get_entity(form["entity"])
    if doc_type == "offer_letter":
        result = _offer_letter(form, ent)
    elif doc_type == "service_agreement":
        result = _service_agreement(form, ent)
    elif doc_type == "ncnda":
        result = _ncnda(form, ent)
    else:
        raise ValueError(f"Unknown doc_type {doc_type}")

    # NCNDAs are plain documents (no company letterhead), matching the samples.
    result["letterhead"] = doc_type != "ncnda"

    today = form.get("letter_date") or date.today().isoformat()
    result["filename_stub"] = "_".join([
        DOC_FILE[doc_type], _sanitize(form.get("candidate")),
        _sanitize(ent["label"]), today,
    ])
    result["meta"] = {
        "doc_type": doc_type,
        "entity": ent["key"],
        "entity_label": ent["label"],
        "candidate": form.get("candidate", ""),
        "role": form.get("role", ""),
        "employment": form.get("employment", ""),
        "signatory": form.get("signatory", ""),
        "form": form,
    }
    return result


# ==========================================================================
# ANNEXURES (shared)
# ==========================================================================
def _render_annexures(form, ent, person_noun, pay_noun, pay_noun_cap):
    chosen = form.get("annexures") or []
    if not chosen:
        return "", []
    contact_email = ("admin@estel-energy.com" if not ent["is_fouress"]
                     else "admin@fouressynergy.com")
    ctx = {
        "person_noun": person_noun,
        "pay_noun": pay_noun,
        "pay_noun_cap": pay_noun_cap,
        "currency": form.get("pay_currency") or ent["currency"],
        "policy_law_title": ent["policy_law_title"],
        "policy_law_short": ent["policy_law_short"],
        "policy_law_updates": ent["policy_law_updates"],
        "contact_email": contact_email,
    }
    tags = []
    out = []
    candidate = form.get("candidate", "")
    for i, a in enumerate(chosen[:5], start=1):
        roman = ROMAN[i]
        kind = a.get("kind", "blank")
        title = a.get("title") or annex.default_title(kind, person_noun == "Service Provider")
        if kind == "responsibilities" and form.get("job_key"):
            body = a.get("body") or jd.get_html(form["job_key"]) or annex.body_html(kind, ctx)
        else:
            body = a.get("body") or annex.body_html(kind, ctx)
        ack = acknowledgement_block(candidate, roman, title, person_noun)
        tags.append(f"ANNEX_ACK_{roman}")
        section = (
            f'<section class="annex" data-annex="{i}">'
            + f'<div class="annex-head">{editable(h(f"Annexure {roman} — {title}", 2))}</div>'
            + f'<div class="annex-body">{editable(body)}</div>'
            + ack
            + '</section>'
        )
        out.append(section)
    return "".join(out), tags


# ==========================================================================
# OFFER LETTER  (employee)
# ==========================================================================
def _offer_letter(form, ent):
    sig = get_signatory(form.get("signatory", "swarit"))
    cur = form.get("pay_currency") or ent["currency"]
    candidate = form.get("candidate", "")
    role = form.get("role", "[role/title]")
    mode, loc = _work_mode_line(form)
    probation = form.get("probation") or "sixty (60) days"
    tags = []

    header = editable(
        f'<p><strong>Date:</strong> {esc(form.get("letter_date") or date.today().isoformat())}</p>'
        f'<p><strong>To:</strong> {esc(candidate)}'
        + (f'<br><strong>Passport No.:</strong> {esc(form.get("passport"))}' if form.get("passport") else "")
        + f'</p>'
        f'<p><strong>Appointment for:</strong> {esc(role)}</p>'
        f'<p>Dear {esc(_first_name(candidate))},</p>'
        f'<p>We are pleased to serve this appointment letter to you under the following '
        f'terms and conditions:</p>'
    )

    terms = []
    terms.append(editable(numbered_term(1, "Designation", esc(role))))
    terms.append(editable(numbered_term(2, "Reporting Office", esc(loc))))
    if form.get("territory"):
        terms.append(editable(numbered_term(3, "Territory", esc(form["territory"]))))
    terms.append(editable(numbered_term(4, "Date of Joining",
                                        esc(form.get("start_date") or "[start date]"))))
    if form.get("reporting_manager"):
        terms.append(editable(numbered_term(5, "Reporting Manager", esc(form["reporting_manager"]))))
    amt = form.get("pay_amount") or "[amount]"
    terms.append(editable(compensation_table(cur, [("Basic", amt), ("Total", amt)],
                                             pay_label="Compensation")))
    terms.append(editable(numbered_term(
        6, "Work Arrangement",
        f'This is a <strong>{esc(mode)}</strong> position. Work location: {esc(loc)}.')))
    terms.append(editable(numbered_term(
        7, "Working Hours & Schedule",
        "44 hours per week (excluding breaks) — Monday to Saturday.")))
    terms.append(editable(numbered_term(
        8, "Leave & Public Holiday Entitlements",
        f"As per applicable law (please refer to the Company Policy annexure).")))

    terms.append(locked(numbered_term(
        9, "Probation",
        f'You will be on probation for a period of {esc(probation)} from your date of joining. '
        f'This probation clause forms part of the terms of employment and may not be removed.'),
        comp="PROBATION"))
    tags.append("PROBATION")

    terms.append(editable(numbered_term(
        10, "Notice Period",
        "During probation, 24 hours by either party; 30 calendar days post-probation by "
        "either party, or payment in lieu.")))
    terms.append(editable(numbered_term(
        11, "Contract Term",
        "Limited fixed term for two (2) years from the effective date, renewable by mutual "
        "agreement.")))
    terms.append(editable(numbered_term(
        12, "BYOD (Bring Your Own Device)",
        "You are required to utilise your personal electronic devices for work purposes as "
        "needed (please refer to the Company Technology & Data Security Policy annexure).")))

    if ent["key"] == "fss_usa":
        terms.append(locked(numbered_term(
            13, "Overtime (FLSA)",
            'To the extent you are classified as a non-exempt employee under the U.S. Fair '
            'Labor Standards Act (FLSA), you are entitled to overtime pay at one-and-one-half '
            '(1.5) times your regular rate of pay for hours worked in excess of forty (40) in a '
            'workweek, in accordance with the FLSA and applicable State law.'),
            comp="FLSA_OVERTIME"))
        tags.append("FLSA_OVERTIME")
        terms.append(locked(numbered_term(
            14, "Employment Eligibility & Work Authorization",
            'This offer is contingent upon your legal authorization to work in the United '
            'States. You must present valid Employment Authorization Document (EAD) / '
            'work-authorization evidence and complete Form I-9 employment eligibility '
            'verification. Continued employment is conditional upon maintaining valid U.S. work '
            'authorization at all times.'),
            comp="EAD"))
        tags.append("EAD")

    closing = editable(
        f'<p>All other terms and conditions of employment not explicitly stated in this offer '
        f'letter shall be governed by, and subject to, {ent["policy_law_short"]}.</p>'
        f'<p>We welcome you to {esc(ent["legal_name"])} and look forward to a fruitful '
        f'association. Please sign and return a copy of this letter as confirmation of your '
        f'acceptance. By accepting this appointment letter, you also confirm your acceptance of '
        f'the Annexures to this letter and the Company\'s policies.</p>'
    )

    sigblock = locked(signature_block(
        ent["legal_name"], sig, party_label="Employee",
        candidate=candidate, passport=form.get("passport", ""), designation=role),
        comp="SIGNATURE")
    tags.append("SIGNATURE")

    annex_html, annex_tags = _render_annexures(form, ent, "Employee", "salary", "Salary")
    tags += annex_tags

    body = (f'<section class="main">{header}{"".join(terms)}{closing}{sigblock}</section>'
            + annex_html)
    return {"title": DOC_TITLES["offer_letter"], "body_html": body, "required_tags": tags}


# ==========================================================================
# SERVICE AGREEMENT  (contractor)
# ==========================================================================
def _service_agreement(form, ent):
    sig = get_signatory(form.get("signatory", "swarit"))
    cur = form.get("pay_currency") or ent["currency"]
    candidate = form.get("candidate", "")
    role = form.get("role", "[role/title]")
    mode, loc = _work_mode_line(form)
    tags = []

    header = editable(
        f'<h2 class="doc-title">SERVICE AGREEMENT</h2>'
        f'<p>This Service Agreement ("Agreement") is made on '
        f'<strong>{esc(form.get("agreement_date") or form.get("letter_date") or date.today().isoformat())}</strong>,</p>'
        f'<p><strong>Between:</strong><br>{esc(ent["legal_name"])}<br>'
        f'{esc(ent["address_lines"][0])}<br>(hereinafter referred to as the "Company")</p>'
        f'<p><strong>And:</strong><br>{esc(candidate)}<br>'
        + (f'Holder of Passport No.: {esc(form.get("passport"))}<br>' if form.get("passport") else "")
        + f'(hereinafter referred to as the "Service Provider")</p>'
    )

    terms = []
    terms.append(editable(numbered_term(
        1, "Designation & Scope of Services",
        f'Designation: {esc(role)}'
        + (f', focusing on {esc(form.get("territory"))}' if form.get("territory") else "")
        + f'. The Service Provider agrees to provide sales and business development services '
        f'for the Company, commencing on {esc(form.get("start_date") or "[start date]")}, '
        f'managing the complete sales cycle including lead generation, client engagement, '
        f'negotiation, and closing of transactions.')))

    amt = form.get("pay_amount") or "[amount]"
    terms.append(editable(compensation_table(cur, [("Monthly Service Fee", amt)],
                                             pay_label="Compensation")))

    terms.append(locked(
        p('This amount shall be paid as a <strong>service fee</strong> and shall not be '
          'construed as salary, wages, or employment compensation.', raw=True),
        comp="SERVICE_FEE_NOT_SALARY"))
    tags.append("SERVICE_FEE_NOT_SALARY")

    terms.append(locked(numbered_term(
        2, "Taxation",
        'The Service Provider shall be solely responsible for any and all taxes, duties, or '
        'statutory obligations arising from the service fee received under this Agreement in '
        'their home jurisdiction or any other applicable jurisdiction. The Company shall bear '
        'no responsibility for tax deductions, filings, or compliance on behalf of the Service '
        'Provider.'),
        comp="CONTRACTOR_TAX"))
    tags.append("CONTRACTOR_TAX")

    terms.append(editable(numbered_term(
        3, "Working Hours & Schedule",
        "44 hours per week (excluding breaks) — Monday to Saturday.")))
    terms.append(editable(numbered_term(
        4, "Leave & Public Holiday Entitlements",
        "As per applicable law (please refer to the Service Engagement Policy annexure).")))
    terms.append(editable(numbered_term(
        5, "Probation",
        f'{esc(form.get("probation") or "Sixty (60) days")} from the date of commencement.')))
    terms.append(editable(numbered_term(
        6, "Notice Period",
        "24 hours during probation; 30 calendar days post-probation by either party, or "
        "payment in lieu.")))
    terms.append(editable(numbered_term(
        7, "Contract Term",
        "Limited fixed term for two (2) years from the effective date, renewable by mutual "
        "agreement.")))
    terms.append(editable(numbered_term(
        8, "Work Arrangement",
        f'This is a <strong>{esc(mode)}</strong> engagement. Work location: {esc(loc)}.')))
    terms.append(editable(numbered_term(
        9, "BYOD (Bring Your Own Device)",
        "The Service Provider utilises personal electronic devices for work purposes as needed "
        "(please refer to the Company Technology & Data Security Policy annexure).")))

    terms.append(locked(numbered_term(
        10, "Engagement Structure",
        'The individual is engaged as an <strong>independent Service Provider</strong> under a '
        'contractual arrangement. This engagement does <strong>not</strong> constitute an '
        'employer-employee relationship. The Service Provider is responsible for their own '
        'statutory obligations, including taxes and insurance, and is not entitled to employee '
        'benefits.'),
        comp="IC_RELATIONSHIP"))
    tags.append("IC_RELATIONSHIP")

    closing = editable(
        f'<p>All other terms and conditions of service not explicitly stated in this Agreement '
        f'shall be governed by {ent["policy_law_short"]}.</p>'
        f'<p>We welcome you to {esc(ent["legal_name"])} and look forward to a fruitful '
        f'association. Please sign and return a copy of this Agreement as confirmation of your '
        f'acceptance as the Service Provider. By accepting this Agreement, you also confirm your '
        f'acceptance of the Annexures and the Company\'s policies.</p>'
    )

    sigblock = locked(signature_block(
        ent["legal_name"], sig, party_label="Service Provider",
        candidate=candidate, passport=form.get("passport", ""), designation=role),
        comp="SIGNATURE")
    tags.append("SIGNATURE")

    annex_html, annex_tags = _render_annexures(form, ent, "Service Provider",
                                               "service fee", "Service Fee")
    tags += annex_tags

    body = (f'<section class="main">{header}{"".join(terms)}{closing}{sigblock}</section>'
            + annex_html)
    return {"title": DOC_TITLES["service_agreement"], "body_html": body,
            "required_tags": tags}


# ==========================================================================
# NCNDA  (plain document — strictly follows the supplied sample format)
# ==========================================================================
def _ncnda(form, ent):
    sig = get_signatory(form.get("signatory", "swarit"))
    candidate = form.get("candidate", "")
    is_contractor = form.get("employment") == "contractor"
    party = "Service Provider" if is_contractor else "Employee"
    engagement = "engagement" if is_contractor else "employment"
    kind_word = "Service" if is_contractor else "Employment"
    market = form.get("territory", "").strip()
    role = form.get("role", "")
    passport = form.get("passport", "")
    agdate = form.get("agreement_date") or form.get("letter_date") or date.today().isoformat()
    joindate = form.get("start_date", "")
    tags = []

    # ---- Title + Parties table (editable variable fields) ----------------
    parties = editable(
        f'<h2 class="doc-title">NON-DISCLOSURE AND NON-COMPETITION AGREEMENT</h2>'
        f'<p class="subtitle">Confidential — {kind_word} Agreement Annexure</p>'
        f'<h3>Parties to this Agreement</h3>'
        f'<table class="parties-table">'
        f'<tr><td class="pt-key">Company</td><td>{esc(ent["legal_name"])}, '
        f'{esc(ent["address_lines"][0])} (hereinafter referred to as "the Company")</td></tr>'
        f'<tr><td class="pt-key">{party}</td><td>Name: {esc(candidate)}<br>'
        f'Passport No.: {esc(passport)} (hereinafter referred to as "the {party}")</td></tr>'
        f'<tr><td class="pt-key">Designation</td><td>{esc(role)}</td></tr>'
        f'<tr><td class="pt-key">Date of Joining</td><td>{esc(joindate)}</td></tr>'
        f'<tr><td class="pt-key">Agreement Date</td><td>{esc(agdate)}</td></tr>'
        f'</table>'
    )

    ops = f", with operations spanning {esc(market)}" if market else ""
    recitals = editable(
        '<h3>Recitals</h3>'
        '<p>WHEREAS, the Company is engaged in the business of international trading of polymers, '
        f'petrochemical products, agro commodities, and related goods{ops}; and</p>'
        f'<p>WHEREAS, in the course of {engagement}, the {party} will be granted access to '
        'confidential business information, trade secrets, client relationships, supplier '
        'networks, pricing strategies, and other proprietary data belonging to the Company; and</p>'
        '<p>WHEREAS, the Company wishes to protect its legitimate business interests, client '
        'relationships, and confidential information from unauthorised disclosure or competitive '
        'misuse;</p>'
        f'<p>NOW, THEREFORE, in consideration of {engagement} and the benefits arising therefrom, '
        f'the {party} agrees to be bound by the terms and conditions set out in this Agreement.</p>'
    )

    # ---- PART A — NDA (locked) -------------------------------------------
    nda = locked(
        '<h3>Part A — Non-Disclosure Agreement (NDA)</h3>'
        '<p><strong>1. Definition of Confidential Information.</strong> For the purposes of this '
        'Agreement, "Confidential Information" shall mean any and all information, data, '
        'knowledge, or material — whether in written, oral, electronic, or any other form — that '
        f'is disclosed to, obtained by, or accessed by the {party} in connection with their '
        f'{engagement}, including but not limited to:</p>'
        '<ul>'
        '<li><strong>Business &amp; Commercial Data:</strong> client lists, customer databases, '
        'prospect lists, pricing structures, discount policies, contract terms, sales strategies, '
        'revenue figures, and profit margins;</li>'
        '<li><strong>Supplier &amp; Vendor Information:</strong> supplier identities, vendor '
        'agreements, sourcing networks, mill/manufacturer/producer relationships, freight '
        'arrangements, procurement costs, and logistics partnerships;</li>'
        '<li><strong>Operational Information:</strong> internal processes, standard operating '
        'procedures, shipment records, inventory data, quality standards, and internal reporting '
        'systems;</li>'
        '<li><strong>Financial Information:</strong> budgets, forecasts, financial statements, '
        'credit terms, banking details, and investment plans;</li>'
        '<li><strong>Strategic Information:</strong> business development plans, market entry '
        'strategies, new product pipelines, geographic expansion plans, and merger or acquisition '
        'discussions;</li>'
        '<li><strong>Technical Information:</strong> product specifications, testing data, '
        'formulations, research, and proprietary technical knowledge;</li>'
        '<li><strong>Third-Party Information:</strong> any confidential information belonging to '
        'clients, suppliers, or partners disclosed in the course of business.</li>'
        '</ul>'
        f'<p><strong>2. Obligations of Non-Disclosure.</strong> During the term of {engagement} '
        f'and at all times thereafter, the {party} agrees to: hold all Confidential Information '
        'in strict confidence and not disclose it to any third party without the prior written '
        'consent of the Company; use Confidential Information solely for the purpose of performing '
        'duties assigned by the Company; not copy, reproduce, or replicate Confidential '
        'Information except as strictly required; take all reasonable measures to protect it from '
        'unauthorised access, loss, or theft; promptly notify the Company of any actual or '
        'suspected breach; and, upon separation, immediately return or permanently delete all '
        'materials containing Confidential Information.</p>'
        f'<p><strong>3. Duration of Confidentiality Obligation.</strong> The {party}\'s obligation '
        'to maintain confidentiality shall remain in force indefinitely — both during the term of '
        f'{engagement} and following separation from the Company, regardless of the reason for '
        'separation. There is no time limit on the duty to protect trade secrets and core '
        'Confidential Information.</p>',
        comp="CONFIDENTIALITY")
    tags.append("CONFIDENTIALITY")

    # ---- PART B — Non-Competition ----------------------------------------
    noncompete = locked(
        '<h3>Part B — Non-Competition Agreement</h3>'
        f'<p><strong>4. Non-Competition Covenant.</strong> The {party} acknowledges that during '
        f'their {engagement}, they will develop deep familiarity with the Company\'s clients, '
        'suppliers, business strategies, and competitive positioning. In recognition of this, the '
        f'{party} agrees to the following post-{engagement} restrictions:</p>'
        '<p><strong>4.1 Restricted Period.</strong> For a period of two (2) years commencing from '
        'the date of separation from the Company ("the Restricted Period"), regardless of the '
        f'reason for termination or resignation, the {party} shall not, directly or indirectly, '
        'engage in any Restricted Activity (as defined in Clause 4.3) within the Restricted '
        'Territory (as defined in Clause 4.2).</p>',
        comp="NONCOMPETE")
    tags.append("NONCOMPETE")

    if form.get("restricted_territory_html"):
        terr_body = form["restricted_territory_html"]
    elif market:
        terr_body = (f'<p><strong>{esc(market)}</strong></p>'
                     f'<p>The Restricted Territory shall be interpreted as the regions where the '
                     f'Company has demonstrable business operations, active client accounts, or '
                     f'active supplier relationships at the date of the {party}\'s separation.</p>')
    else:
        terr_body = ent["restricted_territory_html"]
    territory = editable(
        '<p><strong>4.2 Restricted Territory.</strong> The non-competition restriction shall '
        'apply to the following geographic regions ("the Restricted Territory"), being the '
        'markets in which the Company actively conducts business:</p>'
        + terr_body,
        comp="RESTRICTED_TERRITORY")
    tags.append("RESTRICTED_TERRITORY")

    activities = locked(
        f'<p><strong>4.3 Restricted Activities.</strong> During the Restricted Period and within '
        f'the Restricted Territory, the {party} shall not, directly or indirectly:</p>'
        '<ul>'
        '<li><strong>Employment with Competitors:</strong> be employed by, work for, consult '
        'with, advise, or provide services to any entity engaged in the trading, distribution, '
        'import, or export of polymers, petrochemical products, commodity chemicals, agro '
        'commodities, or any other product category directly competing with the Company;</li>'
        '<li><strong>Establish Competing Business:</strong> set up, incorporate, own, co-own, or '
        'operate any business that competes directly or indirectly with the Company;</li>'
        '<li><strong>Client Solicitation:</strong> solicit, approach, or attempt to do business '
        f'with any client, customer, or prospect of the Company that the {party} had dealings '
        'with or knowledge of during their engagement;</li>'
        '<li><strong>Supplier Solicitation:</strong> solicit or enter into business arrangements '
        'with any supplier, vendor, freight forwarder, or logistics partner of the Company for the '
        'purpose of competing with the Company;</li>'
        f'<li><strong>Personnel Solicitation:</strong> recruit or induce any current {party.lower()} '
        'or employee of the Company to leave the Company;</li>'
        '<li><strong>Use of Confidential Information for Competition:</strong> use or leverage any '
        'Confidential Information to gain a competitive advantage against the Company.</li>'
        '</ul>'
        '<p><strong>4.4 Permitted Activities.</strong> The restrictions in Clause 4.3 shall not '
        f'prohibit the {party} from working in an industry wholly unrelated to the Company\'s '
        'business, working in the trading or commodity sector entirely outside the Restricted '
        'Territory, or pursuing academic study or non-commercial activities.</p>'
        '<p><strong>5. Reasonableness of Restrictions.</strong> The ' + party + ' acknowledges '
        'that these restrictions are reasonable and necessary to protect the Company\'s legitimate '
        'business interests and confirms that they will not prevent the ' + party.lower() + ' from '
        'earning a livelihood.</p>',
        comp="RESTRICTED_ACTIVITIES")
    tags.append("RESTRICTED_ACTIVITIES")

    # ---- PART C — General -------------------------------------------------
    general = locked(
        '<h3>Part C — General Provisions</h3>'
        '<p><strong>6. Breach and Remedies.</strong> The ' + party + ' acknowledges that any '
        'breach or threatened breach of this Agreement would cause the Company irreparable harm '
        'for which monetary damages alone would be inadequate. Accordingly, the Company shall be '
        'entitled to: seek immediate injunctive relief without the requirement to post a bond or '
        'prove actual damages; claim damages including lost profits and consequential losses; '
        'recover all legal costs incurred in enforcing this Agreement; and pursue any other remedy '
        'available under applicable law. The Restricted Period shall be automatically extended by '
        'a period equal to the duration of any proven breach.</p>'
        '<p><strong>7. Severability.</strong> If any provision is held invalid, unenforceable, or '
        'contrary to applicable law, such provision shall be modified to the minimum extent '
        'necessary to make it enforceable, or severed if modification is not possible, and the '
        'remaining provisions shall continue in full force and effect.</p>',
        comp="REMEDIES")
    tags.append("REMEDIES")

    # Governing law editable so it can be tailored to the country of engagement,
    # but required (cannot be deleted).
    governing = editable(
        '<p><strong>8. Governing Law &amp; Jurisdiction.</strong> This Agreement shall be governed '
        f'by and construed in accordance with {ent["ncnda_governing_law"]}. Any dispute arising '
        f'from or related to this Agreement shall be subject to the exclusive jurisdiction of '
        f'{ent["ncnda_courts"]}. Both parties consent to such jurisdiction and waive any objection '
        'to venue.</p>'
        '<p><strong>9. Entire Agreement.</strong> This Agreement constitutes the entire '
        'understanding between the parties with respect to non-disclosure and non-competition and '
        'supersedes all prior discussions or agreements on the same subject. No modification shall '
        'be effective unless made in writing and signed by both parties.</p>',
        comp="GOVERNING_LAW")
    tags.append("GOVERNING_LAW")

    acknowledgment = locked(
        f'<p><strong>10. Acknowledgment.</strong> The {party} confirms that they have read this '
        'Agreement in full, have had the opportunity to seek independent legal advice, and fully '
        'understand and voluntarily accept the obligations contained herein as a condition of '
        f'{engagement} with {esc(ent["legal_name"])}.</p>',
        comp="ACKNOWLEDGMENT")
    tags.append("ACKNOWLEDGMENT")

    execution = locked(
        '<h3>Execution and Signatures</h3>'
        '<p>This Agreement is executed in two (2) copies, one retained by the Company and one by '
        f'the {party}, both of equal legal force and effect.</p>'
        + signature_block(ent["legal_name"], sig, party_label=party,
                          candidate=candidate, passport=passport, designation=role),
        comp="SIGNATURE")
    tags.append("SIGNATURE")

    body = (f'<section class="main">{parties}{recitals}{nda}{noncompete}{territory}'
            f'{activities}{general}{governing}{acknowledgment}{execution}</section>')
    return {"title": DOC_TITLES["ncnda"], "body_html": body, "required_tags": tags}
