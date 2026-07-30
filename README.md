# FSS HR Document Generator

A private internal web tool for generating **Offer Letters**, **Service
Agreements**, and **NCNDAs** for five entities — FSS USA, FSS HK, FSS UAE, FSS
Korea, and the independent ESTEL Energy — on the correct company letterhead, with
an editable preview, PDF/Word download, automatic management notification, and a
full audit trail.

Stack: **Flask + SQLite + WeasyPrint** (single Python service, easy to deploy).

---

## What it does

1. **Login** — only the configured authorised users (the 4 emails) can sign in.
   Zoho OAuth ("Sign in with Zoho") is the recommended mode; a local shared
   password is available for quick/dev use.
2. **Fill a form** — document type, entity, candidate, role, salary/fee,
   dates, probation, reporting manager, work location, a **Remote / Onsite**
   toggle, territory, passport (NCNDA), and the **signatory** (Swarit or Pooja).
3. **Editable preview** — the document is generated on the entity letterhead and
   shown as a rich-text editor. You can reword anything **except locked
   compliance clauses** (marked 🔒). The acknowledgement block at the bottom of
   each annexure is added automatically.
4. **Download** — **PDF** (server-side WeasyPrint, letterhead + running header/
   footer + page breaks + page numbers) or **Word (.docx)**. Files are named
   `{DocType}_{CandidateName}_{Entity}_{Date}.{ext}`.
5. **Every PDF download** sends an automatic email to the management list
   (document type, candidate, entity, who downloaded, timestamp).
6. **Audit log** — every generation, download and email is recorded.

## Auto-derived logic (never asked of the user)

Chosen from the **entity** (see `app/documents/entities.py`):

| Entity | Legal name | Policy / labour-law citation | NCNDA governing law |
|---|---|---|---|
| FSS USA | Fouress Synergy LLC | FLSA + applicable State law | State of [ ], USA |
| FSS HK | Fouress Synergy Trading (HK) Ltd | Employment Ordinance (Cap. 57) | Hong Kong SAR |
| FSS UAE | Fouress Synergy FZC | Federal Decree-Law No. 33 of 2021 | Sharjah, UAE |
| FSS Korea | Fouress Synergy LLC, Korea Branch | Labor Standards Act | Seoul, Korea |
| ESTEL Energy | Estel Energy (SG) Pte. Ltd. | Singapore | Singapore |

- **Letterhead** switches per entity (logo, name, address, footer, accent colour).
- **Legal references** are swapped, not just the logo.
- **NCNDA Restricted Territory** defaults per entity/market (editable in preview).
- **ESTEL is fully independent** — its documents never reference Fouress Synergy.
  A guard refuses to render an ESTEL PDF/DOCX that contains the word "Fouress".

## Compliance clauses that can never be dropped

Enforced both in the editor (locked, non-editable) and re-checked server-side
before any file is produced (`app/documents/compliance.py`):

- **Offer Letter:** probation clause; **FSS USA additionally** FLSA overtime +
  EAD / work-authorisation language.
- **Service Agreement:** "service fee — not salary/wages" clause, independent-
  contractor / no-employment clause, contractor-handles-own-tax clause.
- **NCNDA:** confidentiality, non-compete + restricted activities, restricted
  territory, governing law, remedies, acknowledgement, signature block.
- **Every annexure:** its acknowledgement block.

If any required clause is missing from the submitted HTML, the download is
rejected (HTTP 422) with a clear message.

---

## Run locally

```bash
cd hr-docgen
python -m venv .venv && source .venv/bin/activate      # optional
pip install -r requirements.txt
cp .env.example .env                                   # then edit .env
python run.py                                          # http://localhost:5000
```

WeasyPrint needs system libraries (Pango/Cairo). On Debian/Ubuntu:

```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2
```

(The included `Dockerfile` already installs these — `docker build -t hrdocs .`
then `docker run -p 5000:5000 --env-file .env hrdocs`.)

## Configure

Edit `.env` (see `.env.example`):

- `AUTHORIZED_EMAILS` — the 4 users who may sign in.
- `AUTH_MODE=zoho` + `ZOHO_CLIENT_ID/SECRET/REDIRECT_URI/ACCOUNTS_BASE`
  (register a *Server-based* app at <https://api-console.zoho.com>), **or**
  `AUTH_MODE=password` + `LOCAL_PASSWORD` for a quick start.
- `EMAIL_ENABLED=true` + Zoho SMTP creds (`SMTP_*`, use a Zoho **app-specific
  password**) + `MANAGEMENT_EMAILS` to enable download notifications. While
  `EMAIL_ENABLED=false`, downloads still work and the intent is logged.

## Test

```bash
python -m tests.smoke_test      # builds + renders each doc type, checks guards
```

Sample rendered output is in `tests/out/`.

---

## Editing the templates

All wording lives in plain Python and is easy to change without touching the app:

- `app/documents/entities.py` — legal names, addresses, contact lines, currency,
  labour-law citations, NCNDA jurisdictions, default restricted territories.
- `app/documents/builder.py` — the body of each document type + which clauses
  are locked.
- `app/documents/annexures.py` — the pre-filled (editable) annexure content.
- `app/static/css/document.css` — the letterhead look, margins, page geometry
  (shared by the preview and the PDF).
- `app/static/logos/` — `fouress.jpeg`, `estel.png`.

## Notes / things to confirm

- **No US offer-letter sample** was supplied — the US offer letter is built from
  the UAE/Korea structure with FLSA overtime + EAD language added. Please review
  the US wording with counsel.
- **No US registered-office address** was supplied — a placeholder
  `[US registered office address — TO BE CONFIRMED]` appears in the FSS USA
  letterhead; set it in `entities.py`.
- **No HK offer-letter sample** was supplied — HK offer letters follow the same
  structure with the Employment Ordinance citation.
- U.S. non-compete enforceability varies by state; the NCNDA carries a note to
  confirm with counsel for the relevant state.
- The Korea letterhead address in the offer-letter sample and in the letterhead
  file differed slightly; the offer-letter version (Seoul 03470) is used.
