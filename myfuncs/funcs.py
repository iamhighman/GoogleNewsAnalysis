import sys,os,csv
from datetime import datetime, timedelta
import time
from operator import itemgetter
import cPickle as pickle
from pprint import pprint

TIME_RES = 'month'
NA = 0 # missing or default value
# non_blog = set(['the associated press','associated press','cnn','abcnews.com'])
# unknown_blog = set(['admin','administrator','postingaccount','staff','zip','max','news','news staff','editor','staffwriter','','author'])

monthDict = {"Jan.":1, "Feb." :2, "March":3, "April":4, "May":5, "June":6, "July":7, "Aug.":8, "Sept.":9,  "Oct.":10,  "Nov.":11,  "Dec.":12}

time_format0 = "%Y-%m-%d %H:%M:%S"
time_format1 = '%a %b %d %H:%M:%S +0000 %Y'
time_format2 = '%a, %d %b %Y %H:%M:%S +0000'
time_format_mysql = "%Y-%m-%d %H:%M:%S" # default for MySQL
time_format_short = "%Y%m%d%H%M%S"
time_format_long = "%Y-%m-%d %H:%M:%S"

def uprint(s):
    try:
        sys.stdout.write(unicode(s)+'\n')
    except UnicodeEncodeError, e:
        sys.stderr.write('UnicodeDecodeError: %s\n'%e)
    else: pass
def change_terminal_encoding():
    os.system('export PYTHONIOENCODING=utf-8')
    print sys.stdout.encoding
def timestamp(iformat = time_format_mysql):
    return datetime.utcnow().strftime(iformat)

def today(): return datetime.utcnow().strftime("%Y-%m-%d")
def yesterday(): return (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%d")
def timestr2timestr_month(ts,iformat="%m %d, %Y",oformat="%Y%m%d"):
    m = ts.split()[0]
    if m == 'NA': return None
    m = monthDict[m]
    ts = ts.split()
    ts[0] = str(m)
    ts = ' '.join(ts); #print ts
    try:
	t = datetime.strptime(ts, iformat)
	return datetime.strftime(t, oformat)
    except: return None
def timestr2timestr(ts, iformat="%Y-%m-%d %H:%M:%S",oformat="%Y%m%d%H%M%S"):
    t = datetime.strptime( ts, iformat )
    return datetime.strftime(t,oformat)
def timestr2weeknum(ts,iformat="%Y%m%d",oformat = "%W"):
    if iformat=="%Y%m%d" and len(ts)>8: ts = ts[:8]
    t = datetime.strptime( ts, iformat )
    return int( datetime.strftime(t,oformat) )
def yearweeknum2timestr(ts,iformat='y%Y-w%W-%w',oformat='%Y%m%d'):
    t = datetime.strptime( ts, iformat )
    return datetime.strftime(t,oformat)
def timestr2daynum(ts,iformat="%Y%m%d",oformat = "%j"):
    if iformat=="%Y%m%d" and len(ts)>8: ts = ts[:8]
    t = datetime.strptime( ts, iformat )
    return int( datetime.strftime(t,oformat) )
def timestr2yearweek(ts,iformat="%Y%m%d",oformat = "%W"):
    w = timestr2weeknum(ts)
    return '%s-%02d'%(ts[:4],w)
def unixtime2timestr(unixtime,oformat='%Y%m%d%H%M%S'):
    t = datetime.fromtimestamp(unixtime)
    return datetime.strftime(t,oformat)
def top_dict(a2i,reverse=True,cutoff=5):
    from operator import itemgetter
    sortedpairs = sorted(a2i.items(), key=itemgetter(1), reverse=reverse)
    print len(a2i),sortedpairs[:cutoff]
    tops = [k for k,v in sortedpairs[:cutoff]]
    return tops
def top_percent_dict(a2i,reverse=True,cutoff=90):
    from operator import itemgetter
    from numpy import array,cumsum
    sortedpairs = sorted(a2i.items(), key=itemgetter(1), reverse=reverse)
    wgts = array([v for k,v in sortedpairs])
    total = sum(wgts)
    cwgts = cumsum(wgts);#print cwgts;raw_input('.')
    print len(a2i)
    tops = []
    for i,(k,v) in enumerate(sortedpairs):
	if cwgts[i]> total*cutoff/100.0: break
	# print k,v,cwgts[i]
	tops.append((k,v))
    return tops
def print_dict(a2i,reverse=False,cutoff=5):
    from operator import itemgetter
    sortedpairs = sorted(a2i.items(), key=itemgetter(1), reverse=reverse)
    print len(a2i),sortedpairs[:cutoff]
    return sortedpairs[:cutoff]
def reverse_dict(a2i):
    return dict([(i,a) for a,i in a2i.iteritems()])
def save_dict_txt(a2i,ofilename,reverse=False):
    sortedpairs = sorted(a2i.items(), key=itemgetter(1), reverse=reverse)
    rows = []
    for a,i in sortedpairs:
	rows.append([a])
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename
def save_dict_attr_txt(a2i,ofilename=None,a2attr=None,reverse=False):
    # line number = id: field1=object key, field2,3,... =attributes
    sortedpairs = sorted(a2i.items(), key=itemgetter(1), reverse=reverse)
    rows = []
    for a,i in sortedpairs:
	row = [a]
	if a2attr: row.extend(a2attr[a])
	rows.append(row)
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename,len(rows),'rows'
    
def save_list_txt(aa,ofilename,verbose=False):
    rows = []
    for a in aa: rows.append([a])
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    if verbose: print 'save to',ofilename,len(rows),'lines'
def load_list_txt(ifilename,startline=-1,endline=-1,linenums=None,verbose=False):
    if verbose: print 'read from',ifilename
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    rows = []
    for i,fields in enumerate(reader):
	sys.stdout.write("\r       \r"); sys.stdout.write("%i -" % (i)); sys.stdout.flush()	    
	if startline>=0 and i<startline:continue
	if endline>=0 and i>endline: break
	if linenums and not i in linenums: continue
	rows.append(fields[0])
	# if i==0: print fields	    
    ifile.close()
    if verbose: print '\t...',len(rows),'lines'
    return rows
def load_list_txt_into_dict(ifilename,startline=-1,endline=-1,linenums=None,start_index=1):
    return dict([(w,i+start_index) for i,w in enumerate(load_list_txt(ifilename,startline=startline,endline=endline,linenumms=linenums))])
def save_sortedpairs_txt(sortedpairs,ofilename):
    rows = []
    for a,i in sortedpairs:
	rows.append([a,i])
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename
def save_mat_dict_txt(m2c,ofilename,delim='\t'):
    rows = []
    for m,c in m2c.iteritems():
	rows.append([m[0],m[1],c])
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename,len(rows)
def load_mat_dict_txt(ifilename,delim='\t',verbose=False):
    if verbose: print 'read from',ifilename
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    mat = {}
    for i,fields in enumerate(reader):
	sys.stdout.write("\r                     \r"); sys.stdout.write("%i -" % (i)); sys.stdout.flush()
	u,v,w = fields
	w = float(w)
	mat[u,v] = w
    ifile.close()
    print 'load from',ifilename,len(mat),'edges'
    return mat
def get_all_minutes(start, finish, format="%Y%m%d"):
    """all minutes in interval [start, finish)"""
    start  = datetime.strptime( start, format )
    finish = datetime.strptime( finish, format )
    D = [start]
    curr = start
    dt = timedelta(minutes=1)
    while curr < finish:
        curr += dt
        D.append(curr)
    return [datetime.strftime(h,"%Y%m%d%H%M") for h in D[:-1]]        
def get_all_hours(start, finish, format="%Y%m%d"):
    """all hours in interval [start, finish)"""
    start  = datetime.strptime( start, format )
    finish = datetime.strptime( finish, format )
    D = [start]
    curr = start
    dt = timedelta(hours=1)
    while curr < finish:
        curr += dt
        D.append(curr)
    return [datetime.strftime(h,"%Y%m%d%H") for h in D[:-1]]    
def get_timestr_byRES(ts,TIME_RES=TIME_RES):
    """ts is timestr in format %Y%m%d; return timestr by resolution"""
    day = ts[:8]
    month = ts[:6]
    if TIME_RES == 'month': t=month
    elif TIME_RES == 'day': t=day
    return t
    
def get_t2i(start='20110101',finish='20111231'):
    t2i = dict( (ts,i+1) for i,ts in enumerate(get_all_days(start, finish)) )
    return t2i
def get_window_t(t,run_window=3,t2i=None):
    if not t2i: t2i = get_t2i()
    i2t = reverse_dict(t2i)
    dt = run_window / 2
    win = []
    for i in range(dt):
	ii = t2i[t] - (i+1)
	if ii in i2t:
	    tt = i2t[ii]
	    win.append(tt)
	ii = t2i[t] + (i+1)
	if ii in i2t:
	    tt = i2t[ii]
	    win.append(tt)
    return win
def get_net(ifilename,delim='\t',symm=True):
    if symm: G = nx.read_weighted_edgelist(ifilename,delimiter=delim)
    else: G = nx.read_weighted_edgelist(ifilename,delimiter=delim,create_using=nx.DiGraph())
    print 'net: (|V|=%d,|E|=%d) from %s'%(G.number_of_nodes(),G.number_of_edges(),ifilename)
    return G
def get_projection_net(ifilename,ofilename,delim='\t',tmpname='',selected=None,transpose=False,normalized=False):
    if selected: selected = map(str,selected)
    _ofilename = ofilename
    # step 1) read the edgelist and construct node2integer dictionaries
    a2i,b2i= {},{}
    print 'read from',ifilename,'; to save to',ofilename
    # raw_input('.')
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    rows = []
    for i,fields in enumerate(reader):
	a,b,c = fields
	if selected and (not a in selected):
	    continue
	a2i.setdefault(a,len(a2i)+1)
	b2i.setdefault(b,len(b2i)+1)
	row = [a2i[a],b2i[b],c]
	rows.append(row)
    ifile.close()
    # step 2) save the edgelist to temp.txt
    ofilename = 'temp%s.txt'%tmpname
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    # print 'save to',ofilename
    # step 3) use R script to do projection and save to temp_p.txt
    ifilename = 'temp%s.txt'%tmpname
    ofilename = 'temp%s_p.txt'%tmpname
    ofile = open(ofilename, "w"); ofile.close() # clean the output file
    if not normalized:
	script ='''
      library(Matrix);library(MASS)
      ifilename <- '%s'
      x <- scan(ifilename,what=list(integer(),integer(),numeric()))
      r2i <- sparseMatrix(i=x[[1]],j=x[[2]],x=x[[3]])
      #i2i = t(r2i) %%*%% r2i
      r2r = (r2i) %%*%% t(r2i)
      ofilename <- '%s'
      writeMM(r2r,file=ofilename)	
	    '''%(ifilename,ofilename)
	if transpose:
	    script ='''
      library(Matrix);library(MASS)
      ifilename <- '%s'
      x <- scan(ifilename,what=list(integer(),integer(),numeric()))
      r2i <- sparseMatrix(i=x[[1]],j=x[[2]],x=x[[3]])
      i2i = t(r2i) %%*%% r2i
      # r2r = (r2i) %%*%% t(r2i)
      ofilename <- '%s'
      writeMM(i2i,file=ofilename)	
	    '''%(ifilename,ofilename)
    else:
	script ='''
      library(Matrix);library(MASS)
      ifilename <- '%s'
      x <- scan(ifilename,what=list(integer(),integer(),numeric()))
      r2i <- sparseMatrix(i=x[[1]],j=x[[2]],x=x[[3]])
      D1 <- rowSums(r2i)
      r2i <- diag(D1^(-1)) %%*%% r2i
      #i2i = t(r2i) %%*%% r2i
      r2r = (r2i) %%*%% t(r2i); r2r<-as(r2r,'sparseMatrix') #print(dim(r2r))
      ofilename <- '%s'
      writeMM(r2r,file=ofilename)	
	    '''%(ifilename,ofilename)
	if transpose:
	    script ='''
      library(Matrix);library(MASS)
      ifilename <- '%s'
      x <- scan(ifilename,what=list(integer(),integer(),numeric()))
      r2i <- sparseMatrix(i=x[[1]],j=x[[2]],x=x[[3]])
      i2r <- t(r2i)
      D1 <- rowSums(i2r)
      i2r <- diag(D1^(-1)) %%*%% i2r
      i2i = i2r %%*%% t(i2r); i2i<-as(i2i,'sparseMatrix')
      ofilename <- '%s'
      writeMM(i2i,file=ofilename)	
	    '''%(ifilename,ofilename)
	
    # print script
    command = 'echo "%s" > tmp.R'%script
    os.system(command)
    command = "R --no-save --quiet --slave < tmp.R 1>/dev/null"
    os.system(command)
    # step 4) read from temp_p.txt and re-save the edgelist to ofilename, using the dictiories
    ifilename = 'temp%s_p.txt'%tmpname
    print 'read from',ifilename
    # raw_input('.')
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=' ',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    rows = []
    i2a = reverse_dict(a2i)
    if transpose: i2a = reverse_dict(b2i)
    # i2b = reverse_dict(b2i)
    # print len(i2a),len(a2i)
    # raw_input('.')
    pattern = False
    for i,fields in enumerate(reader):
	if i==0:
	    # print fields
	    if fields[3]=='pattern': pattern=True
	    continue
	if i==1: 
	    print 'm,n,nnz:',fields
	    # raw_input('.')
	    continue
	# print fields
	if pattern: ni,nj = fields; c=1
	else: ni,nj,c = fields
	if ni==nj: continue
	ni,nj = int(ni),int(nj)
	if not ni in i2a or not nj in i2a: continue
	ni,nj = i2a[ni],i2a[nj]
	row = [ni,nj,c]
	# print i,'%s %s %s'%(ni,nj,c)
	rows.append(row)
    ifile.close()
    # raw_input('.')
    ofilename = _ofilename
    # print 'to save to',ofilename
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename
    # raw_input('.')
def market2txt(ifilename,ofilename,delim='\t',remove_self=True):
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=' ',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    rows = []
    pattern = False
    I,J = set(),set()
    nlinks = 0
    for i,fields in enumerate(reader):
	if i==0:
	    # print fields
	    if fields[3]=='pattern': pattern=True
	    continue
	if i==1: 
	    print 'm,n,nnz:',fields
	    continue
	# print fields
	if pattern: ni,nj = fields; c=1
	else: ni,nj,c = fields
	nlinks += 1
	if remove_self and ni==nj:
	    nlinks -= 1
	    c=0
	I.add(ni); J.add(nj)
	row = [ni,nj,c]
	rows.append(row)
    ifile.close()
    ofile = open(ofilename, "w")
    writer = csv.writer(ofile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    print 'save to',ofilename
    print len(I),len(J),'#links=',nlinks,'(does not count self-loops)'
    
def load_net(ifilename,u2i=None,symm=True,delim='\t'):
    print 'read from',ifilename
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    edges = {}
    for i,fields in enumerate(reader):
	a,b,c = fields
	if u2i:
	    ia,ib = u2i[a],u2i[b]
	    edges.setdefault((ia,ib),float(c))
	    if symm: edges.setdefault((ib,ia),float(c))
	else:
	    edges.setdefault((a,b),float(c))
	    if symm: edges.setdefault((b,a),float(c))
    ifile.close()
    return edges
def load_net_2mode(ifilename,u2i=None,w2i=None,symm=False,delim='\t'):
    print 'read from',ifilename
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=delim,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    edges = {}
    for i,fields in enumerate(reader):
	a,b,c = fields
	if u2i and w2i:
	    w2i.setdefault(b,len(w2i)+1)
	    ia,ib = u2i[a],w2i[b]
	    edges.setdefault((ia,ib),float(c))
	else:
	    edges.setdefault((a,b),float(c))
    ifile.close()
    return edges
    
def get_metric(G,metric='deg'):
    if metric=='deg': m = nx.algorithms.centrality.degree_centrality(G)
    if metric=='idg': m = nx.algorithms.centrality.in_degree_centrality(G)
    if metric=='odg': m = nx.algorithms.centrality.out_degree_centrality(G)
    if metric=='clo': m = nx.algorithms.centrality.closeness_centrality(G)
    if metric=='btw': m = nx.algorithms.centrality.betweenness_centrality(G,normalized=True,endpoints=True) #weight doesn't work?
    if metric=='eig': m = nx.algorithms.centrality.eigenvector_centrality(G)
    if metric=='loa': m = nx.algorithms.centrality.load_centrality(G,normalized=True,weight=True) #weight doesn't work?
    if metric=='ncq': m = nx.algorithms.clique.number_of_cliques(G)
    print metric
    print_dict(m,reverse=True)
    return m
def get_mainstream(ifilename='news_list.csv'):
    print 'read from',ifilename
    ifile = open(ifilename,'r')
    reader = csv.reader(ifile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    idx2type = {}
    name2idx = {}
    news2name = {}
    for i,fields in enumerate(reader):
	if i==0:
	    # print fields
	    continue
	if '?' in fields[0]: continue
	newsname = fields[0].strip().lower()
	newstype = fields[1].strip().lower()
	name2idx.setdefault(newsname,len(name2idx)+1)
	idx = name2idx[newsname]
	news2name[newsname] = newsname
	idx2type[idx] = newstype
	if 'blog' in newsname: continue
	if len(fields)>2: cnt = fields[2]
	if len(fields)>3:
	    othername = fields[3].lower()
	    name2idx.setdefault(othername,idx) 
	    news2name[othername] = newsname 
    ifile.close()
    return news2name,name2idx,idx2type
def pickleload(ifilename,verbose=False):
    if not os.path.exists(ifilename):
	pprint( u'file not exist: {0}'.format(ifilename),stream=sys.stderr )
	return None
    try:
	ifile = open(ifilename,'rb')
	obj = pickle.load(ifile)
	ifile.close()
    except:
	pprint( u'file error: {0}'.format(ifilename),stream=sys.stderr )
	return None
    if verbose: pprint( u'load from {0} {1} {2} KB'.format(ifilename, len(obj), os.path.getsize(ifilename)/1000.0),stream=sys.stderr )
	# print 'load from', ifilename, len(obj), os.path.getsize(ifilename)/1000.0,'KB'
    return obj
def pickledump(obj,ofilename,verbose=False):
    ofile = open(ofilename,'wb')
    pickle.dump(obj, ofile, protocol=2)
    ofile.close()
    if verbose: pprint( u'save to {0} {1} {2} KB'.format(ofilename, len(obj), os.path.getsize(ofilename)/1000.0),stream=sys.stderr )
	# print 'save to', ofilename, len(obj), os.path.getsize(ofilename)/1000.0,'KB'
def test_output(ofilename):
    if not os.path.exists(ofilename):
	print 'error: file not exist:',ofilename
	raw_input('.')

def check_format(ts):
    if '-' in ts and ':' in ts and ts.split()>1: return time_format_long
    else: return time_format_short
def time_diff_day(start_str,finish_str, fmt="%Y%m%d"):
    """return number of days between two dates"""
    # format = check_format(start_str)
    s = datetime.strptime( start_str, fmt )
    # format = check_format(finish_str)
    f = datetime.strptime( finish_str, fmt )
    return (f-s).days
def time_diff_min(start_str, finish_str, format="%Y%m%d%H%M"):
    """return number of minutes between two dates"""
    s = datetime.strptime( start_str, format )
    f = datetime.strptime( finish_str, format )
    return (f-s).days*24*60 + (f-s).seconds/60.0
def time_diff_sec(start_str, finish_str, format="%Y%m%d%H%M%S"):
    """return number of minutes between two dates"""
    s = datetime.strptime( start_str, format )
    f = datetime.strptime( finish_str, format )
    return (f-s).days*24*60*60 + (f-s).seconds

def get_all_days(start, finish, format="%Y%m%d"):
    """all days in interval [start, finish]"""
    start  = datetime.strptime( start, format )
    finish = datetime.strptime( finish, format )
    D = [start]
    curr = start
    dt = timedelta(days=1)
    while curr <= finish:
        curr += dt
        D.append(curr)
    return [datetime.strftime(h,format) for h in D[:-1]]

def get_field(fieldname,fields,name2field,name2desc=None,verbose=False):
    if verbose and name2desc:
	print name2desc[fieldname],fields[name2field[fieldname]].strip()
    try: value = fields[name2field[fieldname]].strip()
    except: value = 'NA'
    return value
    
def get_field_value(fieldname,fields,name2field,name2desc=None,verbose=False):
    if verbose and name2desc:
	print name2desc[fieldname],fields[name2field[fieldname]].strip()    
    try:
	value = fields[name2field[fieldname]].strip()
	value = float(value)
    except: value = 'NA'
    return value
def get_fid_value(fid,fields):
    value = fields[fid].strip()
    try: value = float(value)
    except: value = 'NA'
    return value

# from Simple Recipes in Python: http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html    
def meanstdv(x):
    """
    Mean and standard deviation of data
    Usage:
        real, real = meanstdv(list)    
    Calculate mean and standard deviation of data x[]:
    mean = {\sum_i x_i \over n}
    std = sqrt(\sum_i (x_i - mean)^2 \over n-1)
    """
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    if n>1: 
        for a in x:
            std = std + (a - mean)**2
        std = sqrt(std / float(n-1))
    return mean, std

def run_sql(action='build',tablename='tweets'):
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('config.txt') #somApiName.apikey = self.config.get('somApiName', 'apikey')
    user,passwd,host = config.get('mysql','user'),config.get('mysql','pass'),config.get('mysql','host')
    command = 'mysql --local_infile=1 -u %s -p%s -h %s invis < %s_%s_table.sql'%(user,passwd,host,action,tablename)
    print command
    os.system(command)    
def exit_if_running(prog = 'twitter_stream_scraper.py -k'):
    command = """ps -ef | grep -v grep | grep '%s' > curr_running"""%prog
    os.system(command)
    inst = 0
    for line in file('curr_running').readlines():
	if prog in line: inst += 1
    if inst >  1:
	print 'The program is currently running:',line
	sys.exit(0)
def write_sh_file(action='stream-with-keywords'):
    if action == 'stream-with-keywords':
	out = open("twitter_stream_with_keywords.sh", 'w') # all the commands will go here
	out.write("""
	#!/bin/sh
	COMMENT=
	codepath="$HOME/code/twitter_olympic/src"
	lpython="$HOME/env/bin/python"

	cd $codepath
	$lpython twitter_stream_scraper.py -k
	""")
	out.close()
    if action == 'update-tweets-table':
	out = open("twitter_update_tweets_table.sh", 'w') # all the commands will go here
	out.write("""
	#!/bin/sh
	COMMENT=
	codepath="$HOME/code/twitter_olympic/src"
	lpython="$HOME/env/bin/python"

	cd $codepath
	$lpython twitter_stream_scraper.py -u
	""")
	out.close()


# sampling is with replacement
# @see: http://stackoverflow.com/questions/2140787/select-random-k-elements-from-a-list-whose-elements-have-weights/2149533#2149533
def weighted_sample(items, n):
    import random
    total = float(sum(w for w, v in items))
    i = 0
    w, v = items[0]
    while n:
        x = total * (1 - random.random() ** (1.0 / n))
        total -= x
        while x > w:
            x -= w
            i += 1
            w, v = items[i]
        w -= x
        yield v
        n -= 1
# items = [(10, "low"),
#          (100, "mid"),
#          (890, "large")]
# for v in weighted_sample(items,3): print v

def rgb2hex(rgb,base=1):
    r,g,b = rgb
    hexchars = "0123456789ABCDEF"
    s = '#'
    for c in [r,g,b]:
	c = int(c*base)
        s += hexchars[c / 16] + hexchars[c % 16]
    return s
def hex2rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16)/255.0 for i in range(0, lv, lv/3))


import math,numpy
def cosine_distance(u,v):
    return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v))) 

from math import sqrt, sin, cos, pi, asin, acos
def distance_lat_lng( lat_lng1, lat_lng2 ):
    """return distance along earth between two lat/lng pairs, in km"""
    lat1,lng1 = [l*pi/180 for l in lat_lng1]
    lat2,lng2 = [l*pi/180 for l in lat_lng2]
    dlat,dlng = lat1-lat2, lng1-lng2
    ds = 2*asin(sqrt( sin(dlat/2.0)**2 + cos(lat1)*cos(lat2)*sin(dlng/2.0)**2 ))
    return 6371.01*ds # spherical earth...
