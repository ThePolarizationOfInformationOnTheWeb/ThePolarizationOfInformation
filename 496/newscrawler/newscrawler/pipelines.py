# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
import yaml

with open("SQL_Login.yml", 'r') as stream:
    try:
        MySQLLogin = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

conn = pymysql.connect(host=MySQLLogin['localhost'],
                       user=MySQLLogin['user'],
                       passwd=MySQLLogin['password'],
                       db=MySQLLogin['NewsArticles'])
cursor = conn.cursor()

class SQLPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mysql_uri, mysql_db):
        self.mysql_uri = mysql_uri
        self.mysql_db = mysql_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_uri=crawler.settings.get('MYSQL_URI'),
            mysql_db=crawler.settings.get('MYSQL_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymysql.client(self.mysql_uri)
        self.db = self.client[self.mysql_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
