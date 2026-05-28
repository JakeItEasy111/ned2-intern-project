from fastapi import FastAPI, BackgroundTasks, status
from models import CheckinPayload
from arq import create_pool
from arq.connections import RedisSettings
import os
from contextlib import asynccontextmanager
import uuid

app = None
arq_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_arq_pool()  # warm up connection
    yield

app = FastAPI(lifespan=lifespan)


async def get_arq_pool():
    global arq_pool
    if arq_pool is None:
        arq_pool = await create_pool(
            RedisSettings.from_dsn(
                os.getenv("REDIS_URL", "redis://redis:6379")
            )
        )
        return arq_pool

        
@app.get("/")
async def root():
    return {"message": "Hello World!"}


async def _enqueue_checkin_job(payload: CheckinPayload) -> None:

    pool = await get_arq_pool()

    job_id = str(uuid.uuid4())[:8]
    coin_text = f"{payload.first_name} {payload.last_name}"

    await set_status(pool, job_id, "queued")
    await set_value(pool, job_id, "coin_text", coin_text)

    await pool.enqueue_job("fake_cadquery_worker", job_id, coin_text)

    print(f"[stub] enqueue job: {payload.first_name} {payload.last_name} | badge={payload.badge_id}")

    return {"job_id":job_id, "status":"queued"}


@app.post("/checkin", status_code=status.HTTP_200_OK)
async def checkin(payload: CheckinPayload, background_tasks: BackgroundTasks):

    background_tasks.add_task(_enqueue_checkin_job, payload)

    return {"status": "received"}
