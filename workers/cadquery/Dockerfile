FROM python:3.11-slim

WORKDIR /workers/cadquery

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

# Add /app/shared to Python's search path so `from state import ...` works
# without any sys.path hacks inside the source files.
ENV PYTHONPATH="/workers/shared:${PYTHONPATH}"