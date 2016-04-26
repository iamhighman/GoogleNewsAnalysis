#!/usr/bin/env python
import sys
import time
clearScreen='\x1b[H\x1b[2J'
Verbose = False

def remote_func1(chan,jobcnt,jobsetting):
    if Verbose: sys.stderr.write('   channel-%s-%d: %s\n'%(chan,jobcnt,jobsetting['func']))
    secs=jobsetting['secs']
    log='sleep %d secs'%secs
    if Verbose: sys.stderr.write('   channel-%s-%d: %s\n'%(chan,jobcnt,log))
    time.sleep(secs)
    res={'msg':'[channel-%s-%d] complete %s'%(chan,jobcnt,log)}
    return res
def remote_func2(chan,jobcnt,jobsetting):
    if Verbose: sys.stderr.write('   channel-%s-%d: %s\n'%(chan,jobcnt,jobsetting['func']))
    secs=jobsetting['secs']
    log='sleep %d secs'%secs
    if Verbose: sys.stderr.write('   channel-%s-%d: %s\n'%(chan,jobcnt,log))
    time.sleep(secs)
    res={'msg':'complete %s'%(log)}
    return res
if __name__ == '__channelexec__':
    chan=channel.receive()    
    jobcnt=0
    for jobsetting in channel:
        if jobsetting==None:
            channel.send(None)
            break
        if Verbose: sys.stderr.write('>>>channel-%s-%d: %s\n'%(chan,jobcnt,jobsetting['func']))
        # do the job -----
        res=eval('%s(chan,jobcnt,jobsetting)'%jobsetting['func'])
        # report back -----
        channel.send(res)
        jobcnt+=1
    #channel.send(None)
    if Verbose: sys.stderr.write('>>>channel-%s-%d: Ending: %s\n'%(chan,jobcnt,jobsetting))
    
