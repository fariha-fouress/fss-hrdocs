"""
Low-level HTML block helpers shared by every document builder.

Two kinds of region exist in a generated document:

  editable(...)          -> contenteditable, user may reword freely.
  locked(...)            -> contenteditable=false. Compliance-sensitive; the user
                            cannot alter or delete it in the editor.

Both may carry a `comp` tag. Any region with a comp tag is *required*: the
finalise step refuses to render a PDF/DOCX if that tag has disappeared from the
submitted HTML (see compliance.py). Locked regions therefore can never be
dropped, and required-editable regions (e.g. the NCNDA restricted territory,
which the user may reword) can be reworded but not deleted.
"""
from markupsafe import escape


def _attrs(comp, editable):
    cls = "doc-region " + ("editable" if editable else "locked")
    ce = "true" if editable else "false"
    comp_attr = f' data-comp="{escape(comp)}"' if comp else ""
    lock_attr = "" if editable else ' data-locked="1"'
    return f'class="{cls}" contenteditable="{ce}"{comp_attr}{lock_attr}'


def editable(inner_html, comp=None):
    return f'<div {_attrs(comp, True)}>{inner_html}</div>'


def locked(inner_html, comp=None):
    return f'<div {_attrs(comp, False)}>{inner_html}</div>'


def esc(text):
    return str(escape(text))


# ---- content fragments (returned as inner html) --------------------------
def h(text, level=2):
    return f'<h{level}>{esc(text)}</h{level}>'


def p(text_or_html, raw=False):
    return f'<p>{text_or_html if raw else esc(text_or_html)}</p>'


def numbered_term(n, title, body_html):
    """A '1. Designation: ...' style offer-letter term."""
    return (f'<p class="term"><span class="term-n">{n}.</span> '
            f'<strong>{esc(title)}:</strong> {body_html}</p>')


def compensation_table(currency, rows, pay_label="Compensation"):
    """rows = list of (component, amount_text)."""
    trs = "".join(
        f"<tr><td>{esc(c)}</td><td>{esc(a)}</td></tr>" for c, a in rows
    )
    return (
        f'<p class="term-title"><strong>{esc(pay_label)}:</strong></p>'
        f'<table class="comp-table"><thead><tr>'
        f'<th>Component</th><th>Amount in {esc(currency)} Per Month</th>'
        f'</tr></thead><tbody>{trs}</tbody></table>'
    )


def signature_block(company_legal_name, signatory, party_label="Employee",
                    candidate="", passport="", designation=""):
    """Two-column execution block."""
    right_id = "Passport No.:" if party_label in ("Employee", "Service Provider") else "ID:"
    return f'''
<table class="sig-table"><tr>
  <td class="sig-cell">
    <p class="sig-head">For and on behalf of<br><strong>{esc(company_legal_name)}</strong></p>
    <p class="sig-line">Authorised Signatory: __________________________</p>
    <p>Name: {esc(signatory["name"])}</p>
    <p>Designation: {esc(signatory["designation"])}</p>
    <p>Date: __________________________</p>
    <p>Company Stamp:</p>
  </td>
  <td class="sig-cell">
    <p class="sig-head"><strong>{esc(party_label)} — Acceptance</strong></p>
    <p class="sig-line">Signature: __________________________</p>
    <p>Name: {esc(candidate)}</p>
    <p>{right_id} {esc(passport)}</p>
    <p>Designation: {esc(designation)}</p>
    <p>Date: __________________________</p>
  </td>
</tr></table>'''


def acknowledgement_block(candidate, annex_no_roman, title, party_label="Employee"):
    """The auto-appended acknowledgement at the BOTTOM of every annexure."""
    name = esc(candidate) or "________________"
    return locked(
        f'<div class="annex-ack">'
        f'<p>I, <strong>{name}</strong>, acknowledge that I have read and understood '
        f'<strong>Annexure {esc(annex_no_roman)} — {esc(title)}</strong>, and I '
        f'accept and agree to comply with all terms set out therein.</p>'
        f'<p class="sig-line">{esc(party_label)} Signature: __________________________ '
        f'&nbsp;&nbsp; Date: __________________</p>'
        f'</div>',
        comp=f"ANNEX_ACK_{annex_no_roman}",
    )


ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
