
from arq import ArqRedis
from arq.connections import RedisSettings
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable
from state import set_status, set_value
from settings import REDIS_URL
import uuid 
import asyncio

async def fake_cad_worker(ctx, job):
    job_id = job.get("job_id", str(uuid.uuid4()))

    print('f"[{job_id}] generating CAD...')
    await asyncio.sleep(5)
    print('f"[{job_id}] CAD complete')

    return {
        "status": "success",
        "job_id": job_id
    }

class WorkerSettings:
    functions = [fake_cad_worker]  # list every job this worker handles

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1