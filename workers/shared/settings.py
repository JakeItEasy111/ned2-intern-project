import os

# Docker Compose sets REDIS_URL in each container's environment.
# "redis" is the service name in docker-compose.yml — Docker's
# internal DNS resolves it to the Redis container's IP.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# All stages write state under this prefix pattern:
#   job:{job_id}:{field}   e.g. job:abc123:status
def job_key(job_id: str, field: str) -> str:
    return f"job:{job_id}:{field}"