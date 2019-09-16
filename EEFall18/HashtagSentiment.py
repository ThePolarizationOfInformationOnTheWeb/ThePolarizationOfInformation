import pandas as pd
import sys
from EEFall18.TweetFeatureExtractor import TweetFeatureExtractor


def main():
    if len(sys.argv) != 2:
        print("Usage: HashtagSentiment <topic>")

    try:
        open('{}_hashtag_sentiments.csv'.format(sys.argv[1]), 'r')
        print("File: {}_hashtag_sentiments.csv was found in cwd. Move or delete this file and rerun script. "
              "I don't want to overwrite hashtags that were already analyzed!".format(sys.argv[1]))
        sys.exit(0)
    except FileNotFoundError:
        print("Writing to file {}_hashtag_sentiments.csv".format(sys.argv[1]))

    feature_extractor = TweetFeatureExtractor(sys.argv[1])
    hashtag_df = pd.DataFrame(index=feature_extractor.get_hashtag_dataframe().columns,
                              columns=['left', 'right'])
    hashtag_df.index.name = 'hashtag'
    hashtag_df.to_csv('{}_hashtag_sentiments.csv'.format(sys.argv[1]))


if __name__ == '__main__':
    main()
