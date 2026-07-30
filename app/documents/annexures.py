"""
Default annexure content, matched to the supplied sample templates.

Every annexure body here is a *pre-filled editable default*. The user may
reword or replace it entirely in the preview. The heading title is editable
too. The acknowledgement block is appended automatically by the builder and is
locked.

Annexure "kinds":
    sales_incentive   - suggested only for sales roles
    responsibilities  - Job Responsibilities (employee) / Scope of Work (contractor)
    policy            - Company Policy Handbook (employee) / Service Engagement Policy (contractor)
    tech_security     - Company Technology & Data Security Policy
    blank             - empty free-text annexure the user fills in
"""

# Catalogue used by the form to offer choices + defaults.
ANNEXURE_CATALOGUE = [
    {"kind": "sales_incentive", "title": "Sales Incentive Structure",
     "sales_only": True},
    {"kind": "responsibilities", "title": "Job Responsibilities",
     "title_contractor": "Scope of Work"},
    {"kind": "policy", "title": "Company Policy Handbook",
     "title_contractor": "Service Engagement Policy"},
    {"kind": "tech_security", "title": "Company Technology & Data Security Policy"},
    {"kind": "blank", "title": "Additional Annexure"},
]


def default_title(kind, is_contractor):
    for c in ANNEXURE_CATALOGUE:
        if c["kind"] == kind:
            if is_contractor and c.get("title_contractor"):
                return c["title_contractor"]
            return c["title"]
    return "Annexure"


def suggested_kinds(doc_type, role, entity):
    """Default suggestions by logic (all remain editable/removable in the UI)."""
    role_l = (role or "").lower()
    is_sales = "sales" in role_l or "business development" in role_l
    kinds = []
    if is_sales:
        kinds.append("sales_incentive")
    kinds.append("responsibilities")
    kinds.append("policy")           # per-entity company policy handbook
    kinds.append("tech_security")    # per-entity tech & data security policy
    return kinds[:5]


def body_html(kind, ctx):
    """ctx: dict with person_noun, pay_noun, pay_noun_cap, currency,
    policy_law_title, policy_law_short, policy_law_updates, contact_email."""
    fn = _BUILDERS.get(kind)
    return fn(ctx) if fn else "<p>[ Type or paste the content of this annexure here. ]</p>"


# --------------------------------------------------------------------------
def _sales_incentive(ctx):
    cur = ctx["currency"]
    return f"""
<ul>
  <li><strong>Qualifying Threshold:</strong> Incentives apply only on sales volumes exceeding
      a cumulative quarterly baseline of 3,000 MT (average 1,000 MT/month). Disbursement is
      subject to full realization of client payments into the Company's bank account.</li>
</ul>
<p><strong>Incentive Slabs — Calculated Quarterly</strong></p>
<ul>
  <li>Average up to 2,000 MT/month: USD 0.75 per MT</li>
  <li>Average up to 2,500 MT/month: USD 1.00 per MT</li>
  <li>Average up to 3,500 MT/month: USD 1.50 per MT</li>
  <li>Average 3,501 MT/month and above: USD 2.00 per MT</li>
</ul>
<p>The flat rate of the highest slab reached applies to all eligible volume above the
   3,000 MT quarterly baseline.</p>
<p><strong>Currency &amp; Payout Conditions</strong></p>
<ul>
  <li>Currency: Calculated in USD, paid in {cur}.</li>
  <li>Payout Frequency: Quarterly, following realization of client payments.</li>
</ul>
<p><strong>Separation Clause</strong></p>
<ul>
  <li>All dues settled at the time of separation / termination of the engagement.</li>
  <li>No liability for unrealized payments post-separation.</li>
</ul>"""


def _responsibilities(ctx):
    return """
<p>Your key responsibilities will include but are not limited to:</p>
<ul>
  <li><strong>Business Development &amp; Sales Growth:</strong> Identify and develop new
      business opportunities across the assigned territory.</li>
  <li><strong>Client Relationship Management:</strong> Maintain strong relationships with
      existing key accounts and ensure high customer satisfaction.</li>
  <li><strong>Market Expansion &amp; New Client Acquisition:</strong> Develop and execute
      strategies for new client acquisition; explore new geographical markets and
      distribution channels; participate in trade exhibitions and industry conferences;
      establish partnerships with manufacturers, suppliers, and agents.</li>
  <li><strong>Commercial &amp; Pricing Management:</strong> Prepare and negotiate commercial
      proposals, pricing structures, and contracts; monitor market pricing trends and
      supply-demand dynamics; coordinate with procurement and supply chain teams; maintain
      profitability margins as per company targets.</li>
  <li><strong>Sales Operations &amp; Reporting:</strong> Maintain accurate sales forecasts,
      pipelines, and CRM records; prepare monthly, quarterly, and annual sales reports;
      analyze performance data and implement corrective action plans.</li>
  <li><strong>Coordination &amp; Cross-Functional Management:</strong> Coordinate with
      logistics, finance, operations, and procurement teams; ensure timely delivery
      schedules; support finance in receivables management and overdue recovery.</li>
</ul>
<p>A detailed explanation of your duties will be provided during the onboarding process.</p>"""


def _policy(ctx):
    person = ctx["person_noun"]
    pay = ctx["pay_noun"]          # "salary" / "service fee"
    law_title = ctx["policy_law_title"]
    law_updates = ctx["policy_law_updates"]
    return f"""
<p class="annex-lawline"><strong>{law_title}</strong></p>
<p><strong>1. Attendance, Punctuality &amp; Tardiness</strong></p>
<ul>
  <li>Desktop Readiness: All {person.lower()}s must be logged in and ready by 9:00 AM sharp.</li>
  <li>Tardiness Deduction Tiers: 9:01–9:15 AM — three late arrivals in one calendar month
      trigger a 1/4-day {pay} deduction on the 3rd occurrence; 9:16–9:30 AM — 1/4-day
      deduction per occurrence; 9:31–11:00 AM — 1/2-day deduction per occurrence; after
      11:00 AM — full-day deduction; excessive lateness (6+ in a month) — additional
      full-day deduction.</li>
  <li>Leave Balance Adjustments: Accrued Annual Leave may be applied for short or half-day
      absences; deductions apply where no AL balance is available.</li>
</ul>
<p><strong>2. Daily Breaks</strong></p>
<ul><li>Monday–Friday: 1 hour total per day (may be split into two breaks, not exceeding 1 hour in total).</li></ul>
<p><strong>3. Leave Framework</strong></p>
<ul>
  <li>Annual Leave, Sick Leave, Maternity/Paternity, Bereavement and other statutory leave
      are granted in accordance with {law_updates}. [Adjust the specific day entitlements
      for this jurisdiction as required.]</li>
  <li>Emergency Leave during probation or before completion of one (1) year of continuous
      service will not be approved except for emergencies vetted by executive management.</li>
</ul>
<p><strong>4. {ctx['pay_noun_cap']} Administration</strong></p>
<ul>
  <li>Payment processed and transferred between the 5th and 10th of each calendar month.</li>
  <li>Pay slips available on written request to HR with 5 business days' prior notice.</li>
</ul>
<p><strong>5. Performance, Conduct &amp; Non-Compete</strong></p>
<ul>
  <li>Performance Reviews: Ongoing KPI tracking; persistent underperformance may result in a
      formal Performance Improvement Plan (PIP).</li>
  <li>Disciplinary Action: Progressive action — formal warning &rarr; {pay} deduction &rarr;
      suspension &rarr; termination.</li>
  <li>Work Ethics: Maintain professional integrity, commercial transparency, and strict data
      confidentiality in all client and company dealings.</li>
  <li>Non-Compete: Please refer to the NCNDA Agreement.</li>
</ul>
<p><strong>6. BYOD (Bring Your Own Device)</strong></p>
<ul>
  <li>Personal devices used for Company business must meet minimum security standards
      (up-to-date OS, encryption, active antivirus).</li>
  <li>The Company may require MDM software on personal devices; the {person} consents to this
      as a condition of BYOD authorization.</li>
  <li>Company data on personal devices may be remotely wiped upon separation; the Company will
      make reasonable efforts to limit any wipe to Company data only.</li>
</ul>
<p>All clauses in this handbook are subject to revision at the Company's discretion in line
   with {law_updates} updates. Revised versions supersede all prior editions upon issuance.</p>"""


def _tech_security(ctx):
    person = ctx["person_noun"]
    email = ctx["contact_email"]
    return f"""
<p><strong>PART A — PURPOSE AND SCOPE</strong></p>
<p>This Policy establishes legally binding obligations governing the acceptable use, security,
   and management of Company technology resources: (a) to protect Company assets, data, and
   systems from unauthorized access or misuse; (b) to ensure operational efficiency and
   business continuity; and (c) to comply with applicable data-protection and cybercrime laws.
   It applies to all {person.lower()}s, contractors, interns, and third-party vendors, and to
   all Company-owned or managed devices, systems, networks, and data, including remote work
   environments and personally owned devices (BYOD).</p>
<p><strong>General Principles:</strong> All Company technology resources and the data created
   or stored using them remain the exclusive property of the Company. The {person} must comply
   with all applicable laws and software licensing. There is <strong>no expectation of
   privacy</strong> when using Company technology resources; the Company may monitor, inspect,
   and audit all usage at any time, to the extent permitted by law.</p>
<p><strong>PART B — ACCEPTABLE AND PROHIBITED USE</strong></p>
<p>Permitted: official Company business; limited incidental personal use that does not
   interfere with work; role-related professional development.</p>
<p>Strictly prohibited (may result in immediate disciplinary action, termination and referral
   to law-enforcement authorities): accessing/transmitting illegal or offensive content;
   installing unauthorized software; bypassing security controls; using resources for personal
   commercial ventures; sharing credentials/OTPs; forwarding Confidential Information to
   personal accounts; accessing systems over unsecured public Wi-Fi without an approved VPN;
   torrenting or large personal downloads on Company networks.</p>
<p><strong>PART C — DEVICE, SOFTWARE &amp; NETWORK MANAGEMENT</strong></p>
<p>Company-issued devices must use approved security configurations, strong password/PIN and
   full-disk encryption, and are subject to remote monitoring and wipe. Loss or theft must be
   reported within one (1) hour. Only IT-approved, properly licensed software may be installed;
   automatic security updates must remain enabled. A Company-approved VPN must be used for all
   remote access; Wi-Fi must use WPA2/WPA3 encryption.</p>
<p><strong>PART D — DATA SECURITY &amp; CONFIDENTIALITY</strong></p>
<p>Company email is for business use; auto-forwarding to external addresses is prohibited.
   Suspected phishing must be reported to {email}. Data is classified Public / Internal /
   Confidential / Restricted with corresponding handling requirements. All Confidential and
   Restricted data must be encrypted at rest and in transit; any suspected or confirmed data
   breach must be reported immediately to {email}. Only IT-approved cloud/SaaS platforms may be
   used and MFA must be enabled on all Company cloud accounts.</p>
<p><strong>PART E — MONITORING &amp; ENFORCEMENT</strong></p>
<p>The Company may monitor, log, review, and audit all usage at any time without prior notice,
   to the extent permitted by law. Audit logs are retained for a minimum of twelve (12) months
   and may be used as evidence in disciplinary or legal proceedings. Violations are enforced
   progressively from verbal warning through to termination and civil/criminal legal action.</p>
<p><strong>PART F — CONFIDENTIALITY OBLIGATIONS</strong></p>
<p>The {person}'s obligation to maintain confidentiality of technology-related Confidential
   Information remains in force indefinitely, both during and after the engagement, regardless
   of the reason for separation. This obligation is in addition to and consistent with the
   obligations set out in the Non-Disclosure and Non-Competition Agreement (NCNDA).</p>"""


def _blank(ctx):
    return "<p>[ Type or paste the content of this annexure here. ]</p>"


_BUILDERS = {
    "sales_incentive": _sales_incentive,
    "responsibilities": _responsibilities,
    "policy": _policy,
    "tech_security": _tech_security,
    "blank": _blank,
}
