# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
import yaml


class SQLPipeline(object):
    collection_name = 'scrapy_items'

    def __init__(self):
        self._conn = None

        with open("SQL_Login.yml", 'r') as stream:
            try:
                mysql_login = yaml.load(stream)['MySQL_DB']
                self._conn = pymysql.connect(host=mysql_login['host'],
                                             user=mysql_login['user'],
                                             passwd=mysql_login['password'],
                                             db=mysql_login['db'])

                with self._conn.cursor() as cursor:
                    sql_command = "USE " + mysql_login['db']
                    cursor.execute(sql_command)
                    self._conn.commit()
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)
            except pymysql.err.OperationalError as err:
                print(err)
                print('Ensure MySQL Server is running.')
                print('Ensure host, user, password, and db information are correct')
                exit(1)

    def open_spider(self, spider):
        # check if topic exists in topic table
        # and add topic as relation if not already in topic
        with self._conn.cursor() as cursor:
            sql_command = "SELECT 1 FROM Topics WHERE description = '{}' ;".format(spider.topic)
            cursor.execute(sql_command)
            self._conn.commit()
            result = cursor.fetchall()
            #print("RESULT ____________________________________")
            #print(result)
            if not result:
                sql_command = "INSERT INTO Topics (description) VALUES('{}') ;".format(spider.topic)
                cursor.execute(sql_command)
                self._conn.commit()

            sql_command = "SELECT topic_id FROM Topics WHERE(description) = '{}' ;".format(spider.topic)
            cursor.execute(sql_command)
            self._conn.commit()
            self.topic_id = cursor.fetchall()[0][0]
            #print(self.topic_id)


    def close_spider(self, spider):
        self._conn.close()

    def process_item(self, item, spider):
        with self._conn.cursor() as cursor:
            sql_command = "SELECT 1 FROM Articles WHERE url = '{}' ;".format(item['url'])
            cursor.execute(sql_command)
            self._conn.commit()
            result = cursor.fetchall()
            if not result:
                url = self._conn.escape(item['url'])
                content = self._conn.escape(item['content'])
                title = self._conn.escape(item['title'])
                topic_id = self._conn.escape(self.topic_id)
                sql_command = "INSERT INTO Articles (url, content, title, topic_id) VALUES ({},{},{},{})".format(url, content, title, topic_id)
                cursor.execute(sql_command)
                self._conn.commit()
