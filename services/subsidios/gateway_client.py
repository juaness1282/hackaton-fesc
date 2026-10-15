import json
import os
import uuid
import urllib.request
import urllib.error

def send(data, request_id=None):
    document = str(data["documento"])
    if not document.isascii() or not document.isdigit() or len(document) > 15:
        return 422, {"message":"Documento inválido"}
    request_id = request_id or data.get("requestId") or str(uuid.uuid4())
    body = {"requestId":request_id, "date":data["fecha"], "reason":data.get("motivo","RETIRO")}
    request = urllib.request.Request(
        os.environ["GATEWAY_URL"].rstrip("/")+"/api/v1/members/"+document+"/retirements",
        data=json.dumps(body).encode(), headers={"Content-Type":"application/json",
        "Authorization":"Bearer "+os.environ["SUBSIDIOS_TOKEN"]})
    try:
        with urllib.request.urlopen(request,timeout=4) as response:
            result=json.load(response)
            return response.status, {"movimiento":result.get("movement"),"requestId":request_id,"status":result.get("status")}
    except urllib.error.HTTPError as exc:
        return exc.code,json.load(exc)
    except (urllib.error.URLError,TimeoutError):
        return 503, {"message":"Gateway no disponible; reintente con el mismo requestId","requestId":request_id}
