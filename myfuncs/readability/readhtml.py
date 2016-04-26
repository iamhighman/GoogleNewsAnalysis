#!/usr/bin/env python

'''
ReadHtml.py - read text and links via readability

@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Dec 23, 2010
@TODO:
[2012.08.10] check the readability gits to see if the bugs in readability.py summary() are fixed

'''
import getopt,sys,os
import ConfigParser
from readability import Document
import urllib
from BeautifulSoup import BeautifulSoup,BeautifulStoneSoup
import HTMLParser
import nltk
import logging
logging.disable(logging.ERROR)

class ReadHtml():
    def __init__(self,config_file='config.txt',get_entrylinks=True,make_html=False,clean_html=True):
        # get_entrylinks: return a set of embedded hyperlinks on the page
        # make_html: return text in html or plain format
        # clean_html: clean html tags from text
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.get_entrylinks=get_entrylinks
        self.make_html=make_html
        self.clean_html=clean_html
    def __del__(self): pass
    def test(self): pass
    def test1(self):
        url = 'http://firstread.msnbc.msn.com/_news/2010/12/21/5689395-the-do-something-congress'
        file = urllib.urlopen(url)
        text = '<html>\n'+ \
            Document(file.read()).summary().encode('ascii','ignore') + \
            '\n</html>'
        #text = nltk.util.clean_html(text)
        ofilename = 'test.html'
        ofile = open(ofilename, 'w')
        ofile.write(text)
        ofile.close()
    def read(self,data=None,filename=None,url=None,):
        doc=None
        title,text,links=None,None,None
        if data:
            doc = Document(data,debug=False)
        elif filename:
            try:
                file = open(filename,'r')
                doc = Document(file.read(),debug=True)
                file.close()
            except: pass
        elif url:
            try:
                file = urllib.urlopen(url)
                doc = Document(file.read(),debug=True)
		# print doc.summary() #.encode('ascii','ignore')
                file.close()
            except: pass
        if doc:
            try:
                title = doc.title().encode('ascii','ignore')
            except:
                log= 'Unparseable title: %s'%doc
                #sys.stderr.write('Error: (readhtml) %s\n'%(log))
            try:
                text = doc.summary().encode('ascii','ignore')
            except:
                log= 'Unparseable text: %s'%doc
                #sys.stderr.write('Error: (readhtml) %s\n'%(log))
	    # NOTE: there seems blugs inside doc.summary(), but doc.content() would return everything in html including the banner and side-bars
	    # @TODO: check the readability gits to see if the bugs are fixed
	    # if not text or text=='':
	    # 	try:
	    # 	    text = doc.content().encode('ascii','ignore')
	    # 	except:
	    # 	    log= 'Unparseable text: %s'%doc
            
            if text:
                log= 'Parseable text: <<%s>>\n'%(title)
                #sys.stderr.write('\n%s'%(log))
                #sys.stderr.write('\n**********\n %s \n**********\n'%(log))
                if self.get_entrylinks: links = self.get_links(text)
                if self.clean_html:
		    try: text = nltk.util.clean_html(text)
		    except: text = ''
                    #sys.stderr.write('\n%s'%(text))
                if self.make_html: text = '<html>\n<h1>' + title + '</h1>\n' + text + '\n</html>' # for readability later
        else:
            log= 'no doc object!'
            #sys.stderr.write('Error: (readhtml) %s\n'%(log))

        #print title,text,links
        return title,text,links
    def get_links(self,text):
        links=set()
        try:
            bss = BeautifulSoup(text)
        except HTMLParser.HTMLParseError,e:
            log = 'Error: %s' % e
            print log
            return
        
        children = bss.findAll('a')
        #print 'retrieving %d links...' % len(children)
        for child in children:
            #print child
            if child.has_key('href'):
                link = child['href']
		if not link or len(link)==0: continue
                if link.startswith('/') or link.lower().startswith('javascript'): continue
                #log= '%s'%link
                #sys.stderr.write('link found: (readhtml) %s\n'%(log))
                links.add(link)
            else:
                log= '%s'%child
                #sys.stderr.write('link not found: (readhtml) %s\n'%(log))
        return links
def run(opt):
    h = ReadHtml()
    opt=int(opt)
    if opt==0:
        h.test()
        print 'test ok!'
    elif opt==1: h.test1()
    # elif opt==2: h.read(url='http://firstread.msnbc.msn.com/_news/2010/12/21/5689395-the-do-something-congress')
    elif opt==2:
        # title,text,links = h.read(url='http://www.house.gov')
	url = 'http://www.dustbury.com/archives/11782'
	url = 'http://www.gfsnews.com/article/756/1/Democrats__plea_to_Fed_on_foreclosures'
	content = ''
        title,text,links = h.read(url=url)
        print title
        raw_input('.')
        print text
        raw_input('.')
        print links
    else: return False
    return True
def usage():
    prog = os.path.basename(sys.argv[0])
    print '''
    Usage: python %s -c<opt>
        -c0 show testing results
    '''%prog    
def main(argv):
    res=False
    try:
        opts, args = getopt.getopt(argv[0:], 'c:')
        for o, a in opts:
            if o == "-c":
                res=run(a)
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if not res: usage()
if __name__ == '__main__':
    main(sys.argv[1:])    
