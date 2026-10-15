import hmac
import os
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

scheme = HTTPBearer(auto_error=False)

def consumer(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(scheme)):
    supplied = request.headers.get("Authorization", "").encode()
    for name in ("portal", "subsidios", "mobile"):
        secret = os.getenv(name.upper() + "_TOKEN")
        if secret and hmac.compare_digest(supplied, ("Bearer " + secret).encode()):
            request.state.consumer = name
            if request.method not in ("GET", "HEAD") and name == "mobile":
                raise HTTPException(403, "Este consumidor es de solo lectura")
            return name
    raise HTTPException(401, "Token requerido o inválido")
