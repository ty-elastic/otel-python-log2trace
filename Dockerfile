FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY src/*.py ./
COPY data/trace.csv ./

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "file_tracing_via_api.py"]