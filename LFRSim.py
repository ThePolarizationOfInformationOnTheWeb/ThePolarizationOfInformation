import networkx as nx
import pandas as pd
import numpy as np


def build_and_write_tweets_df(n, tau1, tau2, mu, average_degree, min_community, htags_per_community, in_htag_prob,
                              out_htag_prob):

    nx_graph = nx.algorithms.community.community_generators.LFR_benchmark_graph(n, tau1, tau2, mu, average_degree,
                                                                                min_community=min_community)
    communities = {frozenset(nx_graph.nodes[v]['community']) for v in nx_graph}
    communities = [list(c) for c in list(communities)]

    print(communities)

    print('nx graph and communities made')

    tweets_df = pd.DataFrame(index=nx_graph.nodes, columns=['entities'])
    tweets_df.index.name = 'id'

    htag_list_by_community = {}
    for i in range(len(communities)):
        community_sent = 0.5 - np.random.rand(1)[0]
        htag_list_by_community[i] = ['h_{}_{}'.format(i*htags_per_community + j, community_sent)
                                     for j in range(htags_per_community)]

    hashtags_by_tweet = {}
    for tweet in nx_graph.nodes:
        hashtags_by_tweet[tweet] = []

    print('Calculating hashtag assignments')

    for i, cluster in enumerate(communities):
        print('community {} hashtags'.format(i))
        for htag in htag_list_by_community[i]:
            for tweet in nx_graph.nodes:
                if tweet in cluster:
                    if np.random.rand(1)[0] > 1 - in_htag_prob:
                        hashtags_by_tweet[tweet].append({'text': htag})
                else:
                    if np.random.rand(1)[0] > 1 - out_htag_prob:
                        hashtags_by_tweet[tweet].append({'text': htag})

    for tweet in nx_graph.nodes:
        tweets_df.loc[tweet, 'entities'] = str({'hashtags': hashtags_by_tweet[tweet]})

    print('Writing LFR_tweets.csv file')
    tweets_df.to_csv('LFR_tweets.csv')
