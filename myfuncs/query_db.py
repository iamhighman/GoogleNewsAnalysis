#!/usr/bin/env python

'''
query_db.py - functions to query the (full) event tables

@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Jul 10, 2012

'''

import sys,os,csv
import mysql_setup

def export_query(tablename='invis_congress',
		 sql_command='select * from invis_congress limit 10',
		 ofilename='output.tsv'):
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('config.txt')
    user,passwd,host = config.get('mysql','user'),config.get('mysql','pass'),config.get('mysql','host')

    out = open("command.sql", 'w') # all the commands will go here
    out.write(sql_command)
    out.close()
    command = 'cat command.sql | mysql -u %s -p%s -h %s invis > %s'%(user,passwd,host,ofilename)
    print command
    os.system(command)

class query():
    def __init__(self):
        self.con = mysql_setup.get_connect() # you will need to edit the config.txt; see mysql_setup.py
        self.cur = self.con.cursor()
    def __del__(self):
        self.con.close()
    def count_table(self,tablename='events_allFIelds'):
	"""
	an example how to query a table
	"""
        q_str = 'select count(*) from %s'%tablename
        tmp = self.cur.execute(q_str)
        tmp = self.cur.fetchone()
        cnt = tmp['count(*)']
	print cnt
	
def query_payload_columns(tablename = 'events_allFIelds'):
    """
    this function will get number of distinct rows for column payload*, and store the results in payload_columns_in_events_allFIelds.csv
    """
    q = query()
    q.count_table(tablename=tablename) # report #rows
    # get the payload* column names
    q_str = """SELECT column_name FROM information_schema.columns
    WHERE table_name = '%s' and column_name like 'pay%%' """%tablename
    res = q.cur.execute(q_str)
    res = q.cur.fetchall()
    columns = [ c.values()[0] for c in res]
    # query each payload column
    print 'column\t\t # distinct rows'
    col2cnt = {}
    for col in columns:
	q_str = 'select count(distinct %s) from %s'%(col,tablename)
	res = q.cur.execute(q_str)
	res = q.cur.fetchone()
	print '%s\t\t %s'%(col,res.values()[0])
	col2cnt[col] = int(res.values()[0])
	# raw_input('.')
    from operator import itemgetter
    sortedpairs = sorted(col2cnt.items(), key=itemgetter(1), reverse=True)
    rows = [['column','num_distinct_rows']]
    for k,v in sortedpairs:
	row = [k,v]
	rows.append(row)
    ofilename = 'payload_columns_in_%s.csv'%tablename
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename

    # the following query is very time-consuming..
    # column_str = ','.join(columns)
    # q_str = """select count(distinct %s) from %s"""%(column_str,tablename)
    # res = q.cur.execute(q_str)
    # res = q.cur.fetchone()
    # print '%s\t %s'%('all payload*',res.values()[0])
    
def main(argv):
    query_payload_columns()
    
if __name__ == '__main__': 
    main(sys.argv[1:])
