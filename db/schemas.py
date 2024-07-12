import datetime as dt

from pydantic import BaseModel


class WebPageStateCreateSchema(BaseModel):
    """
    Schema for creating a new webpage state entry.

    Attributes:
        tracking_id (int): The ID of the tracking entry associated with this state.
        image_filename (str): The filename of the screenshot representing this state.
    """
    tracking_id: int
    image_filename: str


class WebPageStateSchema(WebPageStateCreateSchema):
    """
    Schema for representing a webpage state, extending the create schema with additional fields.

    Inherits:
        WebPageStateCreateSchema: The base schema for creating a webpage state.

    Attributes:
        id (int): The unique identifier for this webpage state.
        created_at (dt.datetime): The timestamp when this state was created.
    """
    id: int
    created_at: dt.datetime


class TrackingCreateSchema(BaseModel):
    """
    Schema for creating a new tracking entry.

    Attributes:
        url (str): The URL of the webpage to track.
        interval (dt.timedelta): The interval at which to check the webpage for changes.
        save_all_screenshots (bool): Whether to save screenshots for all checks or only when changes are detected.
    """

    url: str
    interval: dt.timedelta
    save_all_screenshots: bool


class TrackingSchema(BaseModel):
    """
    Schema for representing a tracking entry, extending the create schema with additional fields.

    Inherits:
        TrackingCreateSchema: The base schema for creating a tracking entry.

    Attributes:
        id (int): The unique identifier for this tracking entry.
        url (str): The URL of the webpage being tracked.
        interval (dt.timedelta): The interval at which the webpage is checked for changes.
        created_at (dt.datetime): The timestamp when this tracking entry was created.
        save_all_screenshots (bool): Whether to save screenshots for all checks or only when changes are detected.
        last_state (WebPageStateSchema | None): The last recorded state of the webpage, or None if no states have been recorded.
    """
    id: int
    url: str
    interval: dt.timedelta
    created_at: dt.datetime
    save_all_screenshots: bool
    last_state: WebPageStateSchema | None
