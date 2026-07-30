"""End-to-end engine smoke test (no HTTP server needed).

Run from the project root:  python -m tests.smoke_test
Renders one PDF + DOCX per document type into tests/out/ and asserts the
compliance + ESTEL-isolation guards behave correctly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.documents.builder import build
from app.documents.compliance import validate, sanitize
from app.render.pdf import render_pdf
from app.render.docx_render import render_docx

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

CASES = [
    {  # employee offer letter, USA -> must carry FLSA + EAD
        "doc_type": "offer_letter", "entity": "fss_usa", "employment": "employee",
        "candidate": "Jane Doe", "role": "Senior Sales Executive",
        "pay_amount": "6500 (Six Thousand Five Hundred)", "pay_currency": "USD",
        "start_date": "2026-08-01", "probation": "ninety (90) days",
        "reporting_manager": "VP Sales", "work_location": "New York, NY",
        "work_mode": "remote", "territory": "North America", "passport": "X1234567",
        "signatory": "swarit", "letter_date": "2026-07-13",
        "annexures": [{"kind": "sales_incentive", "title": "Sales Incentive Structure"},
                      {"kind": "policy", "title": "Company Policy Handbook"},
                      {"kind": "tech_security", "title": "Technology & Data Security Policy"}],
    },
    {  # contractor service agreement, ESTEL -> no salary word, IC clause, no 'Fouress'
        "doc_type": "service_agreement", "entity": "estel", "employment": "contractor",
        "candidate": "Doan Dac Huy", "role": "Sales Representative",
        "pay_amount": "2000 (Two Thousand)", "pay_currency": "USD",
        "start_date": "2026-06-23", "probation": "sixty (60) days",
        "work_location": "Ho Chi Minh City", "work_mode": "onsite",
        "territory": "Vietnam Domestic Market", "passport": "C3989321",
        "signatory": "pooja", "agreement_date": "2026-06-20",
        "annexures": [{"kind": "sales_incentive", "title": "Sales Incentive Structure"},
                      {"kind": "responsibilities", "title": "Scope of Work"},
                      {"kind": "policy", "title": "Service Engagement Policy"}],
    },
    {  # NCNDA, UAE, employee framing
        "doc_type": "ncnda", "entity": "fss_uae", "employment": "employee",
        "candidate": "Mohammed Irfan", "role": "Senior Sales Executive",
        "start_date": "2026-06-01", "passport": "S9704562",
        "signatory": "swarit", "agreement_date": "2026-05-21", "annexures": [],
    },
]


def main():
    for c in CASES:
        built = build(c)
        body = built["body_html"]
        ok, errors = validate(c["entity"], built["required_tags"], body)
        assert ok, f"{c['doc_type']}/{c['entity']} failed validation: {errors}"

        # USA offer letter must contain FLSA + EAD tags
        if c["entity"] == "fss_usa" and c["doc_type"] == "offer_letter":
            assert "FLSA_OVERTIME" in built["required_tags"]
            assert "EAD" in built["required_tags"]

        # service agreement must never say "salary" for the fee, must have IC clause
        if c["doc_type"] == "service_agreement":
            assert "IC_RELATIONSHIP" in built["required_tags"]
            assert "SERVICE_FEE_NOT_SALARY" in built["required_tags"]
            assert "CONTRACTOR_TAX" in built["required_tags"]

        # ESTEL isolation
        if c["entity"] == "estel":
            assert "fouress" not in body.lower(), "ESTEL doc leaked 'Fouress'!"

        pdf = render_pdf(c["entity"], sanitize(body))
        docx = render_docx(c["entity"], sanitize(body))
        stub = built["filename_stub"]
        open(os.path.join(OUT, stub + ".pdf"), "wb").write(pdf)
        open(os.path.join(OUT, stub + ".docx"), "wb").write(docx)
        print(f"OK  {c['doc_type']:18} {c['entity']:9} -> {stub}.pdf ({len(pdf)} b), "
              f".docx ({len(docx)} b), tags={len(built['required_tags'])}")

    # NEGATIVE 1: dropping a locked clause must fail validation
    built = build(CASES[0])
    tampered = built["body_html"].replace('data-comp="PROBATION"', 'data-comp="X"')
    ok, errors = validate("fss_usa", built["required_tags"], tampered)
    assert not ok and any("PROBATION" in e for e in errors), "tamper check failed"
    print("OK  negative: dropping PROBATION clause is rejected")

    # NEGATIVE 2: 'Fouress' inside an ESTEL doc must fail
    built = build(CASES[1])
    leaked = built["body_html"] + "<p>Fouress Synergy</p>"
    ok, errors = validate("estel", built["required_tags"], leaked)
    assert not ok and any("ESTEL" in e for e in errors), "ESTEL isolation check failed"
    print("OK  negative: 'Fouress' inside ESTEL doc is rejected")

    print("\nAll smoke tests passed. Output in", OUT)


if __name__ == "__main__":
    main()
