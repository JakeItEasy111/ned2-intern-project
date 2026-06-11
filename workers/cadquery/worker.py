
from arq import ArqRedis
from arq.connections import RedisSettings
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable
from state import set_status, set_value
from settings import REDIS_URL
import uuid 
import asyncio
import cadquery as cq 
from cadquery import exporters

#---------
# STAGE 1 
#---------

async def cad_job(ctx, job_id, coin_text):

    print(f"[{job_id}] Generating CAD with text '{coin_text}'...")
    coin = cq.Workplane("XY").circle(30).extrude(5).faces(">Z").workplane().text(coin_text, fontsize=3, distance=1).extrude(1)
    
    exporters.export(
        coin,
        f"/models/{job_id}.stl",
        exporters.ExportTypes.STL, 
        tolerance=0.001, 
        angularTolerance=0.1, 
        ascii=False
    )
    print(f"[{job_id}] CAD saved to /models/{job_id}.stl")

    redis = ctx["redis"]
    await redis.enqueue_job("slicer_job", job_id, _queue_name="slicer")

    return {
        "status": "success",
        "job_id": job_id,
        "coin_text": coin_text
    }


class WorkerSettings:
    functions = [cad_job]  # list every job this worker handles
    queue_name = "cadquery"

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1