# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
import yaml

collection_name = 'scrapy_items'

    def __init__(self):
        with open("SQL_Login.yml", 'r') as stream:
            try:
                mysql_login = yaml.load(stream)['MySQL_DB']
                self._conn = pymysql.connect(host=mysql_login['host'],
                                       user=mysql_login['user'],
                                       passwd=mysql_login['password'],
                                       db=mysql_login['db'])
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)
            except pymysql.err.OperationalError as err:
                print(err)
                print('Ensure MySQL Server is running.')
                print('Ensure host, user, password, and db information are correct')
                exit(1)
        
        # Use database
        try:
            with self._conn.cursor() as cursor:
                sql_command = "USE " + mysql_login['db']
                cursor.execute(sql_command)
                self._conn.commit()
        except pymysql.err.InternalError as err:
            print(err)
            exit(1)


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
