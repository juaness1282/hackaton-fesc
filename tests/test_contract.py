import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
import httpx
import psycopg
import pytest

BASE=os.getenv("GATEWAY_URL","http://gateway:8082")
DOC="1019886173"
MEMBER="/api/v1/members/"+DOC

def call(method,path,token="PORTAL_TOKEN",body=None):
    return httpx.request(method,BASE+path,headers={"Authorization":"Bearer "+os.environ[token]} if token else {},
        json=body,timeout=5)

def body():
    identifier=str(uuid.uuid4())
    return {"requestId":identifier,"date":"2026-10-14","reason":"test-"+identifier}

def count_movements(reason):
    with psycopg.connect(host=os.environ["LEGACY_DB_HOST"],dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],password=os.environ["POSTGRES_PASSWORD"],connect_timeout=2) as db:
        return db.execute("SELECT count(*) FROM logmov WHERE obs_mov=%s",(reason,)).fetchone()[0]

@pytest.fixture(scope="session",autouse=True)
def ready():
    for _ in range(40):
        try:
            if call("GET","/health").json()["legacy"]=="UP":return
        except (httpx.HTTPError,ValueError,KeyError):pass
        time.sleep(.25)
    pytest.fail("Gateway o base no disponible")

def test_health():
    assert call("GET","/health").json()=={"status":"UP","legacy":"UP"}

def test_member():
    result=call("GET",MEMBER)
    assert result.status_code==200
    assert result.json()["fullName"]=="MONICA PABON MENDOZA"
    assert result.json()["document"]==DOC

def test_beneficiaries():
    result=call("GET",MEMBER+"/beneficiaries")
    assert result.status_code==200
    assert isinstance(result.json(),list)
    for row in result.json():
        assert set(row)=={"document","fullName","relationship"}

def test_company_count():
    result=call("GET","/api/v1/companies/2015")
    assert result.status_code==200
    with psycopg.connect(host=os.environ["LEGACY_DB_HOST"],dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],password=os.environ["POSTGRES_PASSWORD"]) as db:
        renamed=db.execute("SELECT to_regclass('public.person_master') IS NOT NULL").fetchone()[0]
        query="SELECT count(*) FROM person_master WHERE status_code='A' AND cod_emp=%s" if renamed else "SELECT count(*) FROM afi_mae WHERE est_afi='A' AND cod_emp=%s"
        assert result.json()["activeMembers"]==db.execute(query,("2015",)).fetchone()[0]

def test_missing_token():
    assert call("GET",MEMBER,token=None).status_code==401

def test_mobile_access():
    assert call("GET",MEMBER,token="MOBILE_TOKEN").status_code==200
    assert call("POST",MEMBER+"/retirements",token="MOBILE_TOKEN",body=body()).status_code==403

def test_missing_record():
    result=call("GET","/api/v1/members/000000000000000")
    assert result.status_code==404
    assert set(result.json())=={"message","error_id"}

def test_retirement_exactly_once():
    data=body()
    first=call("POST",MEMBER+"/retirements",token="SUBSIDIOS_TOKEN",body=data)
    second=call("POST",MEMBER+"/retirements",token="SUBSIDIOS_TOKEN",body=data)
    assert (first.status_code,second.status_code)==(201,200)
    assert first.json()==second.json()
    assert count_movements(data["reason"])==1
    assert call("GET",MEMBER).json()["status"]=="RETIRED"

def test_concurrent_request():
    data=body()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:call("POST",MEMBER+"/retirements",body=data),range(2)))
    assert sorted(r.status_code for r in results)==[200,201]
    assert results[0].json()==results[1].json()
    assert count_movements(data["reason"])==1

def test_conflicting_request():
    data=body()
    assert call("POST",MEMBER+"/retirements",body=data).status_code==201
    data["reason"]="Otro contenido"
    assert call("POST",MEMBER+"/retirements",body=data).status_code==409

def test_invalid_request():
    data=body()
    data["date"]="invalid"
    assert call("POST",MEMBER+"/retirements",body=data).status_code==422

def test_subsidios():
    value=body()
    data={"documento":DOC,"fecha":value["date"],"motivo":value["reason"],"requestId":value["requestId"]}
    a=httpx.post("http://subsidios-app:8091/retiros",json=data)
    b=httpx.post("http://subsidios-app:8091/retiros",json=data)
    assert (a.status_code,b.status_code)==(201,200)
    assert a.json()["movimiento"]==b.json()["movimiento"]
    assert count_movements(value["reason"])==1

def test_existing_consumers():
    assert httpx.get("http://educacion-app:8090/afiliados/"+DOC).json()["estado"]=="RETIRADO"
    assert httpx.get("http://portal-client:8092/portal/afiliados/"+DOC).json()["afiliado"]["status"]=="RETIRED"

def test_mobile_consumer():
    assert httpx.get("http://mobile-client:8093/members/"+DOC).status_code==200
    assert httpx.get("http://mobile-client:8093/members/"+DOC+"/beneficiaries").status_code==200
    assert httpx.post("http://mobile-client:8093/members/"+DOC,json={}).status_code==403

def test_migration_status():
    assert call("GET","/api/v1/migration/status").json()["domains"]["affiliations"] in {"LEGACY","DUAL","MODERN"}
