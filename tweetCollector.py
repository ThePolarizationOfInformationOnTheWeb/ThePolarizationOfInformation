#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 02:57:04 2018

@author: charlesdickens

description: This file contains scripts to collect tweet and twitter user data
             related to a specified topic. Methods included will access the 
             twitter API and then store data in a MySQL db.
    
             The tweet table will its primary key be simply an index
             (... id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id))
             then columns such as the tweet content, who tweeted it 
             (screen name), retweet information, and more...
             
             The user table will have its primary key be the user screen name
             (...screenName VARCHAR(50) NOT NULL, PRIMARY KEY(screenName))
             then columns such as the user's friends, user's followers, and more
"""


