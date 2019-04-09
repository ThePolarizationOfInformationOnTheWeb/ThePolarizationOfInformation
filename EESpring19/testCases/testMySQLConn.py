from EESpring19.MySQLConn import MySQLConn

topics = ['government shutdown']
print('Creating MySQLConn Object')
Connection = MySQLConn("../../EESpring19/keys/SQL_Login.yml")
print('Retrieving Article Text')
ArticleText = Connection.retrieve_article_text(topics)
print(ArticleText)