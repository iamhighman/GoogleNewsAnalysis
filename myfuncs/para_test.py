#!/usr/bin/env python

'''
para_test.py - the module is doing xyz

@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Dec 14, 2010
'''
import getopt,sys,os

import time,execnet
HOSTS={
    'localhost':2,'127.0.0.1':2
}
# cwd='/media/d/connect/barabasilab/polisci/src'
hostname = os.uname()[1]
if 'Mac' in hostname:
    # codepath='/Users/yuru/dh_myprojects/code'
    codepath='/Users/yuru/connect/yurugit'
    whichpython='/usr/bin/python'
    libpath=''
elif 'achtung' in hostname:
    codepath='/home/yuru/code'
    whichpython='/home/yuru/env/bin/python'
    libpath='' #'/home/yuru/env/local/lib/python2.7/site-packages:/home/yuru/env/lib/python2.7/site-packages'
    # libpath='/home/yuru/env/local/lib/python2.7/site-packages:/home/yuru/env/lib/python2.7/site-packages:/home/yuru/env/lib/python2.7/site-packages/csc_pysparse-1.1.1.4-py2.7-linux-x86_64.egg'
elif 'ginestra' in hostname:
    codepath='/home/yuru/code'
    whichpython='/home/yuru/local/bin/python'
    libpath = ''
elif 'rce' in hostname or 'jns' in hostname:
    codepath='/nfs/home/Y/yurulin/shared_space/yurulin/code'
    whichpython='/nfs/home/Y/yurulin/.pythonbrew/pythons/Python-2.7.3/bin/python'
    libpath=''
cwd='%s/myfunc'%codepath
libpath='%s:%s'%(libpath,cwd)
Verbose = False
def init_channels(jobname='some_remote_job_filename',hosts=HOSTS,cwd=cwd,libpath=libpath):
    print 'hosts:',hosts
    print 'cwd=',cwd
    print 'libpath=',libpath
    channels=[]
    for host,cnt in hosts.items():
	if Verbose: print 'opening %d gateways at %s'%(cnt,host)
        if host=='localhost' or host=='127.0.0.1':gatename='popen'
        else: gatename='ssh=%s'%host
        for i in range(cnt):
            gw = execnet.makegateway('''%s//chdir=%s//
                                     python=%s//
                                     env:PYTHONPATH=%s//
                                     env:EXECNET_DEBUG=2'''%(gatename,cwd,whichpython,libpath))
            ch = gw.remote_exec(jobname)
            ch.send(str(len(channels))) #send channel id
            channels.append(ch)
    return channels
def end_channels(channels,job_count,timeout=300000):
    multi = execnet.MultiChannel(channels)
    queue = multi.make_receive_queue()
    results = []
    for i in range(job_count):
        channel, res = queue.get(timeout=timeout)
	if Verbose: print '(%d/%d) response: %s ' %(i+1,job_count,res['msg'])
	results.append(res)
    return results
def init_group_channels(jobname='remote_exec',callback=None,hosts=HOSTS,cwd=cwd,libpath=libpath):
    print 'hosts:',hosts
    print 'cwd=',cwd
    print 'libpath=',libpath
    groups={}
    channels=[]
    for host,cnt in hosts.items():
        print 'opening %d gateways at %s'%(cnt,host)
        if host=='localhost' or host=='127.0.0.1':gatename='popen'
        else: gatename='ssh=%s'%host
        groups[host]=execnet.Group()
        for i in range(cnt):
            ch = groups[host].makegateway('''%s//chdir=%s//
                                     python=%s//
                                     env:PYTHONPATH=%s//
                                     env:EXECNET_DEBUG=2'''%(gatename,cwd,whichpython,libpath)).remote_exec(jobname)
            if callback!=None: ch.setcallback(callback,endmarker=None)
            ch.send(str(len(channels))) #send channel id
            channels.append(ch)
    return groups,channels
def callback_func(res):
    print 'callback:',res
    return
def test():
    import remo_test,random
    channels = init_channels(jobname=remo_test,hosts=HOSTS,cwd=cwd,libpath=libpath)
    job_count=0
    ch_id=0

    t0,t1=time.clock(),time.time()                            
    for i in range(10):
	secs = 20-i*2 #10* random.random()
	jobsetting={'func':'remote_func2','secs':secs}
	channels[ch_id].send(jobsetting)
	job_count+=1
	ch_id= (ch_id+1)%len(channels)

    end_channels(channels,job_count)
    log= 'elapsed: process time%.3f sec.; wall time %.3f sec.'%(time.clock()-t0,time.time()-t1)
    print log

def test1():
    import remo_test,random
    groups,channels = init_group_channels(jobname=remo_test,callback=callback_func,hosts=HOSTS,cwd=cwd,libpath=libpath)
    #print len(groups),len(channels)
    job_count,ch_id=0,0
    #for ch in channels: print ch
    t0,t1=time.clock(),time.time()                            
    for i in range(10):
	secs = 20-i*2 #10* random.random()
	jobsetting={'func':'remote_func1','secs':secs}
	channels[ch_id].send(jobsetting)
	#channels[ch_id].waitclose()
	job_count+=1
	ch_id= (ch_id+1)%len(channels)
    for ch in channels:
	if ch:
	    ch.send(None)
	    ch.waitclose()
    #for k,v in groups.items():
    #    v.terminate(timeout=1)
    log= 'elapsed: process time %.3f sec.; wall time %.3f sec.'%(time.clock()-t0,time.time()-t1)
    print log

    
def usage():
    print '''
    Usage: python classname.py -c<opt>
        -c0 show testing results
    '''    
def main(argv):
    test()
    #test1() # some bugs to be fixed!
    
if __name__ == '__main__':
    main(sys.argv[1:])    
