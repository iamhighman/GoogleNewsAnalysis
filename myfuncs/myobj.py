class Obj(object):
    def __init__(self,odict=None):
    #     if odict: self.fromdict(odic)
    # def fromdict(self, odict):
        self.odict = odict
        for k,v in odict.iteritems():
            setattr(self,k,v)
    def __repr__(self):
        s = ''
        for k,v in self.odict.iteritems():
            # if type(v).__name__!='str' and type(v).__name__!='bool' and len(v)>3: v=len(v)
	    # try:
	    # 	if len(v)>3: v=len(v)
	    # except: pass
            s += '\n\t%s: %s'%(k,v)
        return s
