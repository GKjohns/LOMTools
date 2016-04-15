import requests
import re

def get_format_tweets(url):
    html = requests.get(url).text
    tweet_ids = re.findall('twitter.com/.*/statuses/(\d+)', html) + \
                re.findall('twitter.com/.*/status/(\d+)', html)

    # formats the tweets correctly
    return ['[tweetbegin {} tweetend]'.format(id) for id in tweet_ids]
