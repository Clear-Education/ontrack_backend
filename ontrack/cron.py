# import os
from django.core import management

# from django.conf import settings
from django_cron import CronJobBase, Schedule


class Backup(CronJobBase):
    RUN_AT_TIMES = ["6:00"]
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = "my_app.Backup"

    def do(self):
        management.call_command("dbbackup")
        management.call_command("mediabackup", clean=True)
