
from arq import ArqRedis
from arq.connections import RedisSettings
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable
from state import set_status, set_value
from settings import REDIS_URL
import uuid 
import asyncio

#---------
# STAGE 3 
#---------

async def prusalink_job(ctx, job_id):

    print(f"[{job_id}] ordering print...")
    await asyncio.sleep(5)
    print(f"[{job_id}] print complete")

    redis = ctx["redis"]
    await redis.enqueue_job("niryo_robot_job", job_id, _queue_name="niryo")

    return {
        "status": "success",
        "job_id": job_id
    }

class WorkerSettings:
    functions = [fake_prusalink_worker]  # list every job this worker handles
    queue_name = "prusalink"

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1