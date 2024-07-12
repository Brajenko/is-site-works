from .engine import session_create
from .models import *
from .schemas import *


def tracking_model_to_schema(tr: Tracking) -> TrackingSchema:
    """
    Converts a Tracking model instance to a TrackingSchema.

    This function takes a Tracking model instance, retrieves its last state, and constructs
    a TrackingSchema instance with all the relevant fields from the Tracking model and its
    last state.

    Args:
        tr (Tracking): A Tracking model instance to be converted.

    Returns:
        TrackingSchema: A schema instance representing the tracking and its last state.
    """
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
    """
    Retrieves all tracking entries from the database and converts them to TrackingSchema.

    This function queries the database for all Tracking model instances, converts each to
    a TrackingSchema using `tracking_model_to_schema`, and returns a list of these schemas.

    Returns:
        list[TrackingSchema]: A list of TrackingSchema instances representing all trackings.
    """
    with session_create() as session:
        trackings = session.query(Tracking).all()
        return [tracking_model_to_schema(tracking) for tracking in trackings]


def get_tracking_by_id(id: int) -> TrackingSchema | None:
    """
    Retrieves a tracking entry by its ID and converts it to TrackingSchema.

    This function queries the database for a Tracking model instance by its ID. If found,
    it converts the model to a TrackingSchema and returns it. If not found, returns None.

    Args:
        id (int): The ID of the tracking entry to retrieve.

    Returns:
        TrackingSchema | None: A TrackingSchema instance if the tracking is found, otherwise None.
    """
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
    """
    Creates a new tracking entry in the database from a TrackingCreateSchema.

    This function takes a TrackingCreateSchema instance, creates a new Tracking model instance
    with the provided data, saves it to the database, and returns a TrackingSchema representation
    of the newly created tracking.

    Args:
        tr (TrackingCreateSchema): The schema containing the data for the new tracking.

    Returns:
        TrackingSchema: A schema instance representing the newly created tracking.
    """
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
    """
    Retrieves the most recent state of a given tracking entry.

    This function queries the database for the latest WebPageState associated with the specified
    Tracking object. It returns the most recent state based on the `created_at` timestamp. If no
    states are found for the given tracking, it returns None.

    Args:
        tr (Tracking): The tracking object for which to retrieve the last state.

    Returns:
        WebPageState | None: The most recent WebPageState object if available, otherwise None.
    """
    with session_create() as session:
        return (
            session.query(WebPageState)
            .filter(WebPageState.tracking_id == tr.id)
            .order_by(WebPageState.created_at.desc())
            .first()
        )


def delete_tracking_by_id(tr_id: int):
    """
    Deletes a tracking entry and its associated states from the database by its ID.

    This function deletes a Tracking object and all associated WebPageState objects from the
    database using the specified tracking ID. It commits the changes to the database.

    Args:
        tr_id (int): The ID of the tracking entry to be deleted.
    """
    with session_create() as session:
        session.query(Tracking).filter(Tracking.id == tr_id).delete()
        session.commit()
