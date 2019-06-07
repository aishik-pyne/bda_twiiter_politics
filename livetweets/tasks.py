"""
Python module for computing page rank
"""
import sys
import os
from flashtext import KeywordProcessor
from pprint import pprint
from pyspark import SparkConf, SparkContext
# from livetweets.models import TweetDumps, TweetCountSummary
import json


class TweetAnalysis:

    def __init__(self):
        self.keyword_processor = KeywordProcessor(case_sensitive=True)
        keyword_dict = self.load_party_keywords()
        self.keyword_processor.add_keywords_from_dict(keyword_dict)

    @property
    def parties(self):
        return [os.path.splitext(p)[0] for p in
                os.listdir(os.path.join('data/keywords', 'parties'))]

    def load_party_keywords(self) -> dict:
        """Load a dict of keywords party wise

        :return: Dict of keywords {'party': [list of keywords], ...}
        :rtype: dict
        """
        keywords = {}
        for p in os.listdir(os.path.join('data/keywords', 'parties')):
            with open(os.path.join('data/keywords', 'parties', p)) as f:
                names = f.read().splitlines()
            keywords[os.path.splitext(p)[0]] = names
        return keywords

    def classify_text_to_party(self, text: str) -> list:
        """Classifies a text to the parties it belongs to

        :param text: Text str to classify
        :type text: str
        :return: List of parties names
        :rtype: list
        """
        return self.keyword_processor.extract_keywords(text)


# def get_count_summary(lines):
#     with SparkContext(conf=SparkConf(), appName='TweetCount') as sc:
#         tweet_jsons = sc.parallelize(lines).map(
#             lambda l: json.loads(l))

#         tweets = tweet_jsons.map(lambda t: (t['id'], t['text']))
#         tweet_party = tweets.map(lambda t: (
#             t[0], ta.classify_text_to_party(t[1])))
#         parties = tweet_party.flatMap(lambda t: [(p, 1) for p in t[1]])
#         summary = parties.reduceByKey(lambda n1, n2: n1 + n2).collect()
#         return summary

# @task
def process_pending_dumps_tweet_count():
    ta = TweetAnalysis()
    dumps = os.listdir('data/tweets')
    processed_dumps = os.listdir('data/summary')
    pending_dumps = [d for d in dumps if d not in processed_dumps]
    # Process tweets
    # pending_dumps = TweetDumps.objects.filter(status=TweetDumps.PENDING)
    # print(pending_dumps)
    with SparkContext(conf=SparkConf(), appName='TweetCount') as sc:
        for dump in pending_dumps:
            print(dump)
            with open(os.path.join('data/tweets/', dump), 'r') as f:
                lines = f.read().splitlines()
            try:
                tweet_jsons = sc.parallelize(lines).map(
                    lambda l: json.loads(l))
            except:
                print(dump)

            tweets = tweet_jsons.map(lambda t: (t['id'], t['text']))
            tweet_party = tweets.map(lambda t: (
                t[0], ta.classify_text_to_party(t[1])))
            parties = tweet_party.flatMap(lambda t: [(p, 1) for p in t[1]])
            summary = parties.reduceByKey(lambda n1, n2: n1 + n2).collect()

            with open(os.path.join('data/summary/', dump), 'w') as f:
                json.dump(summary, f)

            # for item in summary:
            #     TweetCountSummary(
            #         party=item[0], count=item[1], time=dump.time).save()
            # dump.status = TweetDumps.PROCESSED
            # dump.save()


if __name__ == "__main__":
    process_pending_dumps_tweet_count()
