#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 10:56:14 2017

@author: charlesdickens

file:        newsCrawler.py

description: This script contains methods used to crawl the the web and obtain 
             information from news artcles covering a specified topic. This 
             crawler will read and collect data from article at a 
             news.google.com search result page, a standard google search, and 
             tweets. 
             The Data will be stored in tables for each domain in a mysql 
             database. Tables will hold information such as article headline, 
             text, referrences, image urls, tweets, and ...
             
             In tweetSearch (currently line 310) : add your twitter account 
             OAuth tokens for acces to the twitter API. This can be easily obtained 
             if you have a twitter account.

             In crawlByTopic(topic) searches the topic string in google news, google search(ToDo), 
             and twiiter's api and begins following the articles and creating or updating tables in 
             existing mysql database.
"""

from bs4 import BeautifulSoup #html parsing tool#
import re
from twitter import Twitter
from twitter import OAuth
import subprocess 
import copy
import datetime
from MySqlNewsCrawler import MySqlConn

"""
function:    crawlByTopic

parameters:  topic:           String describing topic of interest. 
                              Used for google news search.
description: crawlByTopic searches the topic string in google news, google 
             search, and twiiter's api and begins following the articles and 
             creating or updating tables in existing mysql database.     
"""
def crawlByTopic(topic):
    #setup connection to mySQL server
    sqlConn = MySqlConn()

    try:
        #USE database for topic
        sqlConn.mySqlDatabase(topic)
        
        #retreive dictionary of all domain tables and headlines already 
        #existing in database
        domains, tweets = sqlConn.retrieveDomains()
        
        #scrape google news for articles
        numArticles = googleNewsSearch(topic, domains, sqlConn)
        
        #perform a google search from the google home page
        numArticles = numArticles + googleSearch(topic, domains, sqlConn)
        
        #find tweets 
        numArticles = numArticles + tweetSearch(topic, domains, tweets, sqlConn)
    
        print str(numArticles) + " Added"
        
    
    finally:
        del sqlConn

"""
function:    googleNewsSearch 
parameters:  topic:          String describing topic of interest. 
                             Used for google news search.
             domains:        dict of key: domain values: list of headlines 
             sqlConn:        the mySql database connection

description: google news searches the topic string in google news and begins 
             following articles posted on the google news search result page 
             beginning with the 1st or top article and ending with the
             numArticles'st page down, or until all article on google's 
             search results are exhausted.
"""
def googleNewsSearch(topic, domains, sqlConn):
    numAdded = 0
    
    #build google news search url
    topics = topic.split()
    googleNewsSearch = "https://news.google.com/news/search/section/q/" 
    for t in topics:
        googleNewsSearch = googleNewsSearch + t + "%20"
    googleNewsSearch = googleNewsSearch[0:-3]
    googleNewsSearch = googleNewsSearch + '/'
    for t in topics:
        googleNewsSearch = googleNewsSearch + t + "%20"
    googleNewsSearch = googleNewsSearch[0:-3]
    googleNewsSearch = googleNewsSearch + '?hl=en&ned=us'
    
    
    #retrieve html from google news search result page#
    p = subprocess.Popen(['curl','-L', googleNewsSearch], stdout = subprocess.PIPE).communicate()
    searchPageSource = p[0]
    
    #beautiful soup object to parse html#
    bsObj = BeautifulSoup(searchPageSource, "html.parser") 
    
    #articles is a dictionary with key: domain name value: list of (headline,url)
    articles = retrieveGoogleNewsResults(bsObj)
    
    #find full coverage link if there is one
    firstBlock = bsObj.find("c-wiz",{"class":"lPV2Xe k3Pzib"})
    fullCoverage = firstBlock.find("a", {"class":"FKF6mc TpQm9d"})
    if fullCoverage != None:
        fullCoverageLink = fullCoverage.attrs['href']
        fullCoverageLink = "https://news.google.com/news/" + fullCoverageLink
        #follow full coverage link
        p = subprocess.Popen(['curl','-L', googleNewsSearch], stdout = subprocess.PIPE).communicate()
        searchPageSource = p[0]
    
        #beautiful soup object to parse html#
        bsObj = BeautifulSoup(searchPageSource, "html.parser")
        
        #articlesTwo is a dictionary with key: domain name value: list of (headline,url)
        articlesTwo = retrieveGoogleNewsResults(bsObj)
        
        #combine articlesTwo and articles
        for dom,t in articlesTwo.items():
            if dom in articles:
                articles[dom] = articles[dom] + t
            else:
                articles[dom] = t
          
        for a in articles:
            articles[a] = list(set(articles[a]))
        
        #get rid of twitter from list of domains
        articles.pop("twitter",None)
    
#    for dom in articles:
#        print dom + ": " 
#        print articles[dom] 
#        print "\n"
#    print "\n \n .................................................\n \n"
    
    #create table for domains without table yet and remove articles already 
    #in database from articles dictionary
    for dom in articles:
        if dom not in domains:
            sqlConn.createTable(dom)
        else:
            for head in domains[dom]:
                articles[dom] = [(h,u,d) for h,u,d in articles[dom] if h != head]
                
    articles = {x:articles[x] for x in articles if len(articles[x]) !=0}
#    print articles
        
    #add to domains table headline text, and url
    for dom in articles:
        for h,url,date in articles[dom]:
            content = retrieveArticleText(url, topic)
            #content length is 0 if site requires login or perhaps all text was 
            #determined to be "unrelated"
            if len(content) != 0:
                sqlConn.addToTable(dom, h, url, content, date)
                numAdded = numAdded + 1
            
    return numAdded

"""
function:    retreiveSearchResults

parameters:  bsObj:  The beautiful soup object of the google news search result
                     page source code.

description: Given the html beautiful soup object of the search result page
             this function will return a dictionary object of domain names and
             corresponding headlines and links tuples.
"""   
def retrieveGoogleNewsResults(bsObj):
    articles = {}
    
    for c in bsObj.findAll("c-wiz", {"class":"M1Uqc"}):
        try:
            #format domain name for sql
            domain = c.find("span", {"class":"IH8C7b Pc0Wt"})
            domain = re.sub(r"\s", "", domain.contents[0].lower())
            domain = re.sub(r"\..*$", "", domain)
            domain = re.sub(r"\/","", domain)
            domain = re.sub(r"\-","", domain)
            domain = re.sub("&","", domain)
            domain = re.sub("!","",domain)
            domain = re.sub("\(\w*\)","",domain)
            
            #grab headline from html
            headline = c.find("a", {"class":"nuEeue hzdq5d ME7ew", "role":"heading"})
            
            #grab date from html
            datehtml = c.find("span", {"class":"d5kXP YBZVLb"})
            
            today = re.compile("\d{1,}(m|h) ago$")
            now = datetime.datetime.now()
            
            #check date format
            if re.match(today, datehtml.contents[0]):
                #article posted today
                #format date string
                date = now.strftime("%Y-%m-%d")
                    
            else:
                #article posted days ago
                #format date string
                #grab year from contents
                year = int(re.findall("\d{4}$",datehtml.contents[0])[0])
                
                #grab day from contents
                day = int(re.findall("\d{2}",datehtml.contents[0])[0])
                
                #grab month
                m = re.findall("\D{3}",datehtml.contents[0])[0]
                month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(m) + 1
                
                date = str(year) + '-' + str(month) + '-' + str(day)
            
            #check if domain already exists in database
            if domain in articles:
                #append if domain exists
                articles[domain].append((headline.contents[0],headline.attrs['href'],date))
            else:
                #create new key in articles dictionary
                articles[domain] = [(headline.contents[0],headline.attrs['href'],date)]
        except KeyError as err:
            print err
    
    return articles


"""
function:    retrieveArticleText

parameters:  URL:    The url of the article to be read.
             topic:  The topic we are searching

description: Given the url and topic of a article retrieveArticleText will
             return relevent text from the article.
return:      finalText: the relevant article text.
"""
def retrieveArticleText(url, topic):    
    i = 0
    topicFlag = True
    texts = []
    p = []
    topics = topic.split()
    finalText = ""
    
    #retrieve html from article
    p = subprocess.Popen(['curl','-L', url], stdout = subprocess.PIPE).communicate()
    pageSource = p[0]
    
    bsObj = BeautifulSoup(pageSource, "html.parser")
    
    p = bsObj.findAll("p") #list of all p tags in the page HTML
    
    while len(p) > 0:
        #save sets of p texts together
        texts.append(p[0].get_text()) 
        
        for sib in p[0].find_next_siblings("p"):
            #find all siblings of the p tag text together and remove from p list#
            texts[i] = texts[i] + " " + sib.get_text()
            if sib in p:
                p.remove(sib)
        del p[0] #update p list#
        i = i + 1
    
    while len(texts) > 0:
        #print texts[0] + "\n"
        #for each text text group #
        for s in topics:
            #check if the topic is in the text#
            if s.lower() not in texts[0].lower():
                #print s.lower() + " not in : \n" + texts[0].lower() 
                topicFlag = False
        
        if topicFlag == False:
            #if topic not in text then tet is unrelated and should be removed#
            del texts[0]
        
        else:
            #add to final text if topic is in text#
            finalText = finalText + " " + texts[0]
            del texts[0]
        
        topicFlag = True
    
    return finalText

"""
function:    tweetSearch 
parameters:  topic:          String describing topic of interest. 
                             Used for google search.
             domains:        dict of domain names in sql database 
             tweets:         dict of screen name and tweets related to topic 
             sqlConn:        the mySql database connection
description: tweetSearch finds and stores tweets related to topic in sql
"""
def tweetSearch(topic, domains, tweets, sqlConn):
    #setup connection to twitter API
    t = Twitter(auth=OAuth("",
                           "",
                           "",
                           ""))
        
    RelatedTweets = t.search.tweets(q = topic, count = 100, result_type = "popular")
    
    tempTweets = copy.deepcopy(tweets)
    
    if "Twitter" not in domains:
        sqlConn.createTwitterTable()
        
    #add all twitter usernames to tempTweets dict
    for tw in RelatedTweets["statuses"]:
        if tw["user"]["screen_name"] not in tempTweets:
            tempTweets[tw["user"]["screen_name"]] = []
        
    RelatedTweets["statuses"] = [tw for tw in RelatedTweets["statuses"] if tw["text"] not in tempTweets[tw["user"]["screen_name"]]]
    
    #RelatedTweets only has the tweets not already in the table
    numAdded = len(RelatedTweets["statuses"])
    #tempTweets has all the new and old usernames but only the old tweet text 
    
    #append to temptweets all the new tweet text
    for tw in RelatedTweets["statuses"]:
        tempTweets[tw["user"]["screen_name"]].append(tw["text"])
    
    #update Twitter Table in MySql
    sqlConn.addToTwitterTable(tempTweets, tweets)
    
    return numAdded
        

"""
function:    googleSearch 
parameters:  topic:          String describing topic of interest. 
                             Used for google search.
             sqlConn:        the mySql database connection

description: googleSearch searches the topic string in a google bar and begins 
             following articles posted on the google search result page 
             beginning with the 1st or top article and ending with the
             numArticles'st page down, or until all article on google's 
             search results are exhausted.
"""
def googleSearch(topic, domains, sqlConn):
    #TODO
    return 0





























