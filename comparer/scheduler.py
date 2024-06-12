from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler

from db.schemas import TrackingSchema

from .states import update_state, create_states_folder


class MyScheduler:
    def __init__(self):
        self._scheduler = BackgroundScheduler(
            {'apscheduler.job_defaults.max_instances': 10}
        )
        self._scheduler.start()

    def add_tracking(self, tr: TrackingSchema) -> Job:
        create_states_folder(tr)
        return self._scheduler.add_job(
            update_state,
            'interval',
            args=[tr],
            seconds=tr.interval.seconds,
            id=str(tr.id),
        )

    def remove_tracking_by_id(self, tr_id: int):
        self._scheduler.remove_job(str(tr_id))

    def get_all_jobs(self) -> list[Job]:
        return self._scheduler.get_jobs()
