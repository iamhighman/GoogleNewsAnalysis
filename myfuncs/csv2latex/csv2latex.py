#!/usr/bin/env python
#coding=utf-8
'''
csv2latex.py - generate latex table from csv file
    the code is modified from http://neuroscience.telenczuk.pl/?p=252
    Usage:
	sys.path.append('../../myfuncs/csv2latex'); from csv2latex import csv2latex
	ifilename = 'somefile.csv'
	csv2latex(ifilename=ifilename,ofilename='somefile.tex',outputpath='../output/tab',do_pdf=True)
@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Jul 29, 2012
@dependency: django.template
'''


import django
from django.template import Template, Context
import csv,os
from datetime import datetime
django.conf.settings.configure()

def csv2latex(ifilename='names.csv',ofilename='table.tex',outputpath='.',alignment_str='lc',
	      digit=3,rotated=False,font_spec='', #'\\tiny',	      
	      table_label='tab:phonebook',table_caption='Simple Phonebook',author='Yu-Ru Lin',
	      header = None,
	      do_pdf=True):
    # This line is required for Django configuration
    # django.conf.settings.configure()
    cur= os.path.dirname(__file__)
    if cur=='': cur = '.'
    template_filename='%s/table_template.tex'%(cur)
    if rotated: template_filename='%s/table_sideway_template.tex'%(cur)

    # Open and read CSV file
    fid = open(ifilename,'r')
    reader = csv.reader(fid)
    rows = []
    for fields in reader:
	fields = [s.replace('_','\_') for s in fields]
	row = []
	for col in fields:
	    try:
		if col.isdigit(): row.append(col)
		else:
		    v = float(col)
		    fmt = '%%6.%df'%digit
		    v = fmt%v #round(v,digit)
		    row.append(v)
	    except: row.append(col)
	rows.append(row)
    fid.close()
    tmpfilename = 'tmp.csv'
    ofile = open(tmpfilename, "w")
    writer = csv.writer(ofile,delimiter=',',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    ofile.close()
    # print 'save to',ofilename
    fid = open('tmp.csv','r')
    reader = csv.reader(fid)
   
    # Open and read template
    with open(template_filename) as f:
        t = Template(f.read())
   
    # Define context with the table data
    if not header: header = reader.next()
    n_fields = len(header)
    while len(alignment_str)<n_fields: alignment_str += 'c'
    c = Context({"head": header, "table": reader,
		 'alignment_str': alignment_str,'font_spec': font_spec,
		 'table_label':table_label, 'table_caption': table_caption,
		 'author':author,'date':datetime.utcnow().strftime('%Y-%m-%d')})
    # from pprint import pprint
    # pprint(c['table'])

    # Render template
    output = t.render(c)

    fid.close()

    # Write the output to a file
    if not os.path.exists(outputpath): os.system('mkdir -p %s'%outputpath)
    ofilename_ = '%s/%s'%(outputpath,ofilename)
    with open(ofilename_, 'w') as out_f:
        out_f.write(output)
    if do_pdf:
	from glob import glob
	ofile_prefix = ofilename.replace('.tex','.')
	command = 'cd %s; mylatex %s pdf'%(outputpath,ofile_prefix)
	os.system(command)
	rm_files = glob('%s/%s*'%(outputpath,ofile_prefix))
	for f in rm_files:
	    if '.tex' in f or '.pdf' in f or '.csv' in f: continue 
	    command = 'rm %s'%f
	    print command
	    os.system(command)

if __name__ == "__main__":
    csv2latex(ofilename='table.tex',outputpath='tmp')

