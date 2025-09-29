Got it, Francisco — here’s your updated `README.md` in full Markdown format, just like before, with all the new functionality and examples included. You can copy and paste this directly into your `README.md` file:

---

```markdown
# 🎬 Video Transcoder API

A distributed video transcoding system built with FastAPI, Redis, RQ, and Prometheus. Supports asynchronous job queuing and inline transcoding for small files, with full Docker orchestration.

---

## 🧱 Project Structure

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

---

## 🚀 Components

- **FastAPI**: REST API for uploading videos and checking job status.
- **Redis + RQ**: Job queue for asynchronous transcoding.
- **FFmpeg**: Performs the actual video transcoding.
- **Prometheus**: Collects metrics from the API.
- **Docker Compose**: Orchestrates all services.

---

## ⚙️ API Endpoints

### `POST /transcode`

Uploads a video and either:

- Returns the transcoded result immediately (if `inline=true` and the file is small), or
- Enqueues a transcoding job and returns a `job_id`.

**Form fields:**

- `file`: video file to transcode
- `codec`: video codec (default: `libx264`)
- `bitrate`: target bitrate (default: `1000k`)
- `resolution`: target resolution (default: `1280x720`)
- `inline`: optional boolean (`true` or `false`)

---

### `GET /status/{job_id}`

Returns the status of a transcoding job. If the job is finished and the output file exists, includes a `download_url` field.

**Example response:**

```json
{
  "status": "finished",
  "download_url": "http://localhost:8000/download/{job_id}"
}
```

---

### `GET /download/{job_id}`

Downloads the transcoded video file if the job is finished and the result exists.

---

## 🧪 Usage Examples

### 1. Standard transcoding (asynchronous)

```bash
curl -X POST http://localhost:8000/transcode \
  -F "file=@video.mp4" \
  -F "codec=libx264" \
  -F "bitrate=1000k" \
  -F "resolution=1280x720"
```

Then check status:

```bash
curl http://localhost:8000/status/{job_id}
```

And download when ready:

```bash
curl http://localhost:8000/download/{job_id} --output result.mp4
```

---

### 2. Inline transcoding (for small videos)

```bash
curl -X POST http://localhost:8000/transcode \
  -F "file=@small_video.mp4" \
  -F "codec=libx264" \
  -F "bitrate=800k" \
  -F "resolution=640x360" \
  -F "inline=true" --output result_inline.mp4
```

---

### 3. Inline requested but file too large (fallback to queue)

```bash
curl -X POST http://localhost:8000/transcode \
  -F "file=@large_video.mp4" \
  -F "codec=libx264" \
  -F "bitrate=2000k" \
  -F "resolution=1920x1080" \
  -F "inline=true"
```

Response will include `job_id` and status.

---

## 📈 Metrics

Prometheus metrics are exposed at `/metrics` and include:

- Total HTTP requests
- Request durations
- In-progress requests

Access Prometheus at [http://localhost:9090](http://localhost:9090)

