FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000
