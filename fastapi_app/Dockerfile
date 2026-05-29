FROM python:3.11-slim

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
 
# Add /workers/shared to Python's search path so `from state import ...` works
# without any sys.path hacks inside the source files.
ENV PYTHONPATH="/workers/shared:${PYTHONPATH}"
 
# Unbuffered output means print() and logging statements appear in
# `docker compose logs api` immediately rather than being held in a buffer.
ENV PYTHONUNBUFFERED=1
 
# Document which port the app listens on (doesn't actually publish it —
# that's docker-compose's job with the `ports:` key).
EXPOSE 8000
 
# --host 0.0.0.0  → listen on all interfaces inside the container, not just
#                   127.0.0.1, so Docker's port forwarding can reach it.
# --workers 1     → single worker; ARQ connection pools aren't fork-safe so
#                   multiple workers would each need their own pool init.
# --log-level     → driven by the LOG_LEVEL env var set in docker-compose.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level ${LOG_LEVEL:-info}"]