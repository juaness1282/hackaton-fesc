from fastapi import FastAPI, HTTPException
import db_adapter

api = FastAPI(title="Legacy Escape", version="1.0.0")

@api.get("/health")
def health():
    return {"status": "UP", "legacy": "UP" if db_adapter.available() else "DOWN"}

def found(record):
    if record is None:
        raise HTTPException(404, "Registro no encontrado")
    return record

@api.get("/api/v1/members/{document}")
def member(document: str):
    return found(db_adapter.get_member(document))

@api.get("/api/v1/members/{document}/beneficiaries")
def beneficiaries(document: str):
    return found(db_adapter.get_beneficiaries(document))

@api.get("/api/v1/companies/{id}")
def company(id: str):
    return found(db_adapter.get_company(id))
