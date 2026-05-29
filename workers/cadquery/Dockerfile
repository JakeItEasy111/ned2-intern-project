FROM python:3.11-slim

WORKDIR /workers/cadquery

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 