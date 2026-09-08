"""Company Policy Handbook content selected by WORK LOCATION (country).

Each location has its own handbook (different working hours, pay dates, leave
framework and governing labour law). India is taken verbatim from the supplied
sample; the others follow the standard structure adapted to that jurisdiction.
Content is tokenised (__PERSON__ / __PAY__ / __PAYCAP__) so it reads correctly for
an Employee (offer letter) or a Service Provider (service agreement), and it stays
fully editable in the preview.
"""

# key -> display label for the form dropdown (order matters)
POLICY_LOCATIONS = [
    ("india", "India"),
    ("uae", "United Arab Emirates"),
    ("south_korea", "South Korea"),
    ("usa", "United States"),
    ("hong_kong", "Hong Kong"),
    ("singapore", "Singapore"),
    ("vietnam", "Vietnam"),
    ("thailand", "Thailand"),
    ("china", "China"),
    ("other", "Other / generic"),
]


def _india():
    return (
'<p class="annex-lawline"><strong>India — applicable Indian labour law</strong></p>'
'<p><strong>1. Attendance, Punctuality &amp; Tardiness</strong></p><ul>'
'<li>Desktop Readiness: All __PERSON__s must be logged in and ready by 9:00 AM (IST) sharp.</li>'
'<li>Tardiness Deduction Tiers: 3:01–3:15 PM — three late arrivals in one calendar month trigger a '
'1/4-day __PAY__ deduction on the 3rd occurrence; 3:16–3:30 PM — 1/4-day deduction per occurrence; '
'3:31–5:00 PM — 1/2-day deduction per occurrence; after 5:00 PM — full-day deduction; excessive '
'lateness (6+ arrivals in a month) — additional full-day deduction.</li>'
'<li>Leave Balance Adjustments: accrued Annual Leave may be applied for short- or half-day absences; '
'deductions apply where no AL balance is available.</li></ul>'
'<p><strong>2. Daily Breaks</strong></p><ul>'
'<li>Monday–Friday: 1 hour total per day (may be split into two breaks, not exceeding 1 hour in total).</li>'
'<li>Saturday (3:00 PM–7:00 PM): half working day; no scheduled break applies.</li></ul>'
'<p><strong>3. Leave Framework</strong></p><ul>'
'<li>Annual &amp; Other Leave: entitled to leave including annual, casual and sick leave up to 30 '
'calendar days; Annual Leave is paid after 1 year of service; 2 days per month for service between '
'6–12 months. Requests must be submitted at least 60 days in advance.</li>'
'<li>Public Holidays: as per applicable public holiday entitlements under Indian law.</li>'
'<li>Emergency Leave: requests during the probation period or before completion of one (1) year of '
'continuous service will not be approved except for emergencies vetted by executive management.</li></ul>'
'<p><strong>4. __PAYCAP__ Administration</strong></p><ul>'
'<li>Payment processed and transferred between the 15th and 20th of each calendar month.</li></ul>'
'<p><strong>5. Performance, Conduct &amp; Non-Compete</strong></p><ul>'
'<li>Performance Reviews: ongoing KPI tracking; persistent underperformance may result in a formal '
'Performance Improvement Plan (PIP).</li>'
'<li>Disciplinary Action: progressive action — formal warning → __PAY__ deduction → suspension → termination.</li>'
'<li>Work Ethics: maintain professional integrity, commercial transparency, and strict data '
'confidentiality in all client and company dealings.</li>'
'<li>Non-Compete: please refer to the NCNDA Agreement (governed by Indian law and limited in scope to '
'the job profile).</li></ul>'
'<p><strong>6. BYOD (Bring Your Own Device)</strong></p><ul>'
'<li>Personal devices used for Company business must meet minimum security standards (up-to-date OS, '
'encryption, active antivirus).</li>'
'<li>The Company may require MDM software on personal devices; the __PERSON__ consents to this as a '
'condition of BYOD authorization.</li>'
'<li>Company data on personal devices may be remotely wiped upon separation; the Company will make '
'reasonable efforts to limit any wipe to Company data only.</li></ul>'
"<p>All clauses in this policy are subject to revision at the Company's discretion in line with Indian "
'labour law updates. Revised versions supersede all prior editions upon issuance.</p>')


def _standard(law_title, updates, pay_window="between the 5th and 10th", leave=None, noncompete_law=None):
    leave = leave or ("Annual, sick, maternity/paternity and other statutory leave are granted in "
                      "accordance with " + updates + ". [Adjust the specific day entitlements for this "
                      "jurisdiction as required.]")
    nc = noncompete_law or updates
    return (
f'<p class="annex-lawline"><strong>{law_title}</strong></p>'
'<p><strong>1. Attendance, Punctuality &amp; Tardiness</strong></p><ul>'
'<li>Desktop Readiness: All __PERSON__s must be logged in and ready by 9:00 AM (local time) sharp.</li>'
'<li>Tardiness Deduction Tiers: 9:01–9:15 AM — three late arrivals in one calendar month trigger a '
'1/4-day __PAY__ deduction on the 3rd occurrence; 9:16–9:30 AM — 1/4-day per occurrence; 9:31–11:00 AM — '
'1/2-day per occurrence; after 11:00 AM — full-day; excessive lateness (6+ in a month) — additional full-day.</li>'
'<li>Leave Balance Adjustments: accrued Annual Leave may be applied for short- or half-day absences; '
'deductions apply where no AL balance is available.</li></ul>'
'<p><strong>2. Daily Breaks</strong></p><ul>'
'<li>Monday–Friday: 1 hour total per day (may be split into two breaks, not exceeding 1 hour in total).</li></ul>'
'<p><strong>3. Leave Framework</strong></p><ul>'
f'<li>{leave}</li>'
'<li>Emergency Leave: requests during probation or before completion of one (1) year of continuous '
'service will not be approved except for emergencies vetted by executive management.</li></ul>'
'<p><strong>4. __PAYCAP__ Administration</strong></p><ul>'
f'<li>Payment processed and transferred {pay_window} of each calendar month.</li>'
"<li>Pay slips available on written request to HR with 5 business days' prior notice.</li></ul>"
'<p><strong>5. Performance, Conduct &amp; Non-Compete</strong></p><ul>'
'<li>Performance Reviews: ongoing KPI tracking; persistent underperformance may result in a formal PIP.</li>'
'<li>Disciplinary Action: progressive action — formal warning → __PAY__ deduction → suspension → termination.</li>'
'<li>Work Ethics: maintain professional integrity, commercial transparency, and strict data confidentiality.</li>'
f'<li>Non-Compete: please refer to the NCNDA Agreement (governed by {nc}).</li></ul>'
'<p><strong>6. BYOD (Bring Your Own Device)</strong></p><ul>'
'<li>Personal devices used for Company business must meet minimum security standards (up-to-date OS, '
'encryption, active antivirus).</li>'
'<li>The Company may require MDM software on personal devices; the __PERSON__ consents to this as a '
'condition of BYOD authorization.</li>'
'<li>Company data on personal devices may be remotely wiped upon separation; the Company will make '
'reasonable efforts to limit any wipe to Company data only.</li></ul>'
f'<p>All clauses in this handbook are subject to revision at the Company\'s discretion in line with '
f'{updates} updates. Revised versions supersede all prior editions upon issuance.</p>')


HANDBOOKS = {
    "india": _india(),
    "uae": _standard("United Arab Emirates — Federal Decree-Law No. 33 of 2021",
                     "UAE Labour Law", noncompete_law="the laws of the United Arab Emirates",
                     leave=("Annual Leave: 30 calendar days paid after 1 year of service; 2 days per month "
                            "for service between 6–12 months. Sick Leave: 15 days full pay, 30 days half pay, "
                            "45 days unpaid (post-probation). Maternity 60 days; Paternity 5 days. Requests at "
                            "least 60 days in advance.")),
    "south_korea": _standard("South Korea — Labor Standards Act of the Republic of Korea",
                             "the Labor Standards Act of the Republic of Korea",
                             noncompete_law="the laws of the Republic of Korea",
                             leave="Leave is granted in accordance with the Labor Standards Act of the Republic of Korea."),
    "usa": _standard("United States — Fair Labor Standards Act (FLSA) &amp; applicable State law",
                     "the Fair Labor Standards Act (FLSA) and applicable State law",
                     noncompete_law="the applicable State law (note: non-compete enforceability varies by state)"),
    "hong_kong": _standard("Hong Kong — Employment Ordinance (Cap. 57)",
                           "the Employment Ordinance (Cap. 57)",
                           noncompete_law="the laws of the Hong Kong Special Administrative Region"),
    "singapore": _standard("Singapore — Employment Act",
                           "the Employment Act of Singapore",
                           noncompete_law="the laws of the Republic of Singapore"),
    "vietnam": _standard("Vietnam — Labour Code (2019)",
                         "the Vietnam Labour Code",
                         noncompete_law="the laws of the Socialist Republic of Vietnam"),
    "thailand": _standard("Thailand — Labour Protection Act",
                          "the Thailand Labour Protection Act",
                          noncompete_law="the laws of the Kingdom of Thailand"),
    "china": _standard("China — Labour Contract Law of the PRC",
                       "the Labour Contract Law of the PRC",
                       noncompete_law="the laws of the People's Republic of China"),
    "other": _standard("Company Policy Handbook — applicable local labour law",
                       "applicable local labour law",
                       noncompete_law="applicable local law"),
}


def get_policy_html(location, ctx):
    tpl = HANDBOOKS.get(location)
    if not tpl:
        return None
    return (tpl.replace("__PERSON__", ctx.get("person_noun", "Employee"))
               .replace("__PAYCAP__", ctx.get("pay_noun_cap", "Salary"))
               .replace("__PAY__", ctx.get("pay_noun", "salary")))
