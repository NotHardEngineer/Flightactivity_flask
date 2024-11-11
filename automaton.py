from flask_apscheduler import APScheduler
from flask import current_app
import time

from src.parsing import update_all


scheduler = APScheduler()


def test_job():
    print("I run every so often...")


@scheduler.task(
    "interval",
    id="update_db",
    hours=1,
    max_instances=1,
)
def update_db():
    with scheduler.app.app_context():
        start_time = time.time()
        current_app.logger.info("Automatic update started")
        update_all()
        current_app.logger.info("Automatic update finished in %s sec" % format(time.time() - start_time, '.2f'))

