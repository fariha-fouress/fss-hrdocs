"""Authentication: Zoho OAuth or local shared-password, gated by an allowlist.

The allowlist is the AUTHORIZED_EMAILS env seed PLUS any emails added at runtime
via the login page (stored in the DB). Adding a new authorised user requires the
shared password, so only insiders can do it.
"""
import hmac
import secrets
import urllib.parse
from functools import wraps

import requests
from flask import (Blueprint, current_app, redirect, render_template, request,
                   session, url_for, flash)

from .db import log_audit, add_authorized_email, list_authorized_emails

bp = Blueprint("auth", __name__)


def current_user():
    return session.get("user_email")


def is_authorized(email):
    if not email:
        return False
    email = email.strip().lower()
    if email in current_app.config["AUTHORIZED_EMAILS"]:
        return True
    try:
        return email in list_authorized_emails()
    except Exception:
        return False


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def _complete_login(email):
    email = email.strip().lower()
    session["user_email"] = email
    session.permanent = True
    log_audit(email, "LOGIN")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("main.dashboard"))

    mode = current_app.config["AUTH_MODE"]

    if mode == "zoho":
        if not current_app.config["ZOHO_CLIENT_ID"]:
            flash("AUTH_MODE=zoho but ZOHO_CLIENT_ID is not configured.", "error")
            return render_template("login.html", mode="misconfigured")
        state = secrets.token_urlsafe(24)
        session["oauth_state"] = state
        params = {
            "response_type": "code",
            "client_id": current_app.config["ZOHO_CLIENT_ID"],
            "scope": "AaaServer.profile.READ email profile openid",
            "redirect_uri": current_app.config["ZOHO_REDIRECT_URI"],
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        auth_url = (current_app.config["ZOHO_ACCOUNTS_BASE"]
                    + "/oauth/v2/auth?" + urllib.parse.urlencode(params))
        return redirect(auth_url)

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not is_authorized(email):
            flash("This email is not authorised to use this tool.", "error")
        elif not hmac.compare_digest(password, current_app.config["LOCAL_PASSWORD"]):
            flash("Incorrect password.", "error")
        else:
            _complete_login(email)
            # only follow local paths, never another host (open redirect)
            nxt = request.args.get("next") or ""
            if not nxt.startswith("/") or nxt.startswith("//"):
                nxt = url_for("main.dashboard")
            return redirect(nxt)
    return render_template("login.html", mode="password")


@bp.route("/authorize", methods=["POST"])
def authorize():
    """Add a new authorised email. Gated by the shared password."""
    email = (request.form.get("new_email") or "").strip().lower()
    password = request.form.get("auth_password") or ""
    if "@" not in email or "." not in email:
        flash("Enter a valid email address.", "error")
    elif not hmac.compare_digest(password, current_app.config["LOCAL_PASSWORD"]):
        flash("Incorrect shared password — only someone with it can authorise a new user.", "error")
    else:
        add_authorized_email(email, added_by=current_user() or "self-service")
        log_audit(current_user() or email, "AUTHORIZED_USER", detail=email)
        flash(f"{email} is now authorised and can sign in with the shared password.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/auth/callback")
def callback():
    if request.args.get("state") != session.get("oauth_state"):
        flash("Login state mismatch. Please try again.", "error")
        return redirect(url_for("auth.login"))
    code = request.args.get("code")
    if not code:
        flash("Authorization was cancelled.", "error")
        return redirect(url_for("auth.login"))

    token_url = current_app.config["ZOHO_ACCOUNTS_BASE"] + "/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["ZOHO_CLIENT_ID"],
        "client_secret": current_app.config["ZOHO_CLIENT_SECRET"],
        "redirect_uri": current_app.config["ZOHO_REDIRECT_URI"],
        "code": code,
    }
    try:
        tok = requests.post(token_url, data=data, timeout=15).json()
        access_token = tok["access_token"]
        ui = requests.get(
            current_app.config["ZOHO_ACCOUNTS_BASE"] + "/oauth/user/info",
            headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
            timeout=15,
        ).json()
        email = (ui.get("Email") or ui.get("email") or "").strip().lower()
    except Exception as exc:  # noqa
        flash(f"Could not complete Zoho sign-in: {exc}", "error")
        return redirect(url_for("auth.login"))

    if not is_authorized(email):
        flash(f"{email or 'This account'} is not authorised to use this tool.", "error")
        return redirect(url_for("auth.login"))

    _complete_login(email)
    return redirect(url_for("main.dashboard"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
