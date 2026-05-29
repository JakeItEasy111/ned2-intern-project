FROM python:3.11-slim

WORKDIR /workers/niryo

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 