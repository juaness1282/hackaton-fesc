import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
import psycopg
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def failure(status, message, **extra):
    return JSONResponse(status_code=status, content={"message":message, "error_id":str(uuid.uuid4()), **extra})

def install(api):
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger("request_audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.FileHandler("logs/audit.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    @api.middleware("http")
    async def record(request: Request, call_next):
        started = time.monotonic()
        code = 500
        try:
            response = await call_next(request)
            code = response.status_code
            return response
        finally:
            path = re.sub(r"(/(?:members|retirement-requests)/)[^/]+", r"\1****", request.url.path)
            logger.info(json.dumps({"timestamp":datetime.now(timezone.utc).isoformat(),
                "consumer":getattr(request.state,"consumer","unknown"), "endpoint":path,
                "status":code, "latency_ms":round((time.monotonic()-started)*1000,2)}))

    @api.exception_handler(HTTPException)
    def http_error(request, exc):
        return failure(exc.status_code, str(exc.detail))

    @api.exception_handler(RequestValidationError)
    def validation_error(request, exc):
        return failure(422, "Datos de solicitud inválidos")

    @api.exception_handler(psycopg.Error)
    def database_error(request, exc):
        return failure(503, "Base temporalmente no disponible", code="LEGACY_UNAVAILABLE")

    @api.exception_handler(Exception)
    def internal_error(request, exc):
        return failure(500, "Error interno")
