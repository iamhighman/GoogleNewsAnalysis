# mysql init
import MySQLdb
import ConfigParser
import os

cur= os.path.dirname(__file__)
if cur=='': cur = '.'
CONFIG_FILE = '%s/config.txt'%cur
""" the config.txt will look like:
[mysql]
host: <your-host>
username: <your-username>
password: <your-password>
dbname: <your-dbname>
"""

def get_mysql_options(config_file=CONFIG_FILE):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    host = config.get('mysql', 'host')
    username = config.get('mysql', 'username')
    password = config.get('mysql', 'password')
    dbname = config.get('mysql', 'dbname')
    #print host, username, password
    return host, username, password,dbname

def get_connect(host=None,user=None,passwd=None,db=None,curtype="dict"):
    if not host and not user and not passwd and not db: host,user,passwd,db = get_mysql_options()
    con = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db)
    if curtype != "dict":
        pass
    else:
        con.close()
        cursorclass = MySQLdb.cursors.DictCursor
        con = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,cursorclass=cursorclass)
    print con
    return con
