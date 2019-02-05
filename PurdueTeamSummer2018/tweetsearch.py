import twitter
import sys
import json
import re
import urllib2

def search(query, count = 10):
    with open("./consumer_key.txt", "r") as consumer_key_f:
        for line in consumer_key_f:
            consumer_key2 = line.rstrip()

    with open("./consumer_secret.txt", "r") as consumer_secret_f:
        for line in consumer_secret_f:
            consumer_secret2 = line.rstrip()

    with open("./access_key.txt", "r") as access_key_f:
        for line in access_key_f:
            access_key2 = line.rstrip()

    with open("./access_secret.txt", "r") as access_secret_f:
        for line in access_secret_f:
            access_secret2 = line.rstrip()

    api = twitter.Api(consumer_key=consumer_key2, consumer_secret=consumer_secret2, access_token_key=access_key2,
                      access_token_secret=access_secret2)

#    results = api.GetSearch(raw_query='q=' + str(sys.argv[1]) + '&count=' + str(sys.argv[2]))
    results = api.GetSearch(raw_query='q=' + str(query) + '&count=' + str(count))

    jresults = []
    
    for result in results:
        jresults.append(result._json)

    return jresults

def get_user_ids_of_post_likes(post_id):
    try:
        json_data = urllib2.urlopen('https://twitter.com/i/activity/favorited_popup?id=' + str(post_id)).read()
        found_ids = re.findall(r'data-user-id=\\"+\d+', json_data)
        unique_ids = list(set([re.findall(r'\d+', match)[0] for match in found_ids]))
        return unique_ids
    except urllib2.HTTPError:
        return False
        
#if __name__ == "__main__":
#    main()
