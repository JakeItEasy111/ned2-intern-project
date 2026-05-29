from fastapi import FastAPI, BackgroundTasks, status
from models import CheckinPayload
from arq_queue import get_arq_pool, close_arq_pool
from contextlib import asynccontextmanager
from state import set_status, set_value
import uuid
import logging


app = None
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to redis")
    await get_arq_pool()  # warm up connection
    logger.info("Redis connection ready.")
    yield
    await close_arq_pool()
    logger.info("Redis connection closed.")


app = FastAPI(lifespan=lifespan)


@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    status = await get_value(redis, job_id, "status")
    return {"job_id": job_id, "status": status}


async def _enqueue_checkin_job(payload: CheckinPayload) -> None:

    pool = await get_arq_pool()

    job_id = str(uuid.uuid4())[:8]
    coin_text = f"{payload.first_name} {payload.last_name}"

    await set_status(pool, job_id, "queued")
    await set_value(pool, job_id, "email",      payload.email)
    await set_value(pool, job_id, "first_name", payload.first_name)
    await set_value(pool, job_id, "last_name",  payload.last_name)
    await set_value(pool, job_id, "badge_id",   payload.badge_id)

    try:
        await pool.enqueue_job("fake_cadquery_worker", job_id, coin_text, _queue_name="cadquery")
    except Exception:
        logger.info("Failed to enqueue generate_model job.")
        return {"job_id":job_id, "status":"failed"}
    
    logger.info("Enqueued generate_model job %s for %s", job_id, payload.email)
    return {"job_id":job_id, "status":"queued"}


@app.post("/checkin", status_code=status.HTTP_200_OK)
async def checkin(payload: CheckinPayload, background_tasks: BackgroundTasks):

    background_tasks.add_task(_enqueue_checkin_job, payload)

    return {"status": "received"}
