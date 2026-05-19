from fastapi import FastAPI, BackgroundTasks, status
from models import CheckinPayload

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


def _enqueue_checkin_job(payload: CheckinPayload) -> None:
    # TODO: replace with Redis rpush once job schema agreed with Jacob
    print(f"[stub] enqueue job: {payload.first_name} {payload.last_name} | badge={payload.badge_id}")


@app.post("/checkin", status_code=status.HTTP_200_OK)
async def checkin(payload: CheckinPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(_enqueue_checkin_job, payload)
    return {"status": "received"}
