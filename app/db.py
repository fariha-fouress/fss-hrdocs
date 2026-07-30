"""SQLite persistence: documents + audit_log."""
import sqlite3
import json
import os
from datetime import datetime, timezone
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    created_by   TEXT NOT NULL,
    doc_type     TEXT NOT NULL,       -- offer_letter | service_agreement | ncnda
    entity       TEXT NOT NULL,       -- entity key
    entity_label TEXT NOT NULL,
    candidate    TEXT NOT NULL,
    role         TEXT,
    employment   TEXT,                -- employee | contractor
    signatory    TEXT,
    form_json    TEXT NOT NULL,       -- original form inputs
    body_html    TEXT NOT NULL,       -- finalised (possibly edited) document HTML
    status       TEXT NOT NULL DEFAULT 'draft'  -- draft | finalised
);

CREATE TABLE IF NOT EXISTS audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,
    actor_email   TEXT NOT NULL,
    action        TEXT NOT NULL,      -- GENERATED | FINALISED | DOWNLOAD_PDF | DOWNLOAD_DOCX | EMAIL_SENT | EMAIL_FAILED | LOGIN
    document_id   INTEGER,
    doc_type      TEXT,
    candidate     TEXT,
    entity_label  TEXT,
    detail        TEXT
);
"""


def get_db():
    if "db" not in g:
        path = current_app.config["DB_PATH"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()
    app.teardown_appcontext(close_db)


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def save_document(actor, meta, body_html, status="finalised"):
    db = get_db()
    cur = db.execute(
        """INSERT INTO documents
           (created_at, created_by, doc_type, entity, entity_label, candidate,
            role, employment, signatory, form_json, body_html, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (_now(), actor, meta["doc_type"], meta["entity"], meta["entity_label"],
         meta["candidate"], meta.get("role"), meta.get("employment"),
         meta.get("signatory"), json.dumps(meta.get("form", {})), body_html, status),
    )
    db.commit()
    return cur.lastrowid


def get_document(doc_id):
    db = get_db()
    return db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()


def update_document_body(doc_id, body_html, status="finalised"):
    db = get_db()
    db.execute("UPDATE documents SET body_html=?, status=? WHERE id=?",
               (body_html, status, doc_id))
    db.commit()


def log_audit(actor, action, document_id=None, doc_type=None, candidate=None,
              entity_label=None, detail=None):
    db = get_db()
    db.execute(
        """INSERT INTO audit_log
           (ts, actor_email, action, document_id, doc_type, candidate, entity_label, detail)
           VALUES (?,?,?,?,?,?,?,?)""",
        (_now(), actor, action, document_id, doc_type, candidate, entity_label, detail),
    )
    db.commit()


def recent_audit(limit=200):
    db = get_db()
    return db.execute(
        "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()


def recent_documents(limit=100):
    db = get_db()
    return db.execute(
        "SELECT * FROM documents ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
