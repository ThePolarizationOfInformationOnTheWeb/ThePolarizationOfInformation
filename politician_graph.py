import pandas as pd
import json

df = pd.read_csv("~/Downloads/pol_tweets.csv", sep=";")
hashtags = df['hashtag_entities']
pols = df['user_id']
hashtag_list = {}
length = hashtags.shape[0]
for index, currentpol in pols.iteritems():
    if currentpol not in hashtag_list:
        hashtag_list[currentpol] = []
    hashtag = hashtags.iloc[index]
    hashtag = hashtag.replace("{", "")
    hashtag = hashtag.replace("}", "")
    hashtagls = hashtag.split(",")
    currentpolhashtags = hashtag_list[currentpol]
    for h in hashtagls:
        if h not in currentpolhashtags:
            currentpolhashtags.append(h)
    hashtag_list[currentpol] = currentpolhashtags

with open('tweetdict.json', 'w') as f:
    json.dump(hashtag_list, f)
