import datetime as dt

from sqlalchemy.orm import Session
from sqlalchemy import update

from .engine import session_create
from .models import *
from .schemas import *


def tracking_model_to_schema(tr: Tracking) -> TrackingSchema:
    last_state = get_last_state(tr)
    return TrackingSchema(
        id=tr.id,
        url=tr.url,
        interval=tr.interval,
        created_at=tr.created_at,
        save_all_screenshots=tr.save_all_screenshots,
        last_state=(
            WebPageStateSchema(
                id=last_state.id,
                tracking_id=last_state.tracking_id,
                image_filename=last_state.image_filename,
                created_at=last_state.created_at,
            )
            if last_state
            else None
        ),
    )


def get_all_trackings() -> list[TrackingSchema]:
    with session_create() as session:
        trackings = session.query(Tracking).all()
        return [tracking_model_to_schema(tracking) for tracking in trackings]


def get_tracking_by_id(id: int) -> TrackingSchema | None:
    with session_create() as session:
        tracking = session.query(Tracking).get(id)
        return tracking_model_to_schema(tracking) if tracking else None


def create_new_tracking(tr: TrackingCreateSchema) -> TrackingSchema:
    with session_create() as session:
        db_tracking = Tracking(
            url=tr.url,
            interval=tr.interval,
            save_all_screenshots=tr.save_all_screenshots,
        )
        session.add(db_tracking)
        session.commit()
        return tracking_model_to_schema(db_tracking)


def create_new_website_state(
    state: WebPageStateCreateSchema,
) -> WebPageStateSchema:
    with session_create() as session:
        tracking = session.query(Tracking).get(state.tracking_id)
        db_state = WebPageState(
            tracking=tracking,
            image_filename=state.image_filename,
        )
        session.add(db_state)
        session.commit()
        return WebPageStateSchema(
            id=db_state.id,
            tracking_id=db_state.tracking_id,
            image_filename=db_state.image_filename,
            created_at=db_state.created_at,
        )


def get_last_state(tr: Tracking) -> WebPageState | None:
    with session_create() as session:
        return (
            session.query(WebPageState)
            .filter(WebPageState.tracking_id == tr.id)
            .order_by(WebPageState.created_at.desc())
            .first()
        )


def delete_tracking_by_id(tr_id: int):
    with session_create() as session:
        session.query(Tracking).filter(Tracking.id == tr_id).delete()
        session.commit()
