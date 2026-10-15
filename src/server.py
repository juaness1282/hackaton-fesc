from fastapi import FastAPI, HTTPException, Depends
from access import consumer
import db_adapter
from observability import install

api = FastAPI(title="Legacy Escape", version="1.0.0")
install(api)

@api.get("/health")
def health():
    return {"status": "UP", "legacy": "UP" if db_adapter.available() else "DOWN"}

def found(record):
    if record is None:
        raise HTTPException(404, "Registro no encontrado")
    return record

@api.get("/api/v1/members/{document}", dependencies=[Depends(consumer)])
def member(document: str):
    return found(db_adapter.get_member(document))

@api.get("/api/v1/members/{document}/beneficiaries", dependencies=[Depends(consumer)])
def beneficiaries(document: str):
    return found(db_adapter.get_beneficiaries(document))

@api.get("/api/v1/companies/{id}", dependencies=[Depends(consumer)])
def company(id: str):
    return found(db_adapter.get_company(id))

from datetime import date
import re
from pydantic import BaseModel, Field, ConfigDict
from fastapi.responses import JSONResponse

class RetirementInput(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True, extra="forbid")
    requestId: str=Field(min_length=1,max_length=128)
    date: date
    reason: str=Field(min_length=1,max_length=200)

@api.post("/api/v1/members/{document}/retirements")
def retirement(document: str, body: RetirementInput, author: str=Depends(consumer)):
    if not re.fullmatch(r"[0-9]{1,15}",document):
        raise HTTPException(422,"Documento inválido")
    try:
        result=db_adapter.save_retirement(document,body.requestId,body.date,body.reason,author)
    except db_adapter.ReusedRequest:
        raise HTTPException(409,"requestId pertenece a otra solicitud")
    created,movement=found(result)
    return JSONResponse(status_code=201 if created else 200,content={"requestId":body.requestId,"movement":movement,"status":"completed"})
