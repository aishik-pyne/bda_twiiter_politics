import os
import re
from datetime import datetime
from django_cron import CronJobBase, Schedule
from django.conf import settings
from livetweets.models import TweetDumps


class TweetDumpCheck(CronJobBase):
    RUN_EVERY_MINS = 1  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'livetweets.TweetDumpCheck'    # a unique code

    def do(self):
        dumps = os.listdir(settings.TWEETS_ROOT)
        for d in dumps:
            try:
                if TweetDumps.objects.filter(path=d).count():
                    continue
                dump_time = re.search(r'tweets-(.*).txt', d).group(1)
                dump_time = datetime.strptime(
                    dump_time, "%Y-%m-%d:%H:%M:%S%z")
                new_dump = TweetDumps(
                    path=d, time=dump_time, status=TweetDumps.PENDING)
                new_dump.save()
                print(new_dump)
            except Exception as exp:
                print(exp)
