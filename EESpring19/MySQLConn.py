import pymysql
import yaml
import sys


class MySQLConn:

    def __init__(self):
        self._conn = None

        with open("./EESpring19/keys/SQL_Login.yml", 'r') as stream:
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
                sys.exit(1)
            except pymysql.err.OperationalError as err:
                print(err)
                print('Ensure MySQL Server is running.')
                print('Ensure host, user, password, and db information are correct')
                sys.exit(1)

    def retrieve_article_text(self, topics: list):
        #translate topic names into topic ids
        topic_ids = []
        articles = {}
        with self._conn.cursor() as cursor:
            for topic in topics:
                sql_command = "SELECT topic_id FROM Topics WHERE description = '{}';".format(topic)
                cursor.execute(sql_command)
                self._conn.commit()
                result = cursor.fetchall()
                if result:
                    topic_ids.append(result[0][0])

            #use topic ids to retrieve all article ids and text with matching topic ids
            for topic_id in topic_ids:
                sql_command = "SELECT article_id, content FROM Articles WHERE topic_id = '{}';".format(topic_id)
                cursor.execute(sql_command)
                self._conn.commit()
                result = cursor.fetchall()

                for article in result:
                    articles[article[0]] = article[1]

        return articles


