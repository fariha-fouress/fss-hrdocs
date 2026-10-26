"""Central configuration, loaded from environment (.env)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # dotenv optional
    pass

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


def _emails(raw):
    return [e.strip().lower() for e in (raw or "").replace(";", ",").split(",") if e.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Session cookie -------------------------------------------------
    # The app runs inside a Zoho Recruit Web Tab (a cross-origin iframe).
    # Without SameSite=None (+ Secure) Chrome treats the cookie as Lax and
    # drops it in the iframe, so sign-in loops back to /login. Partitioned
    # (CHIPS) keeps it working under Chrome's third-party cookie rules.
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_PARTITIONED = True   # CHIPS, for Chrome third-party cookie rules
    SESSION_COOKIE_HTTPONLY = True

    # --- Storage --------------------------------------------------------
    # DATA_DIR holds the SQLite database and uploaded files (letterheads).
    # On Railway, attach a persistent Volume and set DATA_DIR=/data so that
    # added locations and their uploads survive redeploys.
    DATA_DIR = os.environ.get("DATA_DIR", str(PROJECT_DIR / "data"))
    DB_PATH = os.environ.get("DB_PATH", str(Path(DATA_DIR) / "hrdocs.db"))
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", str(Path(DATA_DIR) / "uploads"))

    # --- Authorisation --------------------------------------------------
    # The 4 authorised users. Only these emails may sign in.
    AUTHORIZED_EMAILS = _emails(os.environ.get(
        "AUTHORIZED_EMAILS",
        # sensible default seeded for first run — REPLACE in .env
        "fariha.sheikh@fouressynergy.com",
    ))

    # AUTH_MODE: "zoho" (Zoho OAuth/OIDC) or "password" (local, for dev/testing)
    AUTH_MODE = os.environ.get("AUTH_MODE", "password").lower()

    # Local password mode: a single shared password (bcrypt/pbkdf2 hashed at rest
    # via werkzeug). For real deployments prefer AUTH_MODE=zoho.
    LOCAL_PASSWORD = os.environ.get("LOCAL_PASSWORD", "changeme123")

    # Zoho OAuth (OIDC). Register an app at https://api-console.zoho.com/
    ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
    ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
    ZOHO_REDIRECT_URI = os.environ.get("ZOHO_REDIRECT_URI", "http://localhost:5000/auth/callback")
    # Zoho accounts server. .com / .eu / .in / .com.au / .jp depending on your DC.
    ZOHO_ACCOUNTS_BASE = os.environ.get("ZOHO_ACCOUNTS_BASE", "https://accounts.zoho.com")

    # --- Email (transactional notification on every PDF download) -------
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zoho.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
    SMTP_USE_SSL = os.environ.get("SMTP_USE_SSL", "true").lower() == "true"
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    # For Zoho with 2FA, use an app-specific password.
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", os.environ.get("SMTP_USERNAME", "no-reply@fouressynergy.com"))
    MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "HR Document Generator")

    # Management recipients that get notified on every PDF download.
    MANAGEMENT_EMAILS = _emails(os.environ.get(
        "MANAGEMENT_EMAILS",
        "admin@fouressynergy.com",
    ))

    # If false, the app still logs the audit event but does not attempt SMTP
    # (useful for local testing without credentials).
    EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"

    # Page size for PDF output: "A4" or "Letter"
    PAGE_SIZE = os.environ.get("PAGE_SIZE", "A4")
