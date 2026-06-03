
from arq import ArqRedis
from arq.connections import RedisSettings
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable
from state import set_status, set_value
from settings import REDIS_URL
import uuid 
import asyncio

#---------
# STAGE 2 
#---------

async def fake_slicer_worker(ctx, job_id):

    print(f"[{job_id}] slicing STL...")
    await asyncio.sleep(5)
    print(f"[{job_id}] slice complete")

    new_job_id = str(uuid.uuid4())[:8]

    redis = ctx["redis"]
    await redis.enqueue_job("fake_prusalink_worker", new_job_id, _queue_name="prusalink")

    return {
        "status": "success",
        "job_id": job_id
    }

class WorkerSettings:
    functions = [fake_slicer_worker]  # list every job this worker handles
    queue_name = "slicer"

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1