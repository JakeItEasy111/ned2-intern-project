# FastAPI Service

Receives Google Form check-in submissions and (eventually) enqueues jobs to Redis for the worker pipeline.

## Setup

```bash
cd fastapi_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd fastapi_app
source .venv/bin/activate
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`.

## Endpoints

### `POST /checkin`

Receives a guest check-in payload, returns 200 immediately, and runs the Redis enqueue as a background task.

**Request body:**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "badge_id": "B-001"
}
```

**Response:**

```json
{"status": "received"}
```

Extra fields (e.g. organization, reason for visit) are silently ignored.

## Test with curl

```bash
curl -s -X POST http://127.0.0.1:8000/checkin \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Doe","email":"jane@example.com","badge_id":"B-001"}'
```

## Notes

- The Redis enqueue in `main.py` is currently a print stub. Once the job schema is agreed, I will replace `_enqueue_checkin_job` with the real `rpush` call.
- ngrok is used as a public tunnel so Google Apps Script can reach the local server. The ngrok URL changes on every restart and must be updated in `apps_script/Code.gs`.
