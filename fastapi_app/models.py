from pydantic import BaseModel, ConfigDict


class CheckinPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    first_name: str
    last_name: str
    email: str
    badge_id: str
