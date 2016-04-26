#!/usr/bin/env python

'''
plot_example.py - plot network via cytoscape
    Use in ipython:
	# from plot_example import * 
	from plot_example import plotter
	p = plotter()
	p.get_graph()
	p.set_graph()
	p.layout()
	p.set_node_color()
@author: Yu-Ru Lin
@contact: yuruliny@gmail.com
@date: Aug 11, 2012

'''

import sys,os,csv
sys.path.append('../../myfuncs')
from funcs import rgb2hex,pickleload,pickledump
sys.path.append('../../myfuncs/cytoscape')
import networkx
from cytoscape import Cytoscape as cyto
import colorbrewer 

class plotter():
    def __init__(self):
	self.net = None
	self.G = None
	self.C = None
    def __del__(self): pass
    def get_graph(self,ifilename='karate.edgelist',directed=False):
	if directed: self.G = networkx.DiGraph()
	else: self.G = networkx.Graph()
	print 'read from',ifilename
	ifile = open(ifilename,'r')
	reader = csv.reader(ifile,delimiter=' ',quotechar='\"',quoting=csv.QUOTE_MINIMAL)
	for i,fields in enumerate(reader):
	    sys.stdout.write("\r                     \r"); sys.stdout.write("%i -" % (i)); sys.stdout.flush()
	    n = len(fields)
	    if n<2: continue
	    ni,nj = fields[:2]
	    if n>2: v = fields[2]
	    else: v = 1
	    self.G.add_edge(ni,nj,weight=float(v))
	ifile.close()
	print '#nodes=',self.G.number_of_nodes(),'#edges=',self.G.number_of_edges()
    def set_graph(self):
	self.C = cyto(network=self.G, node_opacity=0.85, edge_opacity=0.50, verbose=True)
    def layout(self,pkl_filename='tmp.pkl'):
	self.C.perform_yfiles_layout(wait=True)
	if pkl_filename:
	    node2pos = self.C.get_node_positions()
	    # NOTE: the returning position needs to be normalized by bounding box!
	    min_x,max_x,min_y,max_y = self.C.get_bbox()
	    for n,xy in node2pos.iteritems():
		x,y = xy
		x = (x-min_x)*1.0/(max_x-min_x)
		y = (y-min_y)*1.0/(max_y-min_y)
		node2pos[n] = (x,y)	    
	    pickledump(node2pos,pkl_filename,verbose=False)
    def layout_by_pos(self,pkl_filename='tmp.pkl'):
	if pkl_filename:
	    node2pos = pickleload(pkl_filename,verbose=True)
	    self.C.set_node_positions(nodes=node2pos.keys(),positions=node2pos.values())		    
    def set_node_color(self,attrname='example by using id as color'):
	pals = colorbrewer.RdYlBu[10]
	n = self.G.number_of_nodes()
	node2id = dict([(ni,ni) for ni in self.G.nodes()])
	id2color = dict([(ni,rgb2hex(pals[int(float(ni)/n*10)])) for ni in self.G.nodes()])	
	self.C.map_node_color_discrete(node2id, attrname, id2color, match_border=False)
p = plotter()
def main(argv):
    h = plotter()
    h.get_graph()
    h.set_graph()
    h.set_node_color()
    h.layout()
    
if __name__ == '__main__': 
    main(sys.argv[1:])
