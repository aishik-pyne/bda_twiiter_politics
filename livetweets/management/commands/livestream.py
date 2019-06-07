import requests
import pandas as pd
from pprint import pprint
from io import BytesIO
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.conf import settings
from livetweets.stream import TwitterStreamer, get_keywords
# python manage.py seed --mode=refresh


class Command(BaseCommand):
    help = "Start parsing live tweets"

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting Live Stream...')
            track_keywords = get_keywords(settings.KEYWORDS_ROOT)
            twitter_streamer = TwitterStreamer()
            twitter_streamer.stream_tweets(track_keywords)
        finally:
            self.stdout.write('Ending Live Stream...')
