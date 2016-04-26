import nltk,sys,re
from nltk.collocations import *
import myutil
from operator import itemgetter

def text2tokens(text,ngram=2):
    # the text has already been cleaned by export_pubstatement_to_clean_text.clean_text()
    words = text.split()
    text = []
    if ngram==1: text = words
    else:
	for token in nltk.ngrams(words,ngram):
	    token = ' '.join(token).strip()
	    text.append(token)
    # print text[0]
    return text

def clean_html(html, remove_entities=False,remove_links=True):
    p = re.compile("<(script|style).*?>.*?</(script|style)>", re.DOTALL)
    cleaned = re.sub(p, " ", html)               # remove inline js/css
    cleaned = re.sub("<(.|\n)*?>", " ", cleaned) # remove remaining html tags
    if remove_entities: cleaned = re.sub("&[^;]*; ?", "", cleaned)
    if remove_links:
	cleaned = re.sub('http://[^ ]*', " ", cleaned)
	cleaned = re.sub('[^ ,]*house.gov[^ ,]*', " ", cleaned)
	cleaned = re.sub('[^ ,]*senate.gov[^ ,]*', " ", cleaned)
	cleaned = re.sub('www.[^ ,]*.com[^ ,]*', " ", cleaned)
    return cleaned
    
def get_tokens(text,verbose=False,nonalpharemoval=True,stopremoval=True,steming=False,functionalremoval=False):
    text = nltk.util.clean_html(text)
    if verbose: print 'get',len(text),'tokens'
    text = nltk.tokenize.word_tokenize(text)
    if verbose: print 'get',len(text),'tokens after tokenization'
    if nonalpharemoval:
        text = [w.lower() for w in text if w.isalpha()]
        if verbose: print 'get',len(text),'tokens after removing non-alphabets'
    if stopremoval:
        stopwords = nltk.corpus.stopwords.words('english')
        text = [w for w in text if w not in stopwords]
        if verbose: print 'get',len(text),'tokens after removing stopwords'
    if functionalremoval:
        text = self.remove_functional(' '.join(text))
        text = nltk.tokenize.word_tokenize(text)
    if steming:
        stemer = nltk.PorterStemmer()
        text = [stemer.stem(w) for w in text]
    return text

#compile regexes as objects
hash_regex = re.compile(r'#[0-9a-zA-Z+_]*',re.IGNORECASE) 
user_regex = re.compile(r'@[0-9a-zA-Z+_]*',re.IGNORECASE)

def parse_tweet(tweet):
    # @see: http://fromzerotocodehero.blogspot.com/2010/12/parsing-tweets-links-users-and-hash.html
    #first deal with links. Any http://... string change to a proper link
    tweet = re.sub('http://[^ ,]*', lambda t: "link:%s" % (t.group(0)), tweet)
    tweet = re.sub('https://[^ ,]*', lambda t: "link:%s" % (t.group(0)), tweet)

    #for all elements matching our pattern...
    for usr in user_regex.finditer(tweet):
	#for each whole match replace '@' with ''
	url_tweet = usr.group(0).replace('@','user@')
	#in tweet's text replace text with proper link, now without '@'
	tweet = tweet.replace(usr.group(0),url_tweet)

    #do the same for hash tags
    for hash in hash_regex.finditer(tweet):
	url_hash = hash.group(0).replace('#','hash#')
	if len ( hash.group(0) ) > 2:
	    tweet = tweet.replace(hash.group(0),url_hash)
    return tweet
def is_special(w):
    if w.startswith('link:'): return True
    if w.startswith('user@'): return True
    if w.startswith('hash#'): return True
    return False
def get_tweet_tokens(text,verbose=False,nonalpharemoval=True,stopremoval=True,steming=False):
    text = parse_tweet(text)
    # text = nltk.util.clean_html(text)
    text = text.split() #nltk.tokenize.word_tokenize(text)
    if nonalpharemoval:
        text = [w.lower() for w in text if w.isalpha() or is_special(w)]
        if verbose: print 'get',len(text),'tokens after removing non-alphabets'
    if stopremoval:
        stopwords = nltk.corpus.stopwords.words('english')
	stopwords.append('rt')
        text = [w for w in text if w not in stopwords or is_special(w)]
        if verbose: print 'get',len(text),'tokens after removing stopwords'
    if steming:
        stemer = nltk.PorterStemmer()
        text = [stemer.stem(w) for w in text]
    return text
def recover_token(w):
    if w.startswith('link:http://'): w = w.replace('link:http://',':')
    elif w.startswith('link:https://'): w = w.replace('link:https://',':')
    elif w.startswith('user@'): w = w.replace('user@','@')
    elif w.startswith('hash#'): w = w.replace('hash#','#')
    return w
def concate_tweet_ngram(ngram):
    return " ".join(map(recover_token,ngram))
def concate_tweet_ngram_sent(ngram,s,threshold=0):
    w = " ".join(map(recover_token,ngram))
    if s>=threshold: w = '+%s'%(w)
    elif s<-threshold: w = '-%s'%(w)
    return w
    
def get_nltk_text_collection(docs,NGRAM=1):
    collection=[]
    alltext = []
    for doc_num,(doc_id, text) in enumerate(docs.iteritems()):
	sys.stdout.write("\r       \r")
	sys.stdout.write("%i" % (doc_num)); sys.stdout.flush()
	if NGRAM==1: words= text 
	else: words = [w for w in nltk.ngrams(text,NGRAM)]		
        collection.append(words)
	alltext.append(text)
    text = myutil.flatten(alltext)
    # print text[:10]
    collection = nltk.TextCollection(collection)
    return text,collection
def get_nltk_text_collection_by_les(docs,NGRAM=1):
    collection=[]
    lestext = {}
    alltext = []
    for doc_id, text in docs.items():
	if NGRAM==1: words=text
	else: words = [w for w in nltk.ngrams(text,NGRAM)]	
	# print doc_id
	les_id = doc_id.split(':')[0]
	lestext.setdefault(les_id,[])
	lestext[les_id].append(words)
	alltext.append(text)
    # print lestext.keys()
    for doc_id, tt in lestext.items():
	# print doc_id,myutil.flatten(tt)
	# raw_input('.')
        collection.append(myutil.flatten(tt))
    text = myutil.flatten(alltext)
    # print text[:10]
    collection = nltk.TextCollection(collection)
    return text,collection
def get_nltk_text_collection_by_time(docs,NGRAM=1):
    collection=[]
    lestext = {}
    alltext = []
    for doc_id, text in docs.items():
	if NGRAM==1: words=text
	else: words = [w for w in nltk.ngrams(text,NGRAM)]	
	# print doc_id
	les_id = doc_id.split(':')[1].replace('.csv','')
	lestext.setdefault(les_id,[])
	lestext[les_id].append(words)
	alltext.append(text)
    # print lestext.keys()
    for doc_id, tt in lestext.items():
	# print doc_id,myutil.flatten(tt)
	# raw_input('.')
        collection.append(myutil.flatten(tt))
    text = myutil.flatten(alltext)
    # print text
    collection = nltk.TextCollection(collection)
    return text,collection

def get_dist(va,vb,keys,metric='jaccard'):
    if metric=='jaccard':
        n=0
        d=1
        for k in keys:
            if k in va: na=va[k]
            else: na=0
            if k in vb: nb=vb[k]
            else: nb=0                
            n+=min([na,nb])
            d+=max([na,nb])
        #print n*1.0/d
        return n*1.0/d
    if metric=='ks':
        v1 = []
        v2 = []
        for k in keys:
            if k in va: na=va[k]
            else: na=0
            if k in vb: nb=vb[k]
            else: nb=0                
            v1.append(na)
            v2.append(nb)
        v1 = myutil.get_cumulative_values(v1)
        v2 = myutil.get_cumulative_values(v2)
        #print v1
        #raw_input('.')
        s=sum([abs(v1[i]-v2[i]) for i in range(len(v1))])/(.5*len(v1))
        #print s
        return s

def get_wordfreq_lists(lists,topwords):
    for k,v in lists.items():
        freqdist = nltk.FreqDist(v)
        freqcnts = dict(freqdist.items())
        lists[k]={}
        for w in topwords:
            if w in freqcnts: lists[k][w]=freqcnts[w]
    return lists
def get_sim_matrix(names,lists,topwords):
    D={}
    for i,a in enumerate(names):
        if a not in lists: continue
        va = lists[a]
        for j,b in enumerate(names):
            if i<=j: continue
            if b not in lists or a==b: continue
            vb = lists[b]
            D.setdefault(a,{})
            D[a][b]=get_dist(va,vb,topwords)
    return D

def get_top_ngrams(text,collection,NGRAM=2,cutoff=100,df_cutoff=3,do_tfidf=False,remove_web_stopwords=True):
    bigs = nltk.ngrams(text,NGRAM)
    print 'totally',len(bigs),'bigrams'
    if remove_web_stopwords: bigs = remove_website_stopwords(bigs)
    freqdist = nltk.FreqDist(bigs)
    topwords = freqdist.keys()[:cutoff]
    print len(topwords),'topwords:',topwords[:10],freqdist[topwords[0]],freqdist[topwords[1]]
    if do_tfidf:
        _cutoff=10000
        _topwords = freqdist.keys()[:_cutoff]
        tfidfs = {}
	idf = {}
        for w in _topwords:
            # print w
            tfidf_score = collection.tf_idf(w,bigs)
            tfidfs[w]=tfidf_score
	    idf[w] = collection.idf(w,bigs)
        #get sorted words in decreasing order of tfidf values
        sortedwords = sorted(tfidfs.items(), key=itemgetter(1), reverse=True) 
        sortedwords = sortedwords[:cutoff]
        topwords = [w for w,s in sortedwords]
        print 'TF-IDF topwords:'
        print len(topwords),'topwords:',sortedwords[:10],freqdist[topwords[0]],freqdist[topwords[1]]
        return topwords,freqdist,idf
    else:
	sortedpairs = sorted(freqdist.items(), key=itemgetter(1), reverse=True)
	topwords = [w for w,c in sortedpairs]
	topwords = [w for w in topwords if not 'http' in w]
        print 'Frequent topwords:'
        print len(topwords),'topwords:',topwords[:10],freqdist[topwords[0]],freqdist[topwords[1]]
	topwords = topwords[:cutoff]
    return topwords,freqdist,None
def get_top_ngrams_tfidf(text,collection,NGRAM=2,cutoff=100,docs=None):
    bigs = nltk.ngrams(text,NGRAM)
    print 'totally',len(bigs),'bigrams'
    bigs = remove_website_stopwords(bigs)
    freqdist = nltk.FreqDist(bigs)
    topwords = freqdist.keys()[:cutoff]
    # print len(topwords),'topwords:',topwords[:30],freqdist[topwords[0]],freqdist[topwords[1]]
    from math import log
    if True: #do_tfidf
	df = {}
	df_les = {}
	df_time = {}
	tfidf ={}
	for doc_id, text in docs.items():
	    words = [w for w in nltk.ngrams(text,NGRAM)]
	    les_id,time_id = doc_id.split(':')
	    time_id = time_id.replace('.csv','')
	    time_id = time_id[0:8]
	    for w in words:
		df.setdefault(w,set())
		df[w].add(doc_id)
		df_les.setdefault(w,set())
		df_les[w].add(les_id)
		df_time.setdefault(w,set())
		df_time[w].add(time_id)
        _cutoff=10000
        _topwords = freqdist.keys()[:_cutoff]
	df0,df1,df2={},{},{}
        for w in _topwords:
            # print w
	    try: df0[w] = len(df[w])
	    except: df0[w] = 0
	    try: df1[w] = len(df_les[w])
	    except: df1[w] = 0
	    try: df2[w] = len(df_time[w])
	    except: df2[w] = 0
	    tfidf[w] = freqdist[w]/(1+df0[w])
	# print df0
        #get sorted words in decreasing order of tfidf values
        sortedwords = sorted(tfidf.items(), key=itemgetter(1), reverse=True) 
        sortedwords = sortedwords[:cutoff]
        topwords = [w for w,s in sortedwords]
        sortedwords0 = sorted(df0.items(), key=itemgetter(1), reverse=True) 
        sortedwords1 = sorted(df1.items(), key=itemgetter(1), reverse=True) 
        sortedwords2 = sorted(df2.items(), key=itemgetter(1), reverse=True) 
        print 'TF-IDF topwords:'
        print len(topwords),'topwords:',sortedwords[:50],freqdist[topwords[0]],freqdist[topwords[1]]
	print sortedwords0[:30]
	print sortedwords1[:30]
	print sortedwords2[:30]
        return topwords,freqdist,df0,df1,df2
    return topwords,freqdist

def get_top_ngrams1(text,collection,NGRAM=2,cutoff=100):
    if NGRAM==2:
        ngram_measures = nltk.collocations.BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(text)
    elif NGRAM==3:
        ngram_measures = nltk.collocations.TrigramAssocMeasures()
        finder = TrigramCollocationFinder.from_words(text)

    # only bigrams that appear 3+ times
    finder.apply_freq_filter(3) 

    # return the 5 n-grams with the highest PMI
    print finder.nbest(ngram_measures.pmi, 100)
    raw_input('.')
    topwords = finder.nbest(ngram_measures.pmi, cutoff)
def get_website_stopwords():
    ftext = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',\
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',\
            'monday','tuesday','wednesday','thursday','friday','saturday','sunday',\
            'mon','tue','wed','thr','fri','sat','sun',\
            'facebook','twitter','http','myspace', \
            "web", "site","hide", "feedback", "view", \
            "press", "releases","phone", "fax","contact", "us", "hours", "ago",'months',"latest", "news","get", "involved","photo", "gallery","others", "like","continue", "reading",\
            "map", "channel","copyright", "c","upcoming", "events", "email", "address","join","via","po", "box","updates",\
            "press", "release","forgot", "password", "rss", "feed", "issues", "issue",  \
            'privacy', 'terms','comment', 'like', 'policy',\
            'keep', 'logged','search', 'keyword',\
            'bill','district',\
            "comment",'advertising', "developers", 'careers','rights', 'reserved',\
            'information','contact','office','state','states','news','new','comment','comments','view','candidate','template','congress','congressman','url','am','pm',\
            'click','today','daily','day','weekly','week','monthly','via','sign','download','video','audio','home','display','email','see',\
            'welcome','please','join','phone','telephone','page','like','website','blog','post','posted','radio','podcast','id','skip','link','links','get','online','homepage','background','function','help','webmaster','continue','latest',\
            'photo','photos','type']
            #word fragments
            #'ional','ey','erica','ne','de','tin','aho','ds','ed','erican','ds','oba','te','ad',''];
    return [w.lower() for w in ftext]
def get_website_stop_ngrams():
    text = ["comment like","press releases","phone fax","contact us","like view",\
                  "feedback hide","hide feedback","view feedback","hours ago","latest news", \
                  "get involved","photo gallery","others like","continue reading", \
                  "september comment", "site map", "http http","news channel","copyright c", \
                  "upcoming events", "email address","join us","via web","po box","email updates", \
                  "press release","forgot password", "rss feed", "news press", "issues news", "email password", \
                  "web site","privacy terms",\
            'flash player','empty string',\
            'advertising developers careers','toll free','read story',\
            'washington dc','building washington','attribute validation error',\
            'therein minutes','speak therein minutes following',\
	    'permitted speak therein','main street suit'] #
    bigs = [tuple(s.split()) for s in text]
    return bigs

def remove_website_stopwords(words):
    stw = get_website_stopwords()
    stw1 = get_website_stop_ngrams()
    ws = []
    for w in words:
        _w = " ".join( map(str,w) )
        has_s = False
        for s in stw:
            _s = " ".join( map(str,s) )
            if s in _w:
                has_s = True
                break
        for s in stw1:
            _s = " ".join( map(str,s) )
            if _s in _w:
                has_s = True
                break
        if has_s: continue
        ws.append(w)
    return ws
