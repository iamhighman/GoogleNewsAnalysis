#!/usr/bin/env python

'''
dump_load_mongo.py - dump/load to mongo db to replace pickle

@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Dec 24, 2012

'''

import sys,os,time
from collections import defaultdict
hostname = os.uname()[1]
if 'ach' in hostname:
    from pymongo import Connection
from pprint import pprint
import random

# modify according to project
# cache_by_mongo = True
# mongoserver = 'achtung11.ccs.neu.edu'
# dbname='db_wikicrawl'

def connect_db(host='achtung11.ccs.neu.edu',dbname='db_wikicrawl'):
    trials = 0
    db,conn = None,None
    if host=='local':
	while trials < 10:
	    try:
		port = 27017 #random.randint(27017, 56144)
		conn = Connection(port=port)
		db = conn[dbname]
		break
	    except:
		trials += 1
		pprint('reconnect db...%d,%d'%(trials,port),stream=sys.stderr)
		time.sleep(0.5*trials)
    else:
	while trials < 10:
	    try:
		port = 27017 #random.randint(27017, 56144)
		conn = Connection(host=host,port=port)
		db = conn.yuru[dbname]
		break
	    except:
		trials += 1
		pprint('reconnect db...%d,%d'%(trials,port),stream=sys.stderr)
		time.sleep(0.5*trials)
    if db and conn:
	return db,conn
def dump_mongo(host='local',dbname='counts',collection='caller2cnt',obj=None):
    '''dump the dictionary object into mongodb'''
    db,conn = connect_db(host=host,dbname=dbname)
    dbc = db[collection]
    sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    if obj:
	data = []
	for i,(k,v) in enumerate(obj.iteritems()):
	    data.append({'_id':k,'val':v})
	    if i%100000==0:
		sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,i )); sys.stdout.flush()
		dbc.insert(data,continue_on_error=True) # bulk insert; faster!
		data = []
	dbc.insert(data,continue_on_error=True) # bulk insert; faster!
	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    conn.close()
    # return dbc.count()
def save_mongo(host='local',dbname='counts',collection='caller2cnt',obj=None,verbose=False):
    '''update/insert the dictionary object into mongodb'''
    db,conn = connect_db(host=host,dbname=dbname)
    dbc = db[collection]
    if verbose:
	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    if obj:
	for i,(k,v) in enumerate(obj.iteritems()):
	    dbc.save({'_id':k,'val':v})
	    if verbose and i%100000==0:
	    	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,i )); sys.stdout.flush()
	if verbose:
	    sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    conn.close()
    # return dbc.count()
def update_mongo(host='local',dbname='counts',collection='caller2cnt',obj=None,verbose=False):
    '''update the dictionary object into mongodb'''
    db,conn = connect_db(host=host,dbname=dbname)
    dbc = db[collection]
    if verbose:
	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    if obj:
	for i,(k,v) in enumerate(obj.iteritems()):
	    dbc.update({'_id':k},{'$set':v})
	    if verbose and i%100000==0:
	    	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,i )); sys.stdout.flush()
	if verbose:
	    sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    conn.close()
    # return dbc.count()

def load_mongo(host='local',dbname='counts',collection='caller2cnt',key=None,verbose=False):
    '''load the dictionary object from mongodb'''
    db,conn = connect_db(host=host,dbname=dbname)
    dbc = db[collection]
    if verbose:
	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %i -" % (collection,dbc.count() )); sys.stdout.flush()
    obj = {}
    if not key:
	for e in dbc.find():
	    obj[e['_id']] = e['val']
    else:
	query = {'_id':key}
	e = dbc.find_one(query)
	if e is None: return obj
	obj = e['val']
    conn.close()
    return obj
def count_mongo(host='local',dbname='counts',collection='caller2cnt',verbose=False):
    '''count the number of dictionary objects in the given db.collection from mongodb'''
    db,conn = connect_db(host=host,dbname=dbname)
    dbc = db[collection]
    count = dbc.count()
    if verbose:
	sys.stderr.write("\r                               \r"); sys.stderr.write("collection %s: %d -" % (collection,count )); sys.stdout.flush()
    conn.close()
    return count

def main(argv):
    args = set( a.lower() for a in sys.argv[1:] )
    for i,arg in enumerate(argv):
	if arg in ['-h','--help']: print 'usage:'
    pass
if __name__ == '__main__': 
    main(sys.argv[1:])
