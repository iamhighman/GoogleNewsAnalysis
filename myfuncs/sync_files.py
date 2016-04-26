#!/usr/bin/env python

'''
sync_files.py - if the local file does not exist, get the files from remote server (ach|rce|erz|kni|..)

@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Aug 11, 2012

'''

import sys,os

def get_remote_file(src_host='iq',
		    src_path='../pubstatements/sample_text/sample1000/ngram_freq_with_offset0.csv',
		    dst_path='../pubstatements/sample_text/sample1000/',
		    proj_name='invis',
		    verbose=True):
    if verbose:
	if os.path.exists(src_path): print 'File exists: %s'%src_path
	else: print 'File not found: %s'%src_path
    src_path = src_path.replace('..',proj_name)
    if src_host in ['ach']:
	src = 'yuru@achtung.ccs.neu.edu:~/code/%s'%(src_path)
    elif src_host in ['iq','iqss','rce']:
	src = 'yurulin@rce.hmdc.harvard.edu:/nfs/home/Y/yurulin/shared_space/yurulin/code/%s'%(src_path)
    elif src_host in ['kni']:
	src = 'yuru@knightmare.no-ip.org:~/code/%s'%(src_path)
    if src_host in ['erz']:
	src = 'yuru@erzsebet.neu.edu:~/code/%s'%(src_path)
    if src_host in ['gin']:
	src = 'yuru@ginestra.neu.edu:~/code/%s'%(src_path)
    command = 'rsync -av --progress %s %s'%(src,dst_path)
    if verbose:
	inchar = raw_input('Press any key to get remote file or (n|N) to skip:\n%s\n'%(command))
	if inchar in ['n','N']: return
	# print command
    os.system(command)
def put_remote_file(dst_host='iq',
		    src_path='../pubstatements/sample_text/sample1000/ngram_freq_with_offset0.csv',
		    dst_path='../pubstatements/sample_text/sample1000/',
		    proj_name='invis',
		    verbose=True):
    if not os.path.exists(src_path):
	print 'Error - file not found: %s'%src_path
	return
    dst_path = dst_path.replace('..',proj_name)
    if dst_host in ['ach']:
	dst = 'yuru@achtung.ccs.neu.edu:~/code/%s'%(dst_path)
    elif dst_host in ['iq','iqss','rce']:
	dst = 'yurulin@rce.hmdc.harvard.edu:/nfs/home/Y/yurulin/shared_space/yurulin/code/%s'%(dst_path)
    elif dst_host in ['kni']:
	dst = 'yuru@knightmare.no-ip.org:~/code/%s'%(dst_path)
    if dst_host in ['erz']:
	dst = 'yuru@erzsebet.neu.edu:~/code/%s'%(dst_path)
    command = 'rsync --progress %s %s'%(src_path,dst)
    if verbose:
	inchar = raw_input('Press any key to put remote file or (n|N) to skip:\n%s\n'%(command))
	if inchar in ['n','N']: return
	# print command
    os.system(command)

def main(argv):
    get_remote_file()
if __name__ == '__main__': 
    main(sys.argv[1:])
