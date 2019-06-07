from django.conf import settings
import tweepy
import configparser
import os
import json
from datetime import datetime, timezone, timedelta
import pytz
from pprint import pprint
from colored import fg, bg, attr
from livetweets.tasks import process_pending_dumps_tweet_count

config = configparser.ConfigParser()
config.read('config.ini')


class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.auth = tweepy.OAuthHandler(
            settings.TWITTER_CREDS['API_KEY'], settings.TWITTER_CREDS['API_SECRET_KEY'])
        self.auth.set_access_token(
            settings.TWITTER_CREDS['ACCESS_TOKEN'], settings.TWITTER_CREDS['ACCESS_TOKEN_SECRET'])
        self.tweets_folder = settings.TWEETS_ROOT

    def stream_tweets(self, track_keywords):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = FileWriterListener(self.tweets_folder)

        stream = tweepy.Stream(self.auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=track_keywords)


class FileWriterListener(tweepy.streaming.StreamListener):
    """
    A stream listener which dumps tweets to a file with hourly buckets 
    """

    def __init__(self, dump_folder_path):
        if os.path.isdir(dump_folder_path):
            self.dump_folder_path = dump_folder_path
        else:
            raise NotADirectoryError(
                "{} is not a directory".format(dump_folder_path))

        self.last_filename = None

    def get_filename(self, created_at: str):
        """
        Returns the file name to store the tweet based on the hour
        """
        created_at = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        created_at = created_at - timedelta(minutes=created_at.minute % 15,
                                            seconds=created_at.second,
                                            microseconds=created_at.microsecond)
        created_at = created_at.replace(tzinfo=timezone.utc).astimezone(
            tz=pytz.timezone('Asia/Calcutta'))
        filename = "tweets-{}.txt".format(
            datetime.strftime(created_at, "%Y-%m-%d:%H:%M:00%z"))
        if filename != self.last_filename:
            self.last_filename = filename
            process_pending_dumps_tweet_count()
        return os.path.join(self.dump_folder_path, filename)

    def on_data(self, data):
        """
        Write tweet to file when it arrives
        """
        try:
            json_data = json.loads(data)
            filename = self.get_filename(json_data["created_at"])
            with open(filename, 'a') as tf:
                tf.write(data)
                print("{}{}Tweet dumped{} {}".format(bg('green'), fg('black'),
                                                     attr('reset'), json_data['text'][:100]))
        except BaseException as e:
            print("{} Error on_data{} {}".format(
                bg('red'), attr('reset'), str(e)))
        return True

    def on_error(self, status):
        print("Error occoured!!!", status)


def get_keywords(keywords_folder):
    keywords = []
    # Parties
    for p in os.listdir(os.path.join(keywords_folder, 'parties')):
        with open(os.path.join(keywords_folder, 'parties', p)) as f:
            names = f.read().splitlines()
            keywords.extend(names)

    # General
    with open(os.path.join(keywords_folder, 'general.txt')) as f:
        names = f.read().splitlines()
        keywords.extend(names)

    return keywords
