"""Transactional email — the management notification sent on every PDF download.

Uses plain SMTP (defaults tuned for Zoho Mail: smtp.zoho.com:465 SSL). Works
with any SMTP provider by changing the env vars. Never raises to the caller;
returns (ok, detail) so the route can log EMAIL_SENT / EMAIL_FAILED to the audit
trail regardless of outcome.
"""
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

from flask import current_app


def send_download_notification(*, doc_type, candidate, entity_label, downloaded_by,
                               timestamp=None, filename=""):
    cfg = current_app.config
    recipients = cfg["MANAGEMENT_EMAILS"]
    ts = timestamp or datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    pretty_type = {"offer_letter": "Offer Letter",
                   "service_agreement": "Service Agreement",
                   "ncnda": "NCNDA"}.get(doc_type, doc_type)

    subject = f"[HR Doc Downloaded] {pretty_type} — {candidate} ({entity_label})"
    body = (
        "An HR document PDF was downloaded from the HR Document Generator.\n\n"
        f"  Document type : {pretty_type}\n"
        f"  Candidate     : {candidate}\n"
        f"  Entity        : {entity_label}\n"
        f"  Downloaded by : {downloaded_by}\n"
        f"  Timestamp     : {ts}\n"
        f"  File          : {filename}\n\n"
        "This is an automated notification. A full record is kept in the audit log."
    )

    if not cfg["EMAIL_ENABLED"]:
        return (False, "EMAIL_ENABLED is false — notification not sent (logged only).")
    if not recipients:
        return (False, "No MANAGEMENT_EMAILS configured.")

    msg = EmailMessage()
    msg["From"] = f'{cfg["MAIL_FROM_NAME"]} <{cfg["MAIL_FROM"]}>'
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        if cfg["SMTP_USE_SSL"]:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg["SMTP_HOST"], cfg["SMTP_PORT"], context=ctx, timeout=20) as s:
                if cfg["SMTP_USERNAME"]:
                    s.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=20) as s:
                s.starttls(context=ssl.create_default_context())
                if cfg["SMTP_USERNAME"]:
                    s.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
                s.send_message(msg)
        return (True, f"Notification sent to {', '.join(recipients)}")
    except Exception as exc:  # noqa
        return (False, f"SMTP error: {exc}")
