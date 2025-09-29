from fastapi import FastAPI, File, UploadFile, Form
from redis import Redis
from rq import Queue
from rq.job import Job
from tasks import transcode
from prometheus_fastapi_instrumentator import Instrumentator
import os
import time

app = FastAPI()
Instrumentator().instrument(app).expose(app)

def connect_redis():
    for _ in range(10):
        try:
            redis_conn = Redis(host="redis", port=6379)
            redis_conn.ping()
            return redis_conn
        except:
            print("Redis not ready, retrying...")
            time.sleep(2)
    raise Exception("Redis connection failed")

redis_conn = connect_redis()
q = Queue(connection=redis_conn)

@app.post("/transcode")
async def enqueue_transcoding(
    file: UploadFile = File(...),
    codec: str = Form("libx264"),
    bitrate: str = Form("1000k"),
    resolution: str = Form("1280x720")
):
    input_path = f"videos/{file.filename}"
    output_path = f"videos/output_{file.filename}"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    job = q.enqueue(transcode, input_path, output_path, codec, bitrate, resolution)
    return {"job_id": job.get_id(), "status": job.get_status()}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)
    return {"status": job.get_status()}

