import json
import os
import re
import tempfile
from pathlib import Path
import inbox

def current():
    path=inbox.DIRECTORY/"domains.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"affiliations":"DUAL","retirements":"DUAL","companies":"LEGACY"}

def change(mode):
    if mode not in {"LEGACY","DUAL","MODERN"}:
        raise ValueError("Estado inválido")
    inbox.DIRECTORY.mkdir(parents=True,exist_ok=True)
    states=current()
    states.update(affiliations=mode,retirements=mode)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=inbox.DIRECTORY,delete=False) as temp:
        json.dump(states,temp)
        temp.flush()
        os.fsync(temp.fileno())
        filename=temp.name
    os.replace(filename,inbox.DIRECTORY/"domains.json")
    plan=Path("docs/migration-plan.md")
    if plan.exists():
        text=plan.read_text(encoding="utf-8")
        text=re.sub(r"(\| (?:Afiliaciones|Retiros) \| )\w+( \|)",lambda m:m[1]+mode+m[2],text)
        plan.write_text(text,encoding="utf-8")
    return states

if __name__=="__main__":
    import sys
    print(json.dumps(change(sys.argv[1])))
