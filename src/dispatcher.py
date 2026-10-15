import json
import threading
from datetime import date
import psycopg
import db_adapter
import inbox

def deliver(job):
    data=json.loads(job["payload"])
    try:
        result=db_adapter.save_retirement(data["document"],data["requestId"],date.fromisoformat(data["date"]),data["reason"],job["owner"])
        if result is None:
            inbox.complete(job["id"],"not_found")
        else:
            created,movement=result
            inbox.complete(job["id"],"completed",movement)
            return created
    except db_adapter.ReusedRequest:
        inbox.complete(job["id"],"conflict")
    except psycopg.Error:
        pass  # Keep accepted requests pending, including ambiguous commits.
    return False

def launch():
    shutdown=threading.Event()
    def work():
        while not shutdown.wait(.5):
            try:
                for job in inbox.waiting():
                    if shutdown.is_set(): break
                    deliver(job)
            except Exception:
                # Failure never removes or acknowledges a job.
                continue
    thread=threading.Thread(target=work,daemon=True)
    thread.start()
    return shutdown,thread
