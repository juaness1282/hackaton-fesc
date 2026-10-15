"""Durable acceptance is independent of the legacy database."""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DIRECTORY=Path(os.getenv("STATE_DIR","data"))

@contextmanager
def session():
    DIRECTORY.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DIRECTORY/"requests.sqlite",timeout=2)
    db.row_factory=sqlite3.Row
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, payload TEXT NOT NULL, owner TEXT NOT NULL, state TEXT NOT NULL, movement INTEGER, created REAL NOT NULL)")
        with db:
            yield db
    finally:
        db.close()

class ContentConflict(Exception):
    pass

def enqueue(payload,owner):
    canonical=json.dumps(payload,sort_keys=True)
    with session() as db:
        db.execute("INSERT OR IGNORE INTO jobs VALUES (?,?,?,'pending',NULL,?)",(payload["requestId"],canonical,owner,time.time()))
        row=dict(db.execute("SELECT * FROM jobs WHERE id=?",(payload["requestId"],)).fetchone())
        if row["payload"]!=canonical:
            raise ContentConflict()
        return row

def load(identifier):
    with session() as db:
        row=db.execute("SELECT * FROM jobs WHERE id=?",(identifier,)).fetchone()
        return dict(row) if row else None

def waiting():
    with session() as db:
        return [dict(row) for row in db.execute("SELECT * FROM jobs WHERE state='pending' AND created<? ORDER BY created LIMIT 25",(time.time()-2,))]

def complete(identifier,status,movement=None):
    with session() as db:
        db.execute("UPDATE jobs SET state=?,movement=? WHERE id=?",(status,movement,identifier))
