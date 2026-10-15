"""Run destructive kit events from the host; only synthetic data is modified."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import urllib.error
import uuid

ROOT=Path(__file__).resolve().parents[1]
ENV=dict(line.split("=",1) for line in (ROOT/".env").read_text(encoding="utf-8").splitlines() if "=" in line and not line.startswith("#"))
REPORT={"passed":[],"status":"running"}
START=time.monotonic()

def compose(*args,input=None):
    result=subprocess.run(["docker","compose",*args],cwd=ROOT,input=input,text=True,capture_output=True,timeout=90)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout

def bash(script,*args):
    executable=r"C:\Program Files\Git\bin\bash.exe" if os.name=="nt" else shutil.which("bash")
    subprocess.run([executable,script,*args],cwd=ROOT,check=True,capture_output=True,timeout=90)

def call(path,body=None,base="http://localhost:8082"):
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+ENV["SUBSIDIOS_TOKEN"]})
    try:
        with urllib.request.urlopen(req,timeout=5) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as exc:return exc.code,json.load(exc)

def ready():
    for _ in range(40):
        try:
            if call("/health")[0]==200:return
        except OSError:pass
        time.sleep(.25)
    raise AssertionError("Gateway no disponible")

def record(message):
    REPORT["passed"].append(message)
    print(message+": OK",flush=True)

def count(reason):
    assert reason.replace("-","").isalnum()
    output=compose("exec","-T","legacy-db","sh","-c",
        'psql -At -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"',
        input="SELECT count(*) FROM logmov WHERE obs_mov='"+reason+"';\n")
    return int(output.strip())

try:
    ready()
    paths=["/api/v1/members/1019886173","/api/v1/members/1019886173/beneficiaries","/api/v1/companies/2015"]
    before=[call(path) for path in paths]
    assert all(status==200 for status,_ in before)
    bash("scripts/schema-change.sh")
    assert before==[call(path) for path in paths]
    record("Contrato idéntico después de cambiar esquema")

    identifier=str(uuid.uuid4())
    reason="outage-"+identifier
    payload={"requestId":identifier,"date":"2026-10-14","reason":reason}
    try:
        compose("stop","legacy-db")
        started=time.monotonic()
        status,value=call(paths[0])
        assert status==503 and value["code"]=="LEGACY_UNAVAILABLE"
        assert time.monotonic()-started<3
        assert call("/health")[1]["legacy"]=="DOWN"
        record("Consultas con base caída responden 503 en menos de tres segundos")
        assert call(paths[0]+"/retirements",payload)[0]==202
        assert call(paths[0]+"/retirements",payload)[0]==202
        compose("restart","gateway")
        ready()
        assert call("/api/v1/retirement-requests/"+identifier)[1]["status"]=="pending"
        record("Retiro aceptado sobrevive al reinicio del gateway")
    finally:
        compose("start","legacy-db")
    for _ in range(60):
        value=call("/api/v1/retirement-requests/"+identifier)[1]
        if value["status"]=="completed":break
        time.sleep(.3)
    assert value["status"]=="completed"
    assert call(paths[0]+"/retirements",payload)[0]==200
    assert count(reason)==1
    record("Recuperación con exactamente un movimiento")

    bash("rollback.sh","affiliations")
    assert call("/api/v1/migration/status")[1]["domains"]["affiliations"]=="LEGACY"
    compose("restart","gateway")
    ready()
    assert call("/api/v1/migration/status")[1]["domains"]["affiliations"]=="LEGACY"
    compose("stop","gateway")
    reason="rollback-"+str(uuid.uuid4())
    status,_=call("/retiros",{"documento":"1019886173","fecha":"2026-10-14","motivo":reason},base="http://localhost:8091")
    assert status==201 and count(reason)==1
    bash("rollback.sh","affiliations")
    record("Rollback persistente y Subsidios operativo con gateway apagado")
    REPORT["status"]="passed"
finally:
    try:
        compose("start","legacy-db")
        compose("run","--rm","--no-deps","gateway","python","migration.py","DUAL")
        compose("start","gateway")
        ready()
    finally:
        REPORT["seconds"]=round(time.monotonic()-START,2)
        if REPORT["status"]=="running":REPORT["status"]="failed"
        (ROOT/"test-results").mkdir(exist_ok=True)
        (ROOT/"test-results/events.json").write_text(json.dumps(REPORT,ensure_ascii=False,indent=2),encoding="utf-8")
