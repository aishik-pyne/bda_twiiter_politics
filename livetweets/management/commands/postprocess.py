from django.core.management.base import BaseCommand
from django.conf import settings
from livetweets.models import TweetDumps, TweetCountSummary
import os
import json
# python manage.py seed --mode=refresh


class Command(BaseCommand):
    help = "Post Process Tweet Dumps"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting PostProcessing...')
            pending_dumps = TweetDumps.objects.filter(
                status=TweetDumps.PENDING)
            for dump in pending_dumps:
                if os.path.isfile(os.path.join(settings.SUMMARY_ROOT, dump.path)):
                    with open(os.path.join(settings.SUMMARY_ROOT, dump.path), 'r') as f:
                        summary = json.load(f)
                        for item in summary:
                            TweetCountSummary(
                                party=item[0],
                                count=item[1],
                                time=dump.time
                            ).save()
                    dump.status = TweetDumps.PROCESSED
                    dump.save()
        finally:
            self.stdout.write('Ending PostProcessing...')
