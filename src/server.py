from fastapi import FastAPI
import db_adapter

api = FastAPI(title="Legacy Escape", version="1.0.0")

@api.get("/health")
def health():
    return {"status": "UP", "legacy": "UP" if db_adapter.available() else "DOWN"}
