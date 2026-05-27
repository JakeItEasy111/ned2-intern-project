from arq import ArqRedis
from .settings import job_key

# called at the start of each stage
async def set_status(redis: ArqRedis, job_id: str, status: str):
    # ex=86400 means the key expires after 24 hours automatically
    await redis.set(job_key(job_id, "status"), status, ex=86400)

async def set_value(redis: ArqRedis, job_id: str, field: str, value: str):
    await redis.set(job_key(job_id, field), value, ex=86400)

async def get_value(redis: ArqRedis, job_id: str, field: str) -> str:
    val = await redis.get(job_key(job_id, field))
    # Redis returns bytes; decode to str
    return val.decode() if val else None