import datetime as dt

from pydantic import BaseModel


class WebPageStateCreateSchema(BaseModel):
    tracking_id: int
    image_filename: str


class WebPageStateSchema(WebPageStateCreateSchema):
    id: int
    created_at: dt.datetime


class TrackingCreateSchema(BaseModel):
    url: str
    interval: dt.timedelta
    save_all_screenshots: bool


class TrackingSchema(BaseModel):
    id: int
    url: str
    interval: dt.timedelta
    created_at: dt.datetime
    save_all_screenshots: bool
    last_state: WebPageStateSchema | None
