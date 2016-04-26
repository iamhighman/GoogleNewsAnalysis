import csv, codecs, cStringIO

csv.field_size_limit(1000000000)
ENCODING = 'utf-8'
EXTRACT_DECODABLE_TEXT = True # remove token if it's not decodable
REMOVE_N = True # remove \t or \n etc. but keep a whitespace between tokens
def encode_str(s,encoding=ENCODING):
    total_non_decoded_tokens = 0
    try:
        return s.encode(encoding,'ignore')
    except UnicodeDecodeError, e:
        tokens = s.split()
        clean_tokens = []
        for tok in tokens:
            try:
                clean_tokens.append(tok.encode(encoding,'ignore'))
            except UnicodeDecodeError, e:
                # log= 'UnicodeEncodeError: %s %s' %  (e,tok)
                # print log
		total_non_decoded_tokens += 1
        s1 = ' '.join(clean_tokens)
	if total_non_decoded_tokens>0:
	    print 'remove %d/%d tokens due to UnicodeEncodeError'%(total_non_decoded_tokens,len(tokens))
        return s1

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding=ENCODING):
        self.reader = codecs.getreader(encoding)(f)
	self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding,'ignore')

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding=ENCODING, **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
	self.encoding = encoding

    def next(self):
        row = self.reader.next()
        return [unicode(s, self.encoding) for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding=ENCODING, **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
	self.encoding = encoding

    def writerow(self, row):
        self.writer.writerow([encode_str(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
