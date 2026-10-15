"""PostgreSQL boundary: physical schema is private to this module."""
import os
import psycopg
from psycopg.rows import dict_row

def connection():
    return psycopg.connect(
        host=os.getenv("LEGACY_DB_HOST", "legacy-db"),
        port=os.getenv("LEGACY_DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], connect_timeout=1,
        options="-c statement_timeout=1000 -c lock_timeout=500", row_factory=dict_row,
    )

def available():
    try:
        with connection() as db:
            db.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False

from psycopg import sql

def layout(db):
    renamed = db.execute("SELECT to_regclass('public.person_master') IS NOT NULL AS renamed").fetchone()["renamed"]
    return ("person_master", "document_number", "status_code") if renamed else ("afi_mae", "nro_doc", "est_afi")

def display_name(record):
    return " ".join(str(record[key]).strip() for key in ("nom1", "nom2", "ape1", "ape2") if record.get(key))

def get_member(document):
    with connection() as db:
        table, column, status = layout(db)
        query = sql.SQL("SELECT p.*, p.{doc} AS document, p.{state} AS state, e.nom_emp FROM {table} p LEFT JOIN empresa e ON e.cod_emp=p.cod_emp WHERE p.{doc}=%s").format(doc=sql.Identifier(column), state=sql.Identifier(status), table=sql.Identifier(table))
        row = db.execute(query, (document,)).fetchone()
        if row is None:
            return None
        return {"document": row["document"], "fullName": display_name(row), "status": {"A":"ACTIVE", "R":"RETIRED", "S":"SUSPENDED"}[row["state"]], "company": {"id":row["cod_emp"], "name":row["nom_emp"]}}

def get_beneficiaries(document):
    with connection() as db:
        table, column, _ = layout(db)
        exists = db.execute(sql.SQL("SELECT 1 FROM {} WHERE {}=%s").format(sql.Identifier(table), sql.Identifier(column)), (document,)).fetchone()
        if not exists:
            return None
        rows = db.execute("SELECT * FROM afi_ben WHERE nro_doc=%s ORDER BY nro_doc_ben", (document,)).fetchall()
        relations = {"C":"SPOUSE", "H":"CHILD", "P":"FATHER", "M":"MOTHER"}
        return [{"document":r["nro_doc_ben"], "fullName":display_name(r), "relationship":relations[r["cod_par"]]} for r in rows]

def get_company(identifier):
    with connection() as db:
        table, _, status = layout(db)
        query = sql.SQL("SELECT e.cod_emp AS id, e.nom_emp AS name, (SELECT count(*) FROM {table} p WHERE p.cod_emp=e.cod_emp AND p.{status}='A') AS total FROM empresa e WHERE e.cod_emp=%s").format(table=sql.Identifier(table), status=sql.Identifier(status))
        row = db.execute(query, (identifier,)).fetchone()
        return None if row is None else {"id":row["id"], "name":row["name"], "activeMembers":row["total"]}
