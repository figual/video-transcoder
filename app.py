from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi import Request
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
    resolution: str = Form("1280x720"),
    inline: bool = Form(False)
):
    input_path = f"videos/{file.filename}"
    output_path = f"videos/output_{file.filename}"

    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Si el usuario quiere el resultado inline y el archivo es pequeño
    if inline and len(content) < 10 * 1024 * 1024:  # 10 MB
        transcode(input_path, output_path, codec, bitrate, resolution)
        return FileResponse(output_path, media_type="video/mp4", filename=f"transcoded_{file.filename}")

    # Si no, encolamos el trabajo como siempre
    job = q.enqueue(transcode, input_path, output_path, codec, bitrate, resolution)
    return {"job_id": job.get_id(), "status": job.get_status()}

@app.get("/download/{job_id}")
def download_result(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)

    if not job.is_finished:
        return {"status": job.get_status(), "message": "Job not finished yet"}

    output_path = job.result
    if not output_path or not os.path.exists(output_path):
        return {"status": "error", "message": "Output file not found"}

    return FileResponse(output_path, media_type="video/mp4", filename=os.path.basename(output_path))


@app.get("/status/{job_id}")
def get_status(job_id: str, request: Request):
    job = Job.fetch(job_id, connection=redis_conn)
    status = job.get_status()

    response = {"status": status}

    if status == "finished" and job.result and os.path.exists(job.result):
        base_url = str(request.base_url).rstrip("/")
        response["download_url"] = f"{base_url}/download/{job_id}"

    return response

