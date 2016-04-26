#!/usr/bin/env python
from datetime import datetime
from datetime import timedelta
import matlab
import pprint
import time
#import md5
import math
import random
import numpy
#import pylab

def parse_timestr(str):
    return datetime.strptime(str[0:19], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    # note: the parser doesn't take care of timezone, TODO in the future
def get_timestr(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")
    
def timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
def timestampT():
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
def today():
    return datetime.utcnow().strftime("%Y-%m-%d")
def yesterday():
    t = timedelta(1)
    t = datetime.utcnow() - t
    return t.strftime("%Y-%m-%d")

def list2text(l):
    text = ''
    for u in l: text += u + ' '
    return text

def savelog(filename, text):
    logfile = file(filename, 'a')
    s = "[%s] %s\n" % (timestamp(),text)
    logfile.write(s)
    logfile.close()
    
def timeslots(tstart='2004-01-19',tend='2004-04-01',windowsize='weekly',init=0):
    tstarts = tstart
    tends = tend
    tstart = datetime.strptime(tstarts,"%Y-%m-%d")
    tend = datetime.strptime(tends,"%Y-%m-%d")
    ystart = int(tstart.strftime("%Y"))
    yend = int(tend.strftime("%Y"))
    mstart = int(tstart.strftime("%m"))
    mend = int(tend.strftime("%m"))
    slots = {}
    slots_ = []
    if windowsize == 'yearly':
        for y in range(ystart,yend+1):
            startstr = '%d-01-01' % (y)
            endstr = '%d-12-31' % (y)
            ts = matlab.datenum(startstr)
            te = matlab.datenum(endstr)
            if init == 0:
                slots.setdefault((ts,te),len(slots)+1)
            elif init == 'dict':
                slots[(ts,te)] = {}
            elif init == 'list':
                slots[(ts,te)] = []
            slots_.append(ts)
        matlab.save(slots_,'output\slots_yearly.m')
    if windowsize == 'monthly':
        for y in range(ystart,yend+1):
            for m in range(1,13):
                if y == ystart and m < mstart: continue
                if y == yend and m > mend: continue
                startstr = '%d-%d-01' % (y,m)
                endstr = '%d-%d-01' % (y,m+1)
                if m == 12:
                    endstr = '%d-01-01' % (y+1)
                ts = matlab.datenum(startstr)
                te = matlab.datenum(endstr)
                if init == 0:
                    slots.setdefault((ts,te),len(slots)+1)
                elif init == 'dict':
                    slots[(ts,te)] = {}
                elif init == 'list':
                    slots[(ts,te)] = []
                slots_.append(ts)
        matlab.save(slots_,'output\slots_monthly.m')
    if windowsize == 'quarterly':
        #print mstart,mend
        for y in range(ystart,yend+1):
            for q in range(1,5):
                mq_start=(q-1)*3+1
                mq_end=q*3+1
                #print y,mq_start,mq_end
                if y==ystart and mstart>=mq_end:continue
                if y==yend and mend<mq_start:continue
                startstr = '%d-%d-01' % (y,mq_start)
                endstr = '%d-%d-01' % (y,mq_end)
                if mq_end > 12: endstr = '%d-01-01' % (y+1)
                #print startstr,endstr
                ts = matlab.datenum(startstr)
                te = matlab.datenum(endstr)
                if init == 0:
                    slots.setdefault((ts,te),len(slots)+1)
                elif init == 'dict':
                    slots[(ts,te)] = {}
                elif init == 'list':
                    slots[(ts,te)] = []
                slots_.append(ts)
        matlab.save(slots_,'output\slots_quarterly.m')
    if windowsize == 'weekly':
        sn = matlab.datenum(tstarts)
        en = matlab.datenum(tends)
        ts = sn
        while ts <= en:
            te = ts + 7
            slots.setdefault((ts,te),len(slots)+1)
            slots_.append(ts)
            ts = te
        matlab.save(slots_,'output\slots_weekly.m')
    if windowsize == 'daily':
        sn = matlab.datenum(tstarts)
        en = matlab.datenum(tends)
        ts = sn
        while ts <= en:
            te = ts + 1
            slots.setdefault((ts,te),len(slots)+1)
            slots_.append(ts)
            ts = te
        matlab.save(slots_,'output\slots_dailyly.m')
    if windowsize == '2daily':
        sn = matlab.datenum(tstarts)
        en = matlab.datenum(tends)
        ts = sn
        while ts <= en:
            te = ts + 2
            slots.setdefault((ts,te),len(slots)+1)
            slots_.append(ts)
            ts = te
        matlab.save(slots_,'output\slots_2dailyly.m')
    if windowsize == '3daily':
        sn = matlab.datenum(tstarts)
        en = matlab.datenum(tends)
        ts = sn
        while ts <= en:
            te = ts + 3
            slots.setdefault((ts,te),len(slots)+1)
            slots_.append(ts)
            ts = te
        matlab.save(slots_,'output\slots_3dailyly.m')
    #pprint.pprint(slots)
    return slots
    
def get_timeslot(slots,t):
    #pprint.pprint(slots)
    for k,v in slots.items():
        if t>=k[0] and t<=k[1]: return k
    # if key not found
    print t,slots
    for k,v in slots.items():
        return k
    #return None
def timestr2timeslot(slots,ts):
    t = matlab.datenum(ts)
    t = int(math.floor(t))
    sk = get_timeslot(slots,t)
    return t,slots[sk]
def time2timeslot(slots,t):
    t = matlab.datenum(t.strftime("%Y-%m-%d"))
    t = int(math.floor(t))
    sk = get_timeslot(slots,t)
    return t,slots[sk]
def timestamp2timeslot(slots,t):
    t = int(math.floor(t))
    sk = get_timeslot(slots,t)
    return t,slots[sk]
def time2timestamp(t):
    return matlab.datenum(t.strftime("%Y-%m-%d"))

def save_lists(lines, filename):
    outfile = file(filename,'wb')
    for line in lines:
        for col in line:
            outfile.write(str(col)+' ')
        outfile.write('\n')
    outfile.close()

def save_lists2spmat(lines, filename):
    outfile = file(filename,'wb')
    for line in lines:
        outfile.write(str(line[0])+' '+str(line[1])+' 1\n')
    outfile.close()

def md5str(str):
    import md5
    m=md5.new(str.encode('utf8'))
    return m.hexdigest()
def keys2dict(filename):
    ids = file(filename,'r').readlines()
    iddict={}
    for i in ids: iddict[i.strip()]=len(iddict)+1
    #uiddict=dict(zip(uids,xrange(1,len(uids))))
    print len(ids),len(iddict),'from',filename
    return iddict
def combokeys2dict(filename):
    ids = file(filename,'r').readlines()
    iddict={}
    for i in ids: iddict[i.strip().split()[0].strip()]=len(iddict)+1
    #uiddict=dict(zip(uids,xrange(1,len(uids))))
    print len(ids),len(iddict),'from',filename
    return iddict

def sleep_random(min_sec=30,duration_sec=60):
    sec = duration_sec* random.random()+min_sec
    print 'sleep %d seconds...' % sec
    time.sleep(sec)
    
EXTRACT_DECODABLE_TEXT = True # remove token if it's not decodable
REMOVE_N = True # remove \t or \n etc. but keep a whitespace between tokens
def encode_str(s):
    if s==None: return s
    if REMOVE_N: toks = s.split()
    else: toks = s
    s=""
    for tok in toks:
        
        try:
            t=tok.encode('utf-8')
            utxt = unicode(t) # force decode
            t = utxt
            if REMOVE_N: s=s+' '+t #keep a whitespace between tokens
            else: s=s+t
        except UnicodeDecodeError, e:
            text= 'UnicodeDecodeError: %s %s' %  (e,tok)
            #print text  
    return s

def try_encode_str(s):
    try:
        return s.encode("utf-8")
    except UnicodeEncodeError, e:
        tokens = s.split()
        clean_tokens = []
        for tok in tokens:
            try:
                clean_tokens.append(tok.encode('utf-8'))
            except UnicodeEncodeError, e:
                log= 'UnicodeEncodeError: %s %s' %  (e,tok)
                print log
        s1 = ' '.join(clean_tokens)
        return s1

def flatten(x):
    #http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def plot_dictlist(dictlist,cutoff=50,cumulative=True,title='test',xlabel='Samples',ylabel='Frequency'):
    from operator import itemgetter
    # sort by value in decreasing order
    samples = sorted(dictlist.items(), key=itemgetter(1), reverse=True)[:cutoff]
    samples = [k for k,v in samples]
    values = [dictlist[k] for k in samples]
    if cumulative:
        values = get_cumulative_values(values)
        ylabel='Cumulative Percentage'
    else:
        ylabel = 'Frequency Count'
    plot_freq_dist(samples,values,title=title,xlabel=xlabel,ylabel=ylabel)
def plot_pairlist(pairlist,cutoff=50,cumulative=True,title='test',xlabel='Samples',ylabel='Frequency'):
    samples = [k for (k,v) in pairlist][:cutoff]
    values = [v for (k,v) in pairlist][:cutoff]
    if cumulative:
        values = get_cumulative_values(values)
        ylabel='Cumulative Percentage'
    else:
        ylabel = 'Frequency Count'
    plot_freq_dist(samples,values,title=title,xlabel=xlabel,ylabel=ylabel)
def get_cumulative_values(values):
    N = max(1e-9,sum(values))
    return [sum(values[:i+1]) * 1.0/N for i in range(len(values))]
def get_normalized_values(values):
    values = numpy.array(values)
    N = sum(values)*1.0
    return values/N
def plot_freq_dist(samples,values,title='test',xlabel='Samples',ylabel='Frequency',filename=None):
    import pylab
    pylab.hold(False)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.grid(True, color="silver")
    pylab.plot(values)
    if samples!=[]:
        pylab.xticks(range(len(samples)), [str(s) for s in samples], rotation=90)
    pylab.xlim(0,len(values))
    
    if filename!=None:
        pylab.savefig(filename)
    else: pylab.show()
    
def plot_lists(lists,cutoff=50,cumulative=True,title='test',xlabel='Samples',ylabel='Frequency'):
    # assume input lines are stored in dict, all samples are in (decreasing) order
    import pylab
    names = lists.keys()
    N=0
    lines = {}
    for name in names:
        samples = [k for (k,v) in lists[name]][:cutoff]
        values = [v for (k,v) in lists[name]][:cutoff]
        N+=sum(values)
        lines[name] = {'samples':samples,'values':values}
    if cumulative:
        for name in names:
            values = lines[name]['values']
            values = [sum(values[:i+1]) * 100.0/N for i in range(len(values))]
            lines[name]['values']=values
    for name in names:
        pylab.plot(lines[name]['values'],label=name)
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.grid(True, color="silver")
    #pylab.plot(values)
    pylab.xticks(range(len(samples)), [str(s) for s in samples], rotation=90)
    pylab.legend(loc='lower right') 
    pylab.show()
    
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
    for a in x:
        std = std + (a - mean)**2
    if n<=1: std=0
    else: std = sqrt(std / float(n-1))
    return mean, std

def plotrank(samples,errors=None,**kwargs):
    import pylab,numpy as np
    samples = sorted(samples)
    y = np.array(range(0,len(samples)))*1.0/len(samples)
    x = samples
    max_e = max(np.array(errors))
    color=kwargs['color']
    if errors:
        for xi,yi,err in zip(x,y,errors):
            s=max_e-err
            #pylab.plot(xi,yi,marker='s',color='r',mfc='r',mec='None',markersize=s,alpha=0.1)
            #cir = pylab.Circle((xi,yi),radius=s,fc='r',ec='r',alpha=0.1)
            #pylab.gca().add_patch(cir)
            pylab.plot([xi-s,xi+s],[yi,yi],'.',color=color,mfc=color,mec=color,markersize=4,alpha=0.1)
            pylab.hold(True)
    pylab.plot(x,y,':',color=color)
    #pylab.show()
    
# from plfit
def plotpdf(x=None,xmin=None,alpha=None,nbins=50,dolog=True,dnds=False,**kwargs):
    """
    Plots PDF and powerlaw.
    """
    #if not(x): x=self.data
    #if not(xmin): xmin=self._xmin
    #if not(alpha): alpha=self._alpha
    import numpy,pylab
    import numpy.random as npr
    from numpy import log,log10,sum,argmin,argmax,exp,min,max

    x=numpy.sort(x)
    n=len(x)

    pylab.gca().set_xscale('log')
    pylab.gca().set_yscale('log')

    if dnds:
        hb = pylab.histogram(x,bins=numpy.logspace(log10(min(x)),log10(max(x)),nbins))
        h = hb[0]
        b = hb[1]
        db = hb[1][1:]-hb[1][:-1]
        h = h/db
        pylab.plot(b[:-1],h,drawstyle='steps-post',color='k',**kwargs)
        #alpha -= 1
    elif dolog:
        hb = pylab.hist(x,bins=numpy.logspace(log10(min(x)),log10(max(x)),nbins),log=True,fill=False,edgecolor='k',**kwargs)
        alpha -= 1
        h,b=hb[0],hb[1]
        pylab.hold(False)
        pylab.loglog(b[1:],h,'o',mfc="None",mec='blue')
        pylab.hold(True)
    else:
        hb = pylab.hist(x,bins=numpy.linspace((min(x)),(max(x)),nbins),fill=False,edgecolor='k',**kwargs)
        h,b=hb[0],hb[1]
    b = b[1:]

    q = x[x>=xmin]
    px = (alpha-1)/xmin * (q/xmin)**(-alpha)

    arg = argmin(abs(b-xmin))
    plotloc = (b>xmin)*(h>0)
    norm = numpy.median( h[plotloc] / ((alpha-1)/xmin * (b[plotloc]/xmin)**(-alpha))  )
    px = px*norm

    pylab.loglog(q,px,'r',label=('$x_{min}=%.1f$, $\\alpha=%.2f$'%(xmin,alpha)),**kwargs)
    pylab.legend()
    #pylab.vlines(xmin,0.1,max(px),colors='r',linestyle='dashed')
    
    pylab.gca().set_xlim(min(x),max(x))