"""SQLite persistence: documents, audit_log, authorized_users, custom_jds."""
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
    doc_type     TEXT NOT NULL,
    entity       TEXT NOT NULL,
    entity_label TEXT NOT NULL,
    candidate    TEXT NOT NULL,
    role         TEXT,
    employment   TEXT,
    signatory    TEXT,
    form_json    TEXT NOT NULL,
    body_html    TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,
    actor_email   TEXT NOT NULL,
    action        TEXT NOT NULL,
    document_id   INTEGER,
    doc_type      TEXT,
    candidate     TEXT,
    entity_label  TEXT,
    detail        TEXT
);

CREATE TABLE IF NOT EXISTS authorized_users (
    email      TEXT PRIMARY KEY,
    added_by   TEXT,
    added_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS custom_jds (
    title      TEXT PRIMARY KEY,
    html       TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    key            TEXT PRIMARY KEY,
    label          TEXT NOT NULL,
    is_system      INTEGER NOT NULL DEFAULT 0,
    sort_order     INTEGER NOT NULL DEFAULT 100,
    data_json      TEXT NOT NULL,
    letterhead_ref TEXT,
    handbook_html  TEXT,
    updated_by     TEXT,
    updated_at     TEXT NOT NULL
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
    return db.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def recent_documents(limit=100):
    db = get_db()
    return db.execute("SELECT * FROM documents ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


# --- authorized users (runtime allowlist, in addition to env seed) --------
def add_authorized_email(email, added_by=""):
    db = get_db()
    db.execute("INSERT OR IGNORE INTO authorized_users (email, added_by, added_at) VALUES (?,?,?)",
               (email.strip().lower(), added_by, _now()))
    db.commit()


def list_authorized_emails():
    db = get_db()
    return [r["email"] for r in db.execute("SELECT email FROM authorized_users").fetchall()]


# --- custom job descriptions (saved for reuse) ----------------------------
def add_custom_jd(title, html, created_by=""):
    db = get_db()
    db.execute(
        """INSERT INTO custom_jds (title, html, created_by, created_at) VALUES (?,?,?,?)
           ON CONFLICT(title) DO UPDATE SET html=excluded.html""",
        (title.strip(), html, created_by, _now()))
    db.commit()


def list_custom_jds():
    db = get_db()
    return db.execute("SELECT title, html FROM custom_jds ORDER BY title").fetchall()


def get_custom_jd(title):
    db = get_db()
    r = db.execute("SELECT html FROM custom_jds WHERE title=?", (title.strip(),)).fetchone()
    return r["html"] if r else None


# --- locations (entities + letterheads + handbooks, user-managed) ----------
def count_locations():
    db = get_db()
    return db.execute("SELECT COUNT(*) AS n FROM locations").fetchone()["n"]


def list_locations():
    db = get_db()
    return db.execute(
        "SELECT * FROM locations ORDER BY sort_order, label").fetchall()


def get_location(key):
    db = get_db()
    return db.execute("SELECT * FROM locations WHERE key=?", (key,)).fetchone()


def upsert_location(key, label, data_json, letterhead_ref=None,
                    handbook_html="", is_system=0, sort_order=100, updated_by=""):
    db = get_db()
    db.execute(
        """INSERT INTO locations
             (key, label, is_system, sort_order, data_json, letterhead_ref,
              handbook_html, updated_by, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?)
           ON CONFLICT(key) DO UPDATE SET
             label=excluded.label,
             sort_order=excluded.sort_order,
             data_json=excluded.data_json,
             letterhead_ref=COALESCE(excluded.letterhead_ref, locations.letterhead_ref),
             handbook_html=excluded.handbook_html,
             updated_by=excluded.updated_by,
             updated_at=excluded.updated_at""",
        (key, label, is_system, sort_order, data_json, letterhead_ref,
         handbook_html, updated_by, _now()))
    db.commit()


def set_location_letterhead(key, letterhead_ref, updated_by=""):
    db = get_db()
    db.execute("UPDATE locations SET letterhead_ref=?, updated_by=?, updated_at=? WHERE key=?",
               (letterhead_ref, updated_by, _now(), key))
    db.commit()


def delete_location(key):
    db = get_db()
    db.execute("DELETE FROM locations WHERE key=?", (key,))
    db.commit()
