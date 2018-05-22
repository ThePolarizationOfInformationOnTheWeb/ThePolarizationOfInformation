#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 05:06:00 2018

@author: charlesdickens

description: This file contains a class with methods to connect to a MySQL DB
             and to retreive and update data related to topics.

"""

import json
import pymysql
import re

class MySqlConn:
    _db_connection = None
    
    def __init__(self, host = 'localhost', port = 3306, user = 'root',
                 passwd = 'root', db='mysql', charset = 'utf8'):
        
        try:
            self._db_connection = pymysql.connect(host = host, port = port, user = user,
                                   passwd = passwd, db = db, charset = charset)
        
        except:
            self._db_connection = pymysql.connect(host = host, port = port, user = user,
                                   passwd = passwd, charset = charset)
            
            with self._db_connection.cursor() as cursor:
                sqlCommand = 'CREATE DATABASE ' + db
                cursor.execute(sqlCommand)
                
                cursor.execute('USE ' + db)
                
                sqlCommand = 'CREATE TABLE Tweets '
                sqlCommand = sqlCommand + '(id INT NOT NULL AUTO_INCREMENT, '
                sqlCommand = sqlCommand + 'hashtags TEXT, '
                sqlCommand = sqlCommand + 'likes INT, '
                sqlCommand = sqlCommand + 'retweet_count INT, '
                sqlCommand = sqlCommand + 'screenName VARCHAR(50) NOT NULL, '
                sqlCommand = sqlCommand + 'PRIMARY KEY(id)) COLLATE utf8mb4_unicode_ci;'
                cursor.execute(sqlCommand)
                
                sqlCommand = 'CREATE TABLE User '
                sqlCommand = sqlCommand + '(id INT NOT NULL AUTO_INCREMENT, '
                sqlCommand = sqlCommand + 'hashtags TEXT, '
                sqlCommand = sqlCommand + 'likes INT, '
                sqlCommand = sqlCommand + 'retweet_count INT, '
                sqlCommand = sqlCommand + 'screenName VARCHAR(50) NOT NULL, '
                sqlCommand = sqlCommand + 'PRIMARY KEY(id)) COLLATE utf8mb4_unicode_ci;'
                cursor.execute(sqlCommand)
    
    
    def __del__(self):
        self._db_connection.close()
