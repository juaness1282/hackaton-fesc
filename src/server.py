from fastapi import FastAPI, HTTPException, Depends
from access import consumer
import schemas
import db_adapter
import inbox
import dispatcher
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifecycle(api):
    with inbox.session():
        pass
    shutdown,worker=dispatcher.launch()
    yield
    shutdown.set()
    worker.join(timeout=3)

from observability import install

api = FastAPI(title="Legacy Escape", version="1.0.0", lifespan=lifecycle, responses={code:{"model":schemas.Error} for code in (401,403,404,409,422,503)})
install(api)

@api.get("/health",response_model=schemas.Health)
def health():
    return {"status": "UP", "legacy": "UP" if db_adapter.available() else "DOWN"}

def found(record):
    if record is None:
        raise HTTPException(404, "Registro no encontrado")
    return record

@api.get("/api/v1/members/{document}",response_model=schemas.Member, dependencies=[Depends(consumer)])
def member(document: str):
    return found(db_adapter.get_member(document))

@api.get("/api/v1/members/{document}/beneficiaries",response_model=list[schemas.Beneficiary], dependencies=[Depends(consumer)])
def beneficiaries(document: str):
    return found(db_adapter.get_beneficiaries(document))

@api.get("/api/v1/companies/{id}",response_model=schemas.Company, dependencies=[Depends(consumer)])
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

@api.post("/api/v1/members/{document}/retirements",status_code=201,response_model=schemas.Receipt,responses={200:{"model":schemas.Receipt,"description":"Repetición confirmada"},202:{"model":schemas.Receipt,"description":"Persistido y pendiente de recuperación"}})
def retirement(document: str, body: RetirementInput, author: str=Depends(consumer)):
    if not re.fullmatch(r"[0-9]{1,15}",document):
        raise HTTPException(422,"Documento inválido")
    payload=body.model_dump(mode="json")
    payload["document"]=document
    try:
        job=inbox.enqueue(payload,author)
    except inbox.ContentConflict:
        raise HTTPException(409,"requestId pertenece a otra solicitud")
    created=False
    if job["state"]=="pending":
        created=dispatcher.deliver(job)
        job=inbox.load(body.requestId)
    if job["state"]=="not_found":
        raise HTTPException(404,"Registro no encontrado")
    if job["state"]=="conflict":
        raise HTTPException(409,"requestId pertenece a otra solicitud")
    code=202 if job["state"]=="pending" else (201 if created else 200)
    return JSONResponse(status_code=code,content={"requestId":body.requestId,"movement":job["movement"],"status":job["state"]})

@api.get("/api/v1/retirement-requests/{request_id}",response_model=schemas.Receipt,dependencies=[Depends(consumer)])
def request_status(request_id: str):
    job=found(inbox.load(request_id))
    return {"requestId":request_id,"status":job["state"],"movement":job["movement"]}

import migration

@api.get("/api/v1/migration/status",response_model=schemas.Migration,dependencies=[Depends(consumer)])
def migration_status():
    return {"domains":migration.current()}
