import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

class Mobile(BaseHTTPRequestHandler):
    def respond(self,code,body,mime="application/json"):
        self.send_response(code)
        self.send_header("Content-Type",mime+"; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path=="/":
            return self.respond(200,Path("index.html").read_bytes(),"text/html")
        if self.path=="/health":
            return self.respond(200,b'{"status":"UP"}')
        match=re.fullmatch(r"/members/([0-9]{1,15})(/beneficiaries)?",self.path)
        if not match:
            return self.respond(404,b'{"message":"Ruta no encontrada"}')
        url=os.environ["GATEWAY_URL"].rstrip("/")+"/api/v1/members/"+match[1]+(match[2] or "")
        request=urllib.request.Request(url,headers={"Authorization":"Bearer "+os.environ["MOBILE_TOKEN"]})
        try:
            with urllib.request.urlopen(request,timeout=4) as response:
                return self.respond(response.status,response.read())
        except urllib.error.HTTPError as exc:
            return self.respond(exc.code,exc.read())
        except (urllib.error.URLError,TimeoutError):
            return self.respond(503,b'{"message":"Servicio no disponible"}')

    def do_POST(self):
        return self.respond(403,b'{"message":"Solo lectura"}')

    def log_message(self,*args):
        pass

ThreadingHTTPServer(("0.0.0.0",8093),Mobile).serve_forever()
