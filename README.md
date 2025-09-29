# 🎬 Video Transcoder API

Sistema distribuido de transcodificación de vídeo con cola de procesamiento, métricas Prometheus y orquestación con Docker Compose.

## 🧱 Estructura del proyecto

```
video-transcoder/
├── app.py
├── tasks.py
├── worker.py
├── Dockerfile
├── requirements.txt
├── docker-compose.yml
├── prometheus.yml
└── videos/
```

## 🚀 Descripción de componentes

- **FastAPI**: expone la API REST para subir vídeos y consultar estado.
- **Redis + RQ**: gestiona la cola de trabajos de transcodificación.
- **FFmpeg**: realiza la transcodificación.
- **Prometheus**: recolecta métricas de la API.
- **Docker Compose**: orquesta todos los servicios.

## 📦 Dependencias (`requirements.txt`)

```
fastapi
uvicorn
rq
redis
prometheus_fastapi_instrumentator
```

## 🐍 Código fuente

### `tasks.py`

```python
import subprocess

def transcode(input_path, output_path, codec, bitrate, resolution):
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", codec, "-b:v", bitrate, "-s", resolution,
        output_path
    ]
    subprocess.run(command)
    return output_path
```

### `app.py`

```python
from fastapi import FastAPI, File, UploadFile, Form
from redis import Redis
from rq import Queue
from rq.job import Job
from tasks import transcode
from prometheus_fastapi_instrumentator import Instrumentator
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
```

### `worker.py`

```python
from redis import Redis
from rq import Worker

redis_conn = Redis(host="redis", port=6379)

worker = Worker(queues=["default"], connection=redis_conn)
worker.work()
```

## 🐳 Docker

### `Dockerfile`

```Dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
```

### `prometheus.yml`

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'video-transcoder'
    static_configs:
      - targets: ['api:8000']
```

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: api
    command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
    ports:
      - "8000:8000"
    volumes:
      - ./videos:/app/videos
    depends_on:
      - redis

  worker:
    build: .
    container_name: worker
    command: ["python", "worker.py"]
    volumes:
      - ./videos:/app/videos
    depends_on:
      - redis

  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

## ▶️ Ejecución

```bash
docker-compose down -v
docker-compose up --build
```

## 🧪 Pruebas

### Enviar vídeo:

```bash
curl -X POST http://localhost:8000/transcode \
  -F "file=@video.mp4" \
  -F "codec=libx264" \
  -F "bitrate=1000k" \
  -F "resolution=1280x720"
```

### Consultar estado:

```bash
curl http://localhost:8000/status/<job_id>
```

### Ver métricas:

Accede a [http://localhost:9090](http://localhost:9090)

## 📈 Próximos pasos

- Añadir Grafana para dashboards
- Escalar workers horizontalmente
- Añadir autenticación a la API
- Desplegar en Kubernetes o en la nube
EOF
```

Este comando crea el archivo completo con todos los bloques de código correctamente formateados.

---

## 📁 Opción 2: Pegar en VS Code sin perder formato

1. Abre VS Code.
2. Crea un nuevo archivo llamado `README.md`.
3. Pega el contenido que te di antes, incluyendo todos los bloques de código.
4. VS Code reconocerá automáticamente el formato Markdown y te mostrará una vista previa si pulsas `Ctrl+Shift+V`.

---

¿Quieres que te ayude a añadir una sección de “Contribución” o “Licencia” para dejarlo listo como proyecto público? También puedo ayudarte a generar una versión en inglés si lo vas a compartir internacionalmente.
