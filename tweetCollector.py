#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 02:57:04 2018

@author: charlesdickens

description: This file contains scripts to collect tweet and twitter user data
             related to a specified topic.
"""

tweets = []
with open('progressivetweets.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        tweets.append(row)
