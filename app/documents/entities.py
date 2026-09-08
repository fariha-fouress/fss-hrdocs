"""
Entity registry — the single source of truth for the "auto-derived logic".

From the chosen entity we derive, WITHOUT asking the user:
  * legal name shown throughout the document + signature block
  * letterhead brand (masthead image + footer address block)
  * default currency
  * the labour-law citation that appears in the Company Policy annexure
  * the governing-law / courts clause used in the NCNDA
  * a default NCNDA "Restricted Territory"

ESTEL is a fully independent brand. Its `is_fouress` flag is False and NONE of
its text ever references Fouress Synergy. A guard in compliance.py enforces this.
"""

# ---------------------------------------------------------------------------
# Signatories (the "Signatory selector: Swarit or Pooja")
# ---------------------------------------------------------------------------
SIGNATORIES = {
    "swarit": {"name": "Swarit Srivastava", "designation": "Director"},
    "pooja": {"name": "Pooja Talukdar", "designation": "Director"},
    "pinky": {"name": "Pinky Shah", "designation": "Human Resources Manager"},
}

# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------
ENTITIES = {
    "fss_uae": {
        "key": "fss_uae",
        "country": "uae",
        "label": "FSS UAE",
        "legal_name": "Fouress Synergy FZC",
        "brand": "fouress",
        "tagline": "A General Trading Company",
        "is_fouress": True,
        "address_lines": [
            "Head Office Z3-01, 02 & 13, SAIF Suite, SAIF Zone, Sharjah, UAE.",
        ],
        "contact_line": "Email: fouresssynergy@gmail.com  |  admin@fouressynergy.com  |  Landline: +971-6-5267868",
        "currency": "AED",
        "policy_law_title": "United Arab Emirates — Federal Decree-Law No. 33 of 2021",
        "policy_law_short": "the UAE Federal Labour Law (Federal Decree-Law No. 33 of 2021) and the regulations of the Sharjah Airport International Free Zone (SAIF Zone) Authority",
        "policy_law_updates": "UAE Labour Law",
        "ncnda_governing_law": "the laws of the United Arab Emirates",
        "ncnda_courts": "the courts of Sharjah, United Arab Emirates",
        "restricted_territory_html": (
            "<p><strong>Middle East:</strong> United Arab Emirates, Kingdom of Saudi Arabia, "
            "Kuwait, Qatar, Bahrain, Oman, Iraq, Jordan, and Lebanon.</p>"
            "<p><strong>Africa:</strong> All countries in North Africa (Egypt, Libya, Tunisia, "
            "Algeria, Morocco), East Africa (Kenya, Tanzania, Ethiopia, Uganda), West Africa "
            "(Nigeria, Ghana, Ivory Coast, Senegal), and Southern Africa (South Africa, "
            "Mozambique, Zambia, Zimbabwe).</p>"
        ),
    },
    "fss_korea": {
        "key": "fss_korea",
        "country": "south_korea",
        "label": "FSS Korea",
        "legal_name": "Fouress Synergy LLC, Korea Branch",
        "brand": "fouress",
        "tagline": "A General Trading Company",
        "is_fouress": True,
        "address_lines": [
            "Room 1437, FLYQ Eunpyeong, 63-1 Jingwan-dong, Eunpyeong-gu, Seoul 03470, Republic of Korea",
        ],
        "contact_line": "koreabranch@fouressynergy.com  |  www.fouressynergy.com  |  Tel: 82-02-356-8633  |  Fax: 82-02-356-8733",
        "currency": "USD",
        "policy_law_title": "South Korea — Labor Standards Act of the Republic of Korea",
        "policy_law_short": "the Labor Standards Act of the Republic of Korea",
        "policy_law_updates": "the Labor Standards Act of the Republic of Korea",
        "ncnda_governing_law": "the laws of the Republic of Korea",
        "ncnda_courts": "the competent courts of Seoul, Republic of Korea",
        "restricted_territory_html": (
            "<p><strong>East Asia:</strong> Republic of Korea, Japan, People's Republic of China, "
            "Taiwan, Hong Kong SAR, and Singapore.</p>"
            "<p>Together with any additional market in which the Company has demonstrable business "
            "operations, active client accounts, or active supplier relationships at the date of the "
            "Employee's separation.</p>"
        ),
    },
    "fss_usa": {
        "key": "fss_usa",
        "country": "usa",
        "label": "FSS USA",
        "legal_name": "Fouress Synergy LLC",
        "brand": "fouress",
        "tagline": "A General Trading Company",
        "is_fouress": True,
        "address_lines": [
            "Corporate Office: 5000 Centregreen Way, Suite 500, Cary, North Carolina 27513, Wake County, USA",
            "Registered Office: 16192 Coastal Highway, Lewes, Delaware 19958, County of Sussex, USA",
        ],
        "contact_line": "EIN: 61-2102826  |  E-Verify: 2913495  |  admin@fouressynergy.com  |  +1 (984) 296-4442",
        "currency": "USD",
        "policy_law_title": "United States — Fair Labor Standards Act (FLSA) & applicable State law",
        "policy_law_short": "the U.S. Fair Labor Standards Act (FLSA) and the applicable labor law of the State of [STATE]",
        "policy_law_updates": "the Fair Labor Standards Act (FLSA) and applicable State law",
        "ncnda_governing_law": "the laws of the State of [STATE], United States of America",
        "ncnda_courts": "the state and federal courts located in [COUNTY/STATE], United States of America",
        "restricted_territory_html": (
            "<p><strong>North America:</strong> the United States of America, Canada, and Mexico.</p>"
            "<p>Together with any additional market in which the Company has demonstrable business "
            "operations, active client accounts, or active supplier relationships at the date of the "
            "Employee's separation. (Note: non-compete enforceability varies by U.S. state — confirm "
            "with counsel for the relevant state.)</p>"
        ),
    },
    "fss_hk": {
        "key": "fss_hk",
        "country": "hong_kong",
        "label": "FSS HK",
        "legal_name": "Fouress Synergy Trading (HK) Ltd",
        "brand": "fouress",
        "tagline": "A General Trading Company",
        "is_fouress": True,
        "address_lines": [
            "Unit 1411, 14/F, Cosco Tower, 183 Queen's Road Central, Sheung Wan, Hong Kong",
        ],
        "contact_line": "Email: fouresssynergy@gmail.com  |  Tel: +1 9375516649",
        "currency": "HKD",
        "policy_law_title": "Hong Kong — Employment Ordinance (Cap. 57)",
        "policy_law_short": "the Employment Ordinance (Cap. 57) of the Laws of Hong Kong",
        "policy_law_updates": "the Employment Ordinance (Cap. 57)",
        "ncnda_governing_law": "the laws of the Hong Kong Special Administrative Region",
        "ncnda_courts": "the courts of the Hong Kong Special Administrative Region",
        "restricted_territory_html": (
            "<p><strong>Greater China & East Asia:</strong> Hong Kong SAR, People's Republic of China, "
            "Taiwan, Republic of Korea, Japan, and Singapore.</p>"
            "<p>Together with any additional market in which the Company has demonstrable business "
            "operations, active client accounts, or active supplier relationships at the date of the "
            "Employee's separation.</p>"
        ),
    },
    "estel": {
        "key": "estel",
        "country": "singapore",
        "label": "Estel SG",
        "legal_name": "Estel Energy (SG) Pte. Ltd.",
        "brand": "estel",
        "tagline": "",
        "is_fouress": False,
        "address_lines": [
            "138 Robinson Road, #24-01 Oxley Tower, Singapore 068906",
        ],
        "contact_line": "admin@estel-energy.com  |  Tel (USA): +1 (984) 296-4442",
        "currency": "USD",
        "policy_law_title": "Governing Law — Singapore",
        "policy_law_short": "the laws of Singapore and the applicable laws of the market jurisdiction",
        "policy_law_updates": "applicable law",
        "ncnda_governing_law": "the laws of the Republic of Singapore",
        "ncnda_courts": "the courts of the Republic of Singapore",
        "restricted_territory_html": (
            "<p><strong>Southeast Asia:</strong> the Socialist Republic of Vietnam, Singapore, Malaysia, "
            "Thailand, Indonesia, and the Philippines.</p>"
            "<p>Together with any additional market in which the Company has demonstrable business "
            "operations, active client accounts, or active supplier relationships at the date of the "
            "Service Provider's separation.</p>"
        ),
    },
    "estel_usa": {
        "key": "estel_usa",
        "country": "usa",
        "label": "ESTEL USA",
        "legal_name": "Estel Energy LLC",
        "brand": "estel",
        "tagline": "",
        "is_fouress": False,
        "address_lines": [
            "16192 Coastal Highway, Lewes, Delaware 19958, County of Sussex, USA",
        ],
        "contact_line": "EIN: 42-4157144  |  admin@estel-energy.com  |  Tel (USA): +1 (984) 338-6942",
        "currency": "USD",
        "policy_law_title": "United States — Fair Labor Standards Act (FLSA) & applicable State law",
        "policy_law_short": "the U.S. Fair Labor Standards Act (FLSA) and the applicable labor law of the State of Delaware",
        "policy_law_updates": "the Fair Labor Standards Act (FLSA) and applicable State law",
        "ncnda_governing_law": "the laws of the State of Delaware, United States of America",
        "ncnda_courts": "the state and federal courts located in the State of Delaware, United States of America",
        "restricted_territory_html": (
            "<p><strong>North America:</strong> the United States of America, Canada, and Mexico.</p>"
            "<p>Together with any additional market in which the Company has demonstrable business "
            "operations, active client accounts, or active supplier relationships at the date of the "
            "Service Provider's separation. (Note: non-compete enforceability varies by U.S. state.)</p>"
        ),
    },
}

ENTITY_ORDER = ["fss_usa", "fss_hk", "fss_uae", "fss_korea", "estel", "estel_usa"]


def get_entity(key):
    if key not in ENTITIES:
        raise KeyError(f"Unknown entity '{key}'")
    return ENTITIES[key]


def get_signatory(key):
    if key not in SIGNATORIES:
        raise KeyError(f"Unknown signatory '{key}'")
    return SIGNATORIES[key]


def entity_choices():
    return [(k, ENTITIES[k]["label"]) for k in ENTITY_ORDER]
