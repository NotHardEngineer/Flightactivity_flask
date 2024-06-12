from flask_apscheduler import APScheduler
from flask import current_app
import time

from src.parsing import save_tolmachevo_tables, parse_saved_tolmachevo_html


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
        save_tolmachevo_tables()
        parse_saved_tolmachevo_html()
        parse_saved_tolmachevo_html(name="page_tomorrow")
        current_app.logger.info("Automatic update finished in %s sec" % format(time.time() - start_time, '.2f'))

