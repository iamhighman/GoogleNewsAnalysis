import time
from operator import itemgetter
from datetime import datetime

def save(list,filename='output.m'):
    outfile = file(filename,'w')
    for e in list:
        outfile.write(str(e)+'\n')
    outfile.close()
def savelist2spmat(m,filename='output.m'):
    if m==None: return
    outfile = file(filename,'w')
    d1=len(m)
    d2=len(m[0])
    print 'matrix size:',d1,d2
    for i in range(d1):
        for j in range(d2):
            if m[i][j] != 0:
                outfile.write(str(i+1)+' '+str(j+1)+' '+str(m[i][j])+'\n')
    outfile.close()
    
# save as sparse matrix
def saves(dictlist,filename='output.m'):
    outfile = file(filename,'w')
    cnt = 1
    for k,v in dictlist.items():
        for e in v:
            outfile.write(str(cnt)+' '+str(e)+' 1 \n')
        cnt += 1
    outfile.close()
def save_mat(dictlist,filename='output.m')  :  
    outfile = file(filename,'w')
    for k,v in dictlist.items():
        for e in v:
            outfile.write(str(k)+' '+str(e)+' 1 \n')
    outfile.close()
# print keys to file, sorted by values    
def save_dict_key_index(dictlist,filename='output.m'):
    outfile = file(filename,'w')
    # items sorted by value
    elist = sorted(dictlist.items(), key=itemgetter(1), reverse=False)
    for e in elist:
        outfile.write(str(e[0])+'\n')
    outfile.close()
# print keypairs to file, sorted by values    
def save_dict_keypair_index(dictlist, whichkey,filename='output.m'):
    outfile = file(filename,'w')
    # items sorted by value
    elist = sorted(dictlist.items(), key=itemgetter(1), reverse=False)
    for e in elist:
        if whichkey == 'both':
            outfile.write(str(e[0][0])+' '+str(e[0][1])+'\n')
        else:
            outfile.write(str(e[0][whichkey])+'\n')
    outfile.close()
def save_dict_key_value(dictlist, filename='output.m'):
    outfile = file(filename,'w')
    # items sorted by value
    elist = sorted(dictlist.items(), key=itemgetter(1), reverse=False)
    for e in elist:
        outfile.write(str(e[0])+' '+str(e[1])+'\n')
    outfile.close()

def datenum(timestr,unit='day'):
    if timestr == 0: return 0 # for t-infinity
    if len(timestr)>10:timestr = timestr[0:10]
    basetime = '1970-01-01'
    t0 = time.strptime(basetime,"%Y-%m-%d")
    t = time.strptime(timestr,"%Y-%m-%d")
    if t < t0: t=t0
    diff = time.mktime(t)-time.mktime(t0)
    if unit == 'day':
        diff /= (60.0*60*24)
        diff += 719529
        # matlab starts from 0000-01-01, while python starts from 1970-01-01
    elif unit == 'hour':
        diff /= (60.0*60)
    else:
        diff /= 60.0
    return diff
def datestr(timenum,unit='day'):
    basetime = '1970-01-01'
    t0 = time.strptime(basetime,"%Y-%m-%d")
    if unit == 'day':
        timenum -= 719529
        timenum *= (60.0*60*24)
    timenum += time.mktime(t0)
    return datetime.fromtimestamp(timenum).strftime("%Y-%m-%d")
if __name__ == '__main__':
    print datenum('2008-05-03 22:12:00')
    print datestr(733531)
