#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 10:56:16 2017

@author: charlesdickens
"""


import json
import pymysql
import re

class MySqlConn:
    _db_connection = None
    
    def __init__(self, host = 'localhost', port = 3306, user = 'root',
                 passwd = 'passwd', db = 'mysql', charset = 'utf8'):
        
        self._db_connection = pymysql.connect(host = host, port = port, user = user,
                                   passwd = passwd, db = db, charset = charset)
    
    
    def __del__(self):
        self._db_connection.close()
    
    """
    function:    mySqlConnection 
    parameters:  topic:          String describing topic of interest. 
                                 Used database name.
    
    description: Attempts to connect to the mySql server on the local machine and 
                 then uses the topic to either create or continue building a 
                 database for the topic
    return:      sqlConn:        The sql server connection using the database 
                                 for the topic
    """
    def mySqlDatabase(self, topic):
    
        #check if database for topic already exists
        db = re.sub(r"\s", "", topic.lower())
        try:
            with self._db_connection.cursor() as cursor:
                sqlCommand = "USE " + db
                cursor.execute(sqlCommand)
                self._db_connection.commit()
        #if database doesn't exist create database for topic
        except pymysql.err.InternalError as err:
            code, msg = err.args
            #err 1049 corresponds to non existing database
            #if database doesn't exist create on
            if code == 1049:
                with self._db_connection.cursor() as cursor:
                    sqlCommand = "CREATE DATABASE " + db + " COLLATE = utf8mb4_unicode_ci"
                    cursor.execute(sqlCommand)
                    sqlCommand = "USE " + db
                    cursor.execute(sqlCommand)
                    self._db_connection.commit()
            else:
                #if another error is raised print error message
                print msg
                self._db_connection = None
    
    """
    function:    retrieveDomains
    description: retrieveDomains returns a dictionary of existing domain tables 
                 and corresponding headlines relating to the topic.
    return:      domains:        a dict with key domain name and value list of 
                                  headlines for articles existing in table
                 tweets:         a dict with key username and value list of tweets
                                 from user
    """ 
    def retrieveDomains(self):
        domains = {}        #domains dictionary to hold domain and headlines 
        tweets = {}
        
        with self._db_connection.cursor() as cursor:
            #find all tables in database
            sqlCommand = "SHOW TABLES"
            cursor.execute(sqlCommand)
            result = cursor.fetchall()
        
        for t in result:
            for domainName in t:
                #add domain name to dictionary
                domains[str(domainName)] = []
                if domainName != "Twitter":
                    with self._db_connection.cursor() as cursor:
                        #fetch all headlines in domain name table and add to dictionary
                        sqlCommand = "SELECT headline FROM " + str(domainName)
                        cursor.execute(sqlCommand)
                        rslt = cursor.fetchall()
                    for h in rslt:
                        for headline in h:
                            #add headline to domain name in domains
                            domains[str(domainName)].append(headline)
                else:
                    with self._db_connection.cursor() as cursor:
                        #fetch all users in twitter table and add to dictionary
                        sqlCommand = "SELECT screenName FROM Twitter"
                        cursor.execute(sqlCommand)
                        rslt = cursor.fetchall()
        
                    for u in rslt:
                        for user in u:
                            #add domain name to dictionary
                            tweets[user] = []
                            with self._db_connection.cursor() as cursor:
                                #fetch all tweets from user
                                sqlCommand = "SELECT tweets FROM Twitter WHERE screenName = \""
                                sqlCommand = sqlCommand + user
                                sqlCommand = sqlCommand + "\""
                                cursor.execute(sqlCommand)
                                userTweets = cursor.fetchall()
                            
                            for Tw in userTweets:
                                for tweet in Tw:
                                    #add user to twitter with tweets
                                    tweets[user] = json.loads(tweet)                           
        
        
        return domains,tweets    

    """
    function:    createTable
    parameters:  domainName:    the domain name table to be added to the database
                                being USEd by the mySql connection
                 sqlConn:       the mySql connection
    description: create a table in the mySql database being USEd by the mysql 
                 connection with title matching the domain name
    """
    def createTable(self, domainName):
        domainName = re.sub(r"\s", "", domainName.lower())
        domainName = re.sub(r"\..*$", "", domainName)
        domainName = re.sub(r"\/","", domainName)
        domainName = re.sub(r"\-","", domainName)
        domainName = re.sub("&","",domainName)
        domainName = re.sub("!","",domainName)
        domainName = re.sub("\(\w*\)","",domainName)
        
        
        try:
            with self._db_connection.cursor() as cursor:
                sqlCommand = "CREATE TABLE " + domainName + "("
                sqlCommand = sqlCommand + "id INT NOT NULL AUTO_INCREMENT, "
                sqlCommand = sqlCommand + "headline VARCHAR(200) NOT NULL COLLATE utf8mb4_unicode_ci, "
                sqlCommand = sqlCommand + "content TEXT NOT NULL COLLATE utf8mb4_unicode_ci, "
                sqlCommand = sqlCommand + "url VARCHAR(250) NOT NULL, "
                sqlCommand = sqlCommand + "links JSON NULL, "
                sqlCommand = sqlCommand + "dateWritten DATE NULL, "
                sqlCommand = sqlCommand + "dateScraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                sqlCommand = sqlCommand + "PRIMARY KEY(id)"
                sqlCommand = sqlCommand + ") COLLATE utf8mb4_unicode_ci"
                cursor.execute(sqlCommand)
                self._db_connection.commit()
        except pymysql.err.ProgrammingError as err:
            print sqlCommand
            code, msg = err.args
            print msg
            
    """
    function:    addToTable
    parameters:  
    description:
    """
    def addToTable(self, domain, headline, url, text, date):
        text = re.sub(r"\"", "\\\"", text)
        
        headline = re.sub(r"\"", "\\\"", headline)
        
        try:
        
            with self._db_connection.cursor() as cursor:
                sqlCommand = "INSERT INTO " + domain
                sqlCommand = sqlCommand + "(headline, content, url, dateWritten) "
                sqlCommand = sqlCommand + "VALUES (\"" + headline + "\", "
                sqlCommand = sqlCommand + "\"" + text + "\", "
                sqlCommand = sqlCommand + "\"" + url + "\", "
                sqlCommand = sqlCommand + "\"" + date + "\")"
                cursor.execute(sqlCommand)
                self._db_connection.commit()
        
        except (pymysql.err.InternalError,pymysql.err.ProgrammingError) as err:
            print sqlCommand
            code, msg = err.args
            print msg
            
    """
    """
    def createTwitterTable(self):
        try: 
            with self._db_connection.cursor() as cursor:
                sqlCommand = "CREATE TABLE Twitter("
                sqlCommand = sqlCommand + "screenName VARCHAR(200) NOT NULL COLLATE utf8mb4_unicode_ci, "
                sqlCommand = sqlCommand + "tweets JSON NULL, "
                sqlCommand = sqlCommand + "dateWritten DATE NULL, "
                sqlCommand = sqlCommand + "dateScraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                sqlCommand = sqlCommand + "PRIMARY KEY(screenName)"
                sqlCommand = sqlCommand + ") COLLATE utf8mb4_unicode_ci"
                cursor.execute(sqlCommand)
                self._db_connection.commit()
        except pymysql.err.ProgrammingError as err:
            code, msg = err.args
            print sqlCommand
            print msg
            
    """
    function:    addToTwitterTable
    parameters:  tw:             The dict of all the tweets to be updated old and new
                 tweets:         The existing tweets in the database already
    description: addToTwitterTable will update the user if the user has a new tweet
                 or insert a new element into the table if the user doesnt exist
                 already.
    """
    def addToTwitterTable(self, tw, tweets):
        try:   
             #format text in tw for JSON
             tw = {username:[re.sub("\n",r"\\n",tweet) for tweet in tw[username]] for username in tw}
             for user in tw:   
                if user not in tweets:
                    #add new user to twitter table
                    #insert tweets into database
                    with self._db_connection.cursor() as cursor:
                        twtJSONList = json.dumps(tw[user])
                        #replace ' with \'
                        replace = chr(92) + chr(39)
                        twtJSONList = re.sub("'",replace,twtJSONList)
                        twtJSONList = re.sub("\\\"","\\\\\"",twtJSONList)
                        sqlCommand = "INSERT INTO Twitter (screenName, tweets) VALUES("
                        sqlCommand = sqlCommand + "\'" + user + "\'" + ", "
                        sqlCommand = sqlCommand + "\'"+ twtJSONList + "\'"
                        sqlCommand = sqlCommand + ")"
                        cursor.execute(sqlCommand)
                        self._db_connection.commit()
                
                else:
                    #update existing user
                    #update tweets
                    with self._db_connection.cursor() as cursor:
                        twtJSONList = json.dumps(tw[user])
                        #replace ' with \'
                        replace = chr(92) + chr(39)
                        twtJSONList = re.sub("'",replace,twtJSONList)
                        twtJSONList = re.sub("\\\"","\\\\\"",twtJSONList)
                        sqlCommand = "UPDATE Twitter SET tweets = "
                        sqlCommand = sqlCommand + "\'" + twtJSONList + "\'"
                        sqlCommand = sqlCommand + " WHERE screenName = \'" + user + "\'"
                        cursor.execute(sqlCommand)
                        self._db_connection.commit()
        except (pymysql.err.InternalError,pymysql.err.ProgrammingError) as err:
            code, msg = err.args
            print sqlCommand
            print msg
            
        
    def retrieveArticles(self):
        articlesDict = {}        #articlesDict dictionary to hold domain and headlines
                             #and article text
                             
        articlesList = []
        
        domains, tweets = self.retrieveDomains()
        
        articlesDict = {d:{} for d in domains}
        
        for d in articlesDict:
            articlesDict[d] = {h:'' for h in domains[d]}
                
        
        for d in articlesDict:
            for h in articlesDict[d]:
                with self._db_connection.cursor() as cursor:
                    replace = chr(92) + chr(39)
                    head = re.sub("'",replace,h)
                    head = re.sub("\\\"","\\\\\"",head)
                    sqlCommand = "SELECT content FROM " + d
                    sqlCommand = sqlCommand + " WHERE headline = \'" + head + "\'"
                    cursor.execute(sqlCommand)
                    contents = cursor.fetchall()
                
                for c in contents:
                    for text in c:
                       articlesDict[d][h] = text
                       articlesList.append((d,h,text))
        
        
        
        return articlesDict, articlesList 
            
               
    
            

