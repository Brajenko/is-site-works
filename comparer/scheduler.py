from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler

from db.schemas import TrackingSchema

from .states import update_state, create_states_folder


class MyScheduler:
    """
    A scheduler class for managing tracking updates.

    This class encapsulates the functionality of a background scheduler to manage tracking
    updates at specified intervals. It allows adding, removing, and listing tracking jobs,
    which are operations to update tracking states at predefined intervals.

    Attributes:
        _scheduler (BackgroundScheduler): An instance of APScheduler's BackgroundScheduler
                                          used for scheduling tracking updates.

    Methods:
        __init__(self): Initializes a new MyScheduler instance with a BackgroundScheduler.
        add_tracking(self, tr: TrackingSchema) -> Job: Adds a new tracking job to the scheduler.
        remove_tracking_by_id(self, tr_id: int): Removes a tracking job from the scheduler by its ID.
        get_all_jobs(self) -> list[Job]: Returns a list of all scheduled tracking jobs.
    """
    def __init__(self):
        """
        Initializes the MyScheduler instance.

        Creates a BackgroundScheduler with a specific configuration that limits the maximum
        number of instances of each job to 10. It starts the scheduler immediately upon
        initialization.
        """
        self._scheduler = BackgroundScheduler(
            {'apscheduler.job_defaults.max_instances': 10}
        )
        self._scheduler.start()

    def add_tracking(self, tr: TrackingSchema) -> Job:
        """
        Adds a new tracking job to the scheduler.

        This method schedules a new job to update the state of a tracking entry at the interval
        specified in the TrackingSchema. It also ensures that the necessary folder structure
        for storing state information is created before scheduling the job.

        Args:
            tr (TrackingSchema): The tracking entry to be updated by the scheduled job.

        Returns:
            Job: The job instance that was added to the scheduler.
        """
        create_states_folder(tr)
        return self._scheduler.add_job(
            update_state,
            'interval',
            args=[tr],
            seconds=tr.interval.seconds,
            id=str(tr.id),
        )

    def remove_tracking_by_id(self, tr_id: int):
        """
        Removes a tracking job from the scheduler by its ID.

        This method removes a previously scheduled tracking job using its ID. The ID corresponds
        to the tracking entry's ID.

        Args:
            tr_id (int): The ID of the tracking job to be removed.
        """
        self._scheduler.remove_job(str(tr_id))

    def get_all_jobs(self) -> list[Job]:
        """
        Returns a list of all scheduled tracking jobs.

        This method retrieves all jobs currently scheduled in the BackgroundScheduler and returns
        them as a list.

        Returns:
            list[Job]: A list of all jobs currently scheduled in the scheduler.
        """
        return self._scheduler.get_jobs()
