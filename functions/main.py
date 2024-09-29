# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import flask
from firebase_functions import https_fn, scheduler_fn

from cronjobs.cronjobs import StatsCronjob, GoogleCalendarsCronjob

# initialize_app()
app = flask.Flask(__name__)


@https_fn.on_request()
def on_request_exampl(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")


@https_fn.on_request()
def on_request_run_stats(req: https_fn.Request) -> https_fn.Response:
    stats_cronjob = StatsCronjob()
    stats_cronjob.run_stats_periodically()
    return https_fn.Response("Finished run stats!")


@https_fn.on_request()
def on_request_update_google_calendars(req: https_fn.Request) -> https_fn.Response:
    calendar_cronjob = GoogleCalendarsCronjob()
    calendar_cronjob.update_calendars_daily()
    return https_fn.Response("Finished updating google calendars!")


@scheduler_fn.on_schedule(schedule="0 9 * * *")
def run_strava_stats(event):
    stats_cronjob = StatsCronjob()
    stats_cronjob.run_stats_periodically()


@scheduler_fn.on_schedule(schedule="0 12 * * *")
def create_google_calendar_events(event):
    calendar_cronjob = GoogleCalendarsCronjob()
    calendar_cronjob.update_calendars_daily()


