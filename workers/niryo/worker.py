
from arq import ArqRedis
from arq.connections import RedisSettings
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable
from state import set_status, set_value
from settings import REDIS_URL
import uuid 
import asyncio

#---------
# STAGE 4
#---------

async def fake_niryo_worker(ctx, job):
    job_id = job.get("job_id", str(uuid.uuid4()))

    print('f"[{job_id}] moving robot...')
    await asyncio.sleep(5)
    print('f"[{job_id}] action complete. Sequence finished.')

    return {
        "status": "success",
        "job_id": job_id
    }

class WorkerSettings:
    functions = [fake_niryo_worker]  # list every job this worker handles
    queue_name = "niryo"

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1