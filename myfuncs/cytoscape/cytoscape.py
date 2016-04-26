#!/usr/bin/env python

# cytoscape.py
# Jim Bagrow
# Last Modified: 2012-05-18

"""
Requirements:
    OS X (there's some Applescript involved...)
    Python and 3rd-party packages numpy, pylab, and networkx
    Cytoscape
        CYtoscapeRPC plugin
        LayoutSaverPlugin (for node_positions only)
    pdfcrop (optional, to remove empty page around exported network pdfs)

To install:
    1. Install Cytoscape: http://www.cytoscape.org/
    2. Install LayoutSaverPlugin (done within Cytoscape)
    3. Install and configure CytoscapeRPC plugin:
        1. Launch cytoscape:
        2. Go to Plugins > Manage Plugins
        3. When Manage Plugins window appears select Communication/Scripting >
           CytoscapeRPC 1.8 and click Install. Close Manage Plugins Window.
        4. Go to Plugins > CytoscapeRPC > Settings (If not available restart Cytoscape).
        5. Check off Enable XML-RPC, Local only, and Auto start. Make sure Port is set
           to 9,000. Hit OK.
        6. Quit Cytoscape (optional).
"""
import os, time
import xmlrpclib, socket
import colorsys
import numpy, pylab, networkx


class Cytoscape():
    """Control Cytoscape from python on OS X."""
    def __init__(self,
            url='http://localhost:9000',
            node_font_size=0.0,
            node_color="#E6072A",
            edge_color="#000000",
            node_opacity=1.0,
            edge_opacity=1.0,
            node_shape="ellipse",
            node_size=40.0,
            edge_width=1.5,
            bg_color="#ffffff",
            verbose=False,
            show_graphics=True,
            network=None, graph=None):
        """Initialize a connection to Cytoscape. Optionally change some
        graphics defaults, and load a networkx Graph (can also be loaded later
        using `load_network' method).
        """
        
        self._url           = url # localhost url to cytoscape
        self.verbose        = verbose
        self._nid           = None # network id, set by load_network
        self.graph          = None # networkx graph, set by load_network
        self.show_graphics  = show_graphics
        self.node_font_size = node_font_size
        self.node_color     = node_color
        self.edge_color     = edge_color
        self.node_opacity   = node_opacity
        self.edge_opacity   = edge_opacity
        self.node_shape     = node_shape
        self.node_size      = node_size
        self.edge_width     = edge_width
        self.bg_color       = bg_color
        if self.verbose:
            print "Activating cytoscape..."
        self.cyto = self._launch()
        self.clear() # also applies vizmap defaults
        
        # load network, if specified:
        if network or graph:
            if network is not None:
                self.load_network(network)
            elif graph is not None:
                self.load_network(graph)
            self.redraw()
    
    def _launch(self):
        """Connect to cytoscape through the RPC XML magic. Cytoscape may not be
        fully activated when this is first called, so continue trying to
        connect until the cytoscape "server" issues a response.
        """
        a = xmlrpclib.ServerProxy(self._url) # install cyto RPC plugin, and set to autostart.
        os.system( """osascript -e 'tell Application "Cytoscape" to activate'""" )
        while True: # keep trying to connect
            try:
                a._()   # Call a fictitious method.
            except xmlrpclib.Fault: # Connected to the server, method doesn't exist which is expected.
                return a.Cytoscape
            except socket.error:    # Not connected; socket error means that the service is unreachable.
                time.sleep(1)
    
    def connect(self):
        """Connect or reconnect to cytoscape."""
        if self.verbose:
            print "Connecting to cytoscape..."
        self.cyto = self._launch()
        
    def quit(self):
        """Tell cytoscape (through applescript) to quit."""
        if self.verbose:
            print "Quitting cytoscape..."
        os.system("""osascript -e 'tell Application "Cytoscape" to quit'""" )
    
    def perform_layout(self, layout="default"):
        """Perform a cytoscape layout using the default settings on the current
        network. For yFiles layouts, please see `perform_yfiles_layout'.
        `layout' is the name of the cytoscape layout to be run; see
        available_layouts for a list of valid layout strings.
        """
        if layout == "default":
            self.cyto.performDefaultLayout()
        else:
            available_layouts = self.available_layouts()
            available_layouts.remove("Apply Saved Layout")
            layout = layout.lower()
            if layout not in available_layouts:
                print "Unknown layout, using default instead..."
                self.cyto.performDefaultLayout()
            else:
                if self.verbose:
                    print "Applying '%s' layout..." % layout
                self.cyto.performLayout(layout)
        self.redraw()
    
    def available_layouts(self):
        """Print a list of the names of all available cytoscape layout commands
        (except the yFiles commands, see perform_yfiles_layout). These names
        may be used in perform_layout.
        """
        return set(self.cyto.getLayoutNames())
    
    def _vizmap_defaults(self):
        """Set the default values for a number of cytoscape visual attributes
        such as background color, node and edge opacity, etc. These defaults
        were set when Cytoscape() was initialized.
        """
        self.cyto.setDefaultBackgroundColor('default', self.bg_color)
        self.cyto.setDefaultVizMapValue('default', "Node Shape", self.node_shape)
        self.cyto.setDefaultVizMapValue('default', "Node Font Size", str(self.node_font_size))
        self.cyto.setDefaultVizMapValue('default', "Node Color", self.node_color)
        self.cyto.setDefaultVizMapValue('default', "Edge Color", self.edge_color)
        self.cyto.setDefaultVizMapValue('default', "Node Opacity", str(255*self.node_opacity))
        self.cyto.setDefaultVizMapValue('default', "Edge Opacity", str(255*self.edge_opacity))
        self.cyto.setDefaultVizMapValue('default', "Node Size", str(self.node_size))
        self.cyto.setDefaultVizMapValue('default', "Edge Line Width", str(self.edge_width))
    
    def perform_yfiles_layout(self, layout="Organic", wait=True):
        """Special command to execute the propreitary yFiles layouts. `layout'
        is the name of the yFiles command to run, as listed in the Layout >
        yFiles menu in Cytoscape. The name is case-sensitive. `Wait' if True
        tells the script to pause until the user indicates it may continue.
        This is useful since cytoscape does not seem able to communicate
        whether the yFiles process has finished executing or not.
        """
        if self.verbose:
            print "Performing yfiles layout..."
        click_yfiles = """
        tell application "System Events"
            tell process "Cytoscape"
                tell menu bar 1
                    tell menu bar item "Layout"
                        pick
                        tell menu 1
                            tell menu item "yFiles"
                                pick
                                tell menu 1
                                    pick menu item "%s"
                                end tell
                            end tell
                        end tell
                    end tell
                end tell
            end tell
        end tell
        """ % layout
        #time.sleep(0.5)
        os.system("""osascript -e '%s' > /dev/null""" % click_yfiles)
        #time.sleep(0.5)
        if wait is True:
            os.system("""osascript -e 'tell application "Terminal" to activate'""")
            raw_input("Wait until cytoscape layout is finished, then press enter...")
        self.redraw()
    
    def load_network(self, graph, name="network",new_network=True):
        """Load (undirected) networkx graph into cytoscape.  Nodes IDs are
        changed to strings before loading.
        """
        if self.verbose:
            print "Loading network..."
        self.graph = graph
	if new_network:
	    self.cyto.createNetwork(name)        # create a network in cytoscape
	    self._nid = self.cyto.getNetworkID() # get the network id (nid)
        nodes = map(str,graph.nodes()) # cytoscape nodes must always be strings
        self.cyto.createNodes(nodes)
        edgesL,edgesR = [],[]
        for i,j in graph.edges():
            if i > j: # edges in cyto are directed, but we don't support that!
                i,j = j,i
            edgesL.append(str(i)) # again, nodes must be strings
            edgesR.append(str(j))
        self.cyto.createEdges(edgesL,edgesR)
	if new_network: self.cyto.performDefaultLayout()
        self.show_graphics_details(show=self.show_graphics)
        self.redraw()

    def edit_network(self, graph, name="network"):
        """Load (undirected) networkx graph into cytoscape.  Nodes IDs are
        changed to strings before loading.
	Note: this function is still experimental! It works but too slow to be useful.
	@TODO: check how to call self.cyto.removeSelectedEdges and self.cyto.removeSelectedNodes
        """
        if self.verbose:
            print "Loading network..."
	N,E = self.graph.nodes(),self.graph.edges()
	N1,E1 = graph.nodes(),graph.edges()
	new_nodes = [n for n in N1 if not n in N]
	to_remove_nodes = [n for n in N if not n in N1]
	new_edges = [e for e in E1 if not e in E]
	to_remove_edges = [e for e in E if not e in E1]
	for i,j in to_remove_edges:
	    self.cyto.removeEdge(self._edge_id(i,j))
	for n in to_remove_nodes:
	    self.cyto.removeNode(str(n))
	for n in new_nodes:
	    self.cyto.addNode(str(n))
	for i,j in new_edges:
	    self.cyto.addEdge(self._edge_id(i,j))
	    
        # self.cyto.performDefaultLayout()
        self.graph = graph
        self.show_graphics_details(show=self.show_graphics)
        self.redraw()
    
    def remove_nodes(self, nodes):
        for n in nodes:
            if n in self.graph:
                self.cyto.removeNode(str(n))
                self.graph.remove_node(n)
    
    def save_pdf(self, filename, crop=True):
        """Write the current network view to a pdf with name `filename'.  If
        `crop' is True, the pdf will have surrounding whitespace removed using
        the open-source pdfcrop script [1] (which the user must install and
        make available on his/her path). This script is typically available
        through modern tex distros such as miktex,texlive, or mactex.
        
        [1] http://www.ctan.org/pkg/pdfcrop
        """
        if self.verbose:
            print "Saving pdf..."
        # default save location is directory holding Cytoscape.app, so I need
        # to deal with this nonsense: :(
        if filename[0] != "/" and filename[0] != "~":
            filename = os.getcwd() +"/"+ filename
        if crop:
            self.fit_view() # necessary?
        self.cyto.exportViewToPDF(self._nid, filename)
        if crop:
            os.system("pdfcrop '%s' f123_temp.pdf > /dev/null; mv f123_temp.pdf '%s'" % (filename,filename))
    
    def map_node_color_discrete(self, node2cat, name, cat2color=None, match_border=True):
        """Color nodes according to "categories" stored in dict `node2cat'
        mapping each node's name to a discrete value.  `name' is a string
        describing the attributes being added; it will be visible in Cytoscape.
        
        Optional dictionary `cat2color' maps each category to a hexadecimal rgb
        color string; if not supplied, colors will be generated for each
        category.
        
        If `match_border' is True, then node borders will have the same color
        as their centers, otherwise the default cytoscape border color is used.
        """
        if self.verbose:
            print "Applying discrete node colors..."
        
        # add node attribute to cytoscape:
        nodes,categories = zip(*node2cat.items())
        nodes,categories = map(str,nodes), map(str,categories)
        self.cyto.addStringNodeAttributes(name, nodes, categories)
        
        # create discrete colors:
        if cat2color is None:
            all_cats = sorted(list(set(categories)))
            colors   = distinguishable_colors(len(all_cats))
            cat2color = dict(zip(all_cats,colors))
        else:
            cats,colors = zip(*cat2color.items())
            cat2color = dict( zip(map(str,cats),colors) )
        
        # add node color vizmapper for the attribute in cytoscape:
        self.cyto.createDiscreteMapper(
            'default',    # vizmap being modified
            name,         # node attribute used as key
            'Node Color', # What is being changed
            '#ffffff',    # default value for nodes without attribute
            cat2color
        )
        if match_border:
            self.cyto.createDiscreteMapper(
                'default',           # vizmap being modified
                name,                # node attribute used as key
                'Node Border Color', # What is being changed
                '#ffffff',           # default value for nodes without attribute
                cat2color
            )
        
        self.redraw()
    
    def map_node_color_continuous(self, node2val, name, val2color=None, match_border=True, cmap=None):
        """Color nodes based on "continuous" (ie, orderable) scalar attributes
        assigned to each node by dictionary `node2val'. Values/attributes are
        assumed to be floats and will be converted as such. The string `name'
        is  the label for the node attribute that will appear in cytoscape.
        
        `val2color' is an optional dict or list mapping values to hexadecimal
        rgb color strings.  Cytoscape will linearly interpolate between values,
        so not all values need a specified color.  If `val2color' is not given,
        a colormap will be used based on matlab's "jet" colormap. If
        `val2color' is a list of color strings instead of a dict, those colors
        will be linearly spaced over the range of node values. For example, if
        val2color is ["#000000", "#ffffff"] then node colors will be mapped
        linearly from black for the minimum value to white for the maximum
        value.
        
        If `match_border' is True, then node borders will have the same color
        as their centers, otherwise the default cytoscape border color is used.
        """
        if self.verbose:
            print "Applying continuous node colors..."
        
        # add the float node attributes:
        nodes,values = zip(*node2val.items())
        values = map(float,values)
        self.cyto.addDoubleNodeAttributes(name, map(str,nodes), values)
        
        # prepare the mapping between attribute and color:
        if val2color is None:
            valPoints,valColors = build_colormap(values, cmap=cmap)
        elif type(val2color) == type({}):
            valPoints,valColors = zip(*val2color.items())
        elif type(val2color) == type([]):
            valColors = val2color
            valPoints = numpy.linspace(min(values)-1e-4,max(values)+1e-4, len(valColors))
            valPoints = map(float,list(valPoints))
        valColors = list(valColors)
        
        # add node color vizmappers to cytoscape:
        self.cyto.createContinuousNodeVisualStyle(
            name,
            'Node Color',
            valPoints, ["#000000"]+valColors+["#000000"],
            True
        )
        if match_border:
            self.cyto.createContinuousNodeVisualStyle(
                name,
                'Node Border Color',
                valPoints, ["#000000"]+valColors+["#000000"],
                True
            )
        self.redraw()
    
    def map_node_size(self, node2val, name, val2size=None):
        """Make node size proportional to continuous values stored in
        dictionary `node2val'. `name' is a string that will be used to title
        the cytoscape attribute corresponding to node2val. `val2size' is an
        optional dictionary or list mapping each attribute value to a node
        radius. If val2size=[10,100], for example, then the values will be
        mapped linearly to sizes ranging from 10 for the smallest node value to
        100 for the largest value.
        """
        if self.verbose:
            print "Applying node sizes..."
        
        # add the float node attributes:
        nodes,values = zip(*node2val.items())
        values = map(float,values)
        self.cyto.addDoubleNodeAttributes(name, map(str,nodes), values)
        
        # prepare the mapping between value/attribute and size/radius:
        if val2size is None:
            mapPoints = [min(values)-1e-4, max(values)+1e-4]
            mapSizes  = [20.0, 80.0]
        elif type(val2size) == type({}):
            mapPoints,mapSizes = zip(*val2size.items())
        elif type(val2size) == type([]):
            mapSizes = val2size
            mapPoints = numpy.linspace(min(values)-1e-4,max(values)+1e-4, len(mapSizes))
            mapPoints = map(float,list(mapPoints))
        
        # apply the style and redraw the network:
        self.cyto.createContinuousNodeVisualStyle(
                name, 'Node Size',
                map(float,mapPoints), [0.1]+list(mapSizes)+[0.1],
                True
            )
        self.redraw()
    
    def map_node_shape(self, node2cat, name, cat2shape=None):
        """Make node shapes reflect categories stored in dict `node2cat'. The optional
        dict cat2shape maps each category to the name of a node shape. For example,
        cat2shape={'1':'ellipse', '2':'triangle'}, will display each category '1' node
        as a circle and each category '2' node as a triagnle.
        
        The names of cytoscape node shapes can be seen using:
        >>> C = Cytoscape()
        >>> print C.cyto.getNodeShapeNames()
        """
        if self.verbose:
            print "Applying node shapes..."
        
        # add category node attributes:
        nodes,categories = zip(*node2cat.items())
        nodes,categories = map(str,nodes), map(str,categories)
        self.cyto.addStringNodeAttributes(name, nodes, categories)
        
        all_cats = sorted(list(set(categories))) # cats should be strings!
        if cat2shape is None:
            #available_shapes = self.cyto.getNodeShapeNames()
            available_shapes = ['ellipse', 'triangle', 'diamond', 'parallelogram',
                                'rect', 'vee', 'hexagon', 'octagon',
                                'trapezoid', 'round_rect', 'rect_3d', 'trapezoid_2']
            num_shapes = len(available_shapes)
            num_categs = len(all_cats)
            shapes = available_shapes*int(1.0*num_categs/num_shapes+1)
            cat2shape = dict( zip(all_cats,shapes[:num_categs]) )
        else:
            cats,shapes = zip(*cat2shape.items())
            cat2shape = dict( zip(map(str,cats),shapes) )
            
        
        self.cyto.createDiscreteMapper(
            'default',    # vizmap being modified
            name,         # node attribute used as key
            'Node Shape', # What is being changed
            'triangle',   # default value for nodes without attribute
            cat2shape,    # dict mapping attribue to display
        )
        self.redraw()
    
    def map_edge_width(self, edge2val, name, val2size=None):
        """Make edge width proportional to values stored in dict `edge2val'.
        This function works similarly to map_node_size, see there for details.
        """
        if self.verbose:
            print "Applying edge widths..."
        
        # rebuild edge2val using cytoscape edge IDs, if necessary:
        eid2val = {}
        for e in edge2val:
            if type(e) == type("string"): # assume strings are cytoIDs
                eid2val[e] = edge2val[e]
            else:
                eid = self._edge_id(*e)
                eid2val[eid] = edge2val[e]
        
        # add the float edge attributes:
        eids,values = zip(*eid2val.items())
        values = map(float,values)
        self.cyto.addDoubleEdgeAttributes(name,eids,values)
        
        # prepare the mapping between value/attribute and width:
        if val2size is None:
            mapPoints = [min(values)-1e-4, max(values)+1e-4]
            mapSizes  = [0.5, 10.0]
        elif type(val2size) == type({}):
            mapPoints,mapSizes = zip(*val2size.items())
        elif type(val2size) == type([]):
            mapSizes = val2size
            mapPoints = numpy.linspace(min(values)-1e-4,max(values)+1e-4, len(mapSizes))
            mapPoints = map(float,list(mapPoints))
        
        self.cyto.createContinuousEdgeVisualStyle(
                name, 'Edge Line Width',
                mapPoints, [0.0]+mapSizes+[0.0],
                True
            )
        self.redraw()

    def map_edge_opacity(self, edge2val, name, val2size=None):
        """Make edge width proportional to values stored in dict `edge2val'.
        This function works similarly to map_node_size, see there for details.
        """
        if self.verbose:
            print "Applying edge opacities..."
        
        # rebuild edge2val using cytoscape edge IDs, if necessary:
        eid2val = {}
        for e in edge2val:
            if type(e) == type("string"): # assume strings are cytoIDs
                eid2val[e] = edge2val[e]
            else:
                eid = self._edge_id(*e)
                eid2val[eid] = edge2val[e]
        
        # add the float edge attributes:
        eids,values = zip(*eid2val.items())
        values = map(float,values)
        self.cyto.addDoubleEdgeAttributes(name,eids,values)
        
        # prepare the mapping between value/attribute and width:
        if val2size is None:
            mapPoints = [min(values)-1e-4, max(values)+1e-4]
            mapSizes  = [0.0, 255.0]
        elif type(val2size) == type({}):
            mapPoints,mapSizes = zip(*val2size.items())
        elif type(val2size) == type([]):
            mapSizes = val2size
            mapPoints = numpy.linspace(min(values)-1e-4,max(values)+1e-4, len(mapSizes))
            mapPoints = map(float,list(mapPoints))
        self.cyto.createContinuousEdgeVisualStyle(
                name, 'Edge Opacity',
                mapPoints, [0.0]+mapSizes+[0.0],
                True
            )
        self.redraw()
    
    def map_edge_color_discrete(self, edge2cat, name, cat2color=None):
        """Like map_node_color_discrete but for edges. The dict `edge2cat'
        takes tuples (i,j) and maps them to categories/attributes. The optional
        dict `cat2color' maps each category name to a hexadecimal rgb string.
        If not provided, N colors with maximally separated hues will be used,
        where N is the number of unique categories found in edge2cat.
        """
        if self.verbose:
            print "Applying discrete edge colors..."
        
        # add edge attributes to cytoscape:
        edges,categories = zip(*edge2cat.items())
        eids = [self._edge_id(*e) for e in edges]
        categories = map(str,categories)
        self.cyto.addStringEdgeAttributes(name, eids, categories)
        
        # create discrete colors:
        if cat2color is None:
            all_cats = sorted(list(set(categories)))
            colors   = distinguishable_colors(len(all_cats))
            cat2color = dict(zip(all_cats,colors))
        else: # make sure keys are strings
            cats,colors = zip(*cat2color.items())
            cat2color = dict( zip(map(str,cats),colors) )
        
        # add node color vizmapper for the attribute in cytoscape:
        self.cyto.createDiscreteMapper(
            'default',    # vizmap being modified
            name,         # edge attribute used as key
            'Edge Color', # What is being changed
            '#000000',    # default value for edges without attribute
            cat2color
        )
        self.redraw()
    
    def map_edge_color_continuous(self, edge2val, name, val2color=None, cmap=None):
        """Like map_node_color_continuous but for edges. The dict `edge2val'
        takes tuples (i,j) and maps them to values.
        """
        if self.verbose:
            print "Applying continuous edge colors..."
        
        # add the float edge attributes:
        edges,values = zip(*edge2val.items())
        eids = [self._edge_id(*e) for e in edges]
        values = map(float,values)
        self.cyto.addDoubleEdgeAttributes(name, eids, values)
        
        # prepare the mapping between attribute and color:
        if val2color is None:
            valPoints,valColors = build_colormap(values, cmap=None)
        elif type(val2color) == type({}):
            valPoints,valColors = zip(*val2color.items())
        elif type(val2color) == type([]):
            valColors = val2color
            valPoints = numpy.linspace(min(values)-1e-4,max(values)+1e-4, len(valColors))
            valPoints = map(float,list(valPoints))
        
        # add edge color vizmappers to cytoscape:
        self.cyto.createContinuousEdgeVisualStyle(
            name,
            'Edge Color',
            valPoints, ["#000000"]+valColors+["#000000"],
            True
        )
        self.redraw()
    
    def redraw(self):
        """Tells cytoscape to refresh the network view."""
        try:
            self.cyto.redraw()
        except:
            pass
    
    def _edge_id(self, nodei, nodej):
        """Cytoscape has a strange way of storing the string that represents an
        edge.
        """
        if nodei > nodej:
            nodei,nodej = nodej,nodei
        return "%s (directed) %s" % (str(nodei),str(nodej))
    
    def clear_attributes(self):
        """Erase all node and edge attributes currently in cytoscape, delete
        the current visual style, and reapply the visual style generated when
        Cytoscape() was called.
        """
        for n in self.cyto.getNodeAttributeNames():
            self.cyto.deleteNodeAttribute(n)
        for e in self.cyto.getEdgeAttributeNames():
            self.cyto.deleteEdgeAttribute(e)
        self.cyto.deleteVisualStyle('default') # is this right...?
        self.cyto.setVisualStyle('default')
        self._vizmap_defaults()
        self.redraw()
    
    def destroy_networks(self):
        """Clear the network(s) currently present in cytoscape."""
        while True:
            try:
                self.cyto.destroyNetwork(self.cyto.getNetworkID())
            except:
                break
    
    def clear(self):
        """Remove networks, node/edge attributes, and changes to visual styles
        that have been added to cytoscape.
        """
        self.clear_attributes()
        self.destroy_networks()
    
    def show_graphics_details(self,show=True):
        """Tell cytoscape to show or hide Graphics Details."""
        if self.verbose:
            print "Toggling graphics..."
        self.cyto.setShowGraphicsDetails(self._nid, show)
        self.redraw()
    
    def get_node_positions(self, nodes=None, filename=None):
        """Return a dict mapping node to (x,y) tuples. `nodes' is a list of
        nodes to get coordinates for; if omitted all node coordinates are
        retrieved. If `filename' is given, these coordinates are also saved to
        a (tab-separated) file with that name.
        
        It's up to you to ensure that specified nodes are actually inside
        cytoscape when this is called.
        
        Note that this requires installing the "Save Node Positions" cytoscape
        plugin.
        """
        # clear existing x,y attributes:
        self.cyto.deleteNodeAttribute("saved_x_location")
        self.cyto.deleteNodeAttribute("saved_y_location")
        
        # run the save node positions command:
        applescript = """
        tell application "System Events"
            tell process "Cytoscape"
                tell menu bar 1
                    tell menu bar item "Layout"
                        pick
                        tell menu 1
                            pick menu item "Save Node Positions"
                        end tell
                    end tell
                end tell
            end tell
        end tell
        """
        time.sleep(1)
        os.system("""osascript -e '%s' > /dev/null""" % applescript)
        time.sleep(1)
        
        # prepare the list of nodes, if necessary:
        if nodes is None:
            nodes = self.graph.nodes()
        nodes = map(str,nodes) # nodes are always strings in cytoscape
            
        # retrieve x,y positions:
        X = self.cyto.getNodesAttributes("saved_x_location", nodes)
        Y = self.cyto.getNodesAttributes("saved_y_location", nodes)
        
        # build output dict:
        node2xy = {}
        for node,x,y in zip(nodes,X,Y):
            node2xy[node] = (x,y)
        
        if filename is not None:
            fout = open(filename, 'w')
            for n in node2xy:
                x,y = node2xy[n]
                fout.write("%s\t%f\t%f\n" % (n,x,y))
            fout.close()
        
        return node2xy
    
    def set_node_positions(self, nodes, positions=None, absolute=False):
        """Set the XY-coordinates of nodes.  Input may be a dict mapping nodes
        -> (x,y) pairs, or a list of nodes and a list of (x,y) pairs, or a
        single node and single (x,y) pair.
        
        X (Y) coordinates are defined such that 0 is the current leftmost
        (topmost) node while 1 is the current rightmost (bottommost) node.
        Coordinates can be < 0 or > 1.
        
        Nodes that are not already in the network will be added (with no
        links). This is useful for drawing node size/shape/color keys or
        legends. However, it is best to add these nodes to the network before
        initializing the cytoscape visual mappings (such as
        map_node_color_discrete) so that the legend nodes are assigned
        attributes.
        
        Example:
        >>> C = Cytoscape(network=G)
        >>> C.set_node_positions( [1,2], [(0.4,0.5), (0.6,0.5)] )
        """
        
        # parse input(s):
        if type(nodes) == type({}) and positions is None:
            nodesL, positions = [],[] # verbose code here, just to be safe...
            for n in nodes:
                nodesL.append(n)
                positions.append(nodes[n])
            nodes = nodesL
        elif is_iterable(nodes) and is_iterable(positions):
            if len(nodes) != len(positions):
                raise TypeError("The number of nodes does not equal the number of positions.")
            pass # input is ready
        elif not is_iterable(nodes) and is_iterable(positions) and len(positions) > 1:
            nodes, positions = [nodes], [positions[:2]] # just one node
        else:
            raise TypeError("Input is not in an expected form.")
        
        # add any new nodes to the network:
        new_nodes = [n for n in nodes if n not in self.graph]
        self.cyto.createNodes(map(str,new_nodes))
        # also add to self.graph?
        
        # set node positions:
        if absolute is False: # transform from [0,1]
            X_all, Y_all = zip(*self.get_node_positions().values()) # a bit too slow...
            xmin,xmax = min(X_all),max(X_all)
            ymin,ymax = min(Y_all),max(Y_all)
            w,h = xmax-xmin,ymax-ymin
            coords = [ (xmin + w*x, ymin + h*y) for x,y in positions ]
            X,Y = zip(*coords)
        else: # coordinates don't need to be transformed
            X,Y = zip(*positions)
        self.cyto.setNodesPositions(self._nid, map(str,nodes), X, Y)
        
        self.redraw()
    
    def get_bbox(self):
        """get node coordinates x,y and return min(x), max(x), min(y),
        max(y)."""
        xy = self.get_node_positions().values()
        x,y = zip(*xy)
        return min(x), max(x), min(y), max(y)
    

    def set_node_labels(self, nodes, labels=None, name=None, fontsizes=None, absolute_fontsize=False ):
        """Nodes can be a dict node->text, or a list of nodes. If a list of
        nodes, then labels can be either a string and all nodes will be given
        that label or a list of the same length as nodes. Nodes omitted will be
        given no label while nodes that are labeled but not present in the
        network will be added (with no neighbors). Fontsizes is a single number
        specifying how big all the labels should be, or a dict mapping node
        (label?) to font size.
        """
        # parse input(s):
        if name is None:
            name = "node_label"
        
        if type(nodes) == type({dict}) and labels is None:
            nodes, labels = zip(*nodes)
        elif is_iterable(nodes) and is_iterable(labels):
            if len(nodes) != len(labels):
                raise TypeError("The number of nodes does not equal the number of labels.")
            pass # input is ready
        else:
            raise TypeError("Input is not in an expected form.")
        nodes = map(str,nodes)
        
        if type(fontsizes) == type(12):
            fontsizes = [fontsizes]*len(nodes)
        elif type(fontsizes) == type({}):
            fontsizes = [fontsizes[n] for n in nodes]
        elif is_iterable(fontsizes):
            pass # input is ready
        else:
            fontsizes = [24]*len(nodes)
        
        # adjust for zoom:
        if not absolute_fontsize:
            z = float(self.cyto.getZoom(self._nid))
            fontsizes = [int(f/z) for f in fontsizes]
        
        
        # add any new nodes to the network:
        new_nodes = [n for n in nodes if n not in self.graph]
        self.cyto.createNodes(map(str,new_nodes))
        # also add to self.graph?
        
        # add string attributes:
        self.cyto.addStringNodeAttributes(name, nodes, labels)
        self.cyto.addIntegerNodeAttributes(name+" fontsize", nodes, fontsizes)
        
        # create the vizmaps:
        self.cyto.createPassthroughMapper(
            'default',    # vizmap being modified
            name,         # node attribute used as key
            'Node Label', # What is being changed
            ''            # default value for nodes without attribute
        )
        self.cyto.createPassthroughMapper(
            'default',        # vizmap being modified
            name+" fontsize", # node attribute used as key
            'Node Font Size', # What is being changed
            '0'               # default value for nodes without attribute
        )
        
        self.redraw()
    
    def rescale_fontsize(self,z=None):
        """docstring TODO"""
        if z is None:
            z = self.cyto.getZoom(self._nid)
        else:
            z = 1.0/z
        
        # replace existing attribute:
        nodes = self.cyto.getNodes(self._nid)
        for name in self.cyto.getNodeAttributeNames():
            if " fontsize" in name:
                nodesWattr = [n for n in nodes if self.cyto.hasNodeAttribute(n, name)]
                fontsizes = self.cyto.getNodesAttributes(name, nodesWattr)
                fontsizes = [int(float(f)/z) for f in fontsizes]
                self.cyto.addIntegerNodeAttributes(name, nodesWattr, fontsizes)
        
        self.redraw()
    
    def add_node_legend(self, name, values=None, position=None, legend_height=0.25, show_labels=True,
                              label_fontsize=12):
        """docstring TODO"""
        if self.verbose:
            print "Adding node legend..."
        
        # what kind of attribute is it?
        try:
            attr_type = self.cyto.getNodeAttributeType(name)
        except:
            raise ValueError("Given name (%s) is not currently present in cytoscape.")
        
        # create new nodes for the legend:
        num_nodes = len(values)
        nodes = ["%i legendnode" % i for i in xrange(num_nodes)]
        self.cyto.createNodes(nodes)
        
        # add the attributes for the new nodes:
        if attr_type == "FLOATING":
            self.cyto.addDoubleNodeAttributes(name, nodes, map(float,values))
        elif attr_type == "STRING":
            self.cyto.addStringNodeAttributes(name, nodes, map(str,values))
        elif attr_type == "INTEGER":
            self.cyto.addIntegerNodeAttributes(name, nodes, map(int,values))
        else:
            raise TypeError("Attribute type (%s) is unexpected." % attr_type)
            
        # set positions of the legend nodes:
        if position and is_iterable(position):
            if is_iterable(position[0]):
                if len(position) == 2: # just start and stop:
                    (xi,yi),(xs,ys) = position
                    X = [float(x) for x in numpy.linspace(float(xi),float(xs),num_nodes)]
                    Y = [float(y) for y in numpy.linspace(float(ys),float(yi),num_nodes)]
                    positions = zip(X,Y)
                elif len(position) == num_nodes:
                    positions = position
            else:
                xi,yi = position # just start, assume vertical legend
                ys = yi + legend_height
                positions = [(float(xi),float(y)) for y in numpy.linspace(ys,yi,num_nodes)]
        #positions = [ (1.0,float(y)) for y in numpy.linspace(0.9,0.5,num_nodes) ]
        self.set_node_positions(nodes, positions)
        
        if show_labels:
            labels = map(str,values)
            self.set_node_labels(nodes, labels=labels, fontsizes=label_fontsize, name="legendlabel")
        
        self.fit_view()
    
    def fit_view(self):
        """Redraw cytoscape network window to tightly display all elements of
        the network.
        """
        if self.verbose:
            print "Fitting view..."
        self.cyto.fitContent(self._nid)
        self.redraw()
    


def is_iterable(candidate):
    if type(candidate) == type("string"):
        return False
    try:
        iter(candidate)
    except TypeError:
        return False
    else:
        return True


def build_colormap(vals, num=100, cmap=pylab.cm.jet):
    """Build a list of `num' rgb hexadecimal color strings corresponding to num
    points linearly spaced between the minimum and maximum of vals. Colors are
    generated from the "jet" colormap by default (jet is MATLAB's default colormap).
    Other colormaps can be used by passing their pylab functions with the cmap command,
    for example: `cmap=pylab.cm.hot'.
    
    Returns list of linearly spaced points between `min(vals)' and `max(vals)'
    and list of color strings corresponding to each point.
    
    Example:
    >>> points,colors = build_colormap([0.0,1.0,2.0], num=20)
    """
    X = numpy.arange(0.0,1.0+1e-8,1.0/num)
    if cmap is None:
        cmap = pylab.cm.jet
    J = cmap(X)
    mapX = list(numpy.linspace(min(vals)-1e-5, max(vals)+1e-5, num+1))
    colX = [rgb_to_hex(c[:3]) for c in J]
    return map(float,mapX),colX


def distinguishable_colors(num, sat=1.0, val=1.0):
    """Generate a list of `num' rgb hexadecimal color strings. The strings are
    linearly spaced along hue values from 0 to 1, leading to `num' colors with
    maximally different hues.
    
    Example:
    >>> print distinguishable_colors(5)
    ['#ff0000', '#ccff00', '#00ff66', '#0066ff', '#cc00ff']
    """
    list_colors = [];
    hue = 0.0
    while abs(hue - 1.0) > 1e-4:
        rgb = [i for i in list(colorsys.hsv_to_rgb(hue, sat, val))]
        list_colors.append( rgb_to_hex(rgb) )
        hue += 1.0/num;
    return list_colors


def rgb_to_hex(rgb):
    """Convert an rgb 3-tuple to a hexadecimal color string.
    
    Example:
    >>> print rgb_to_hex((0.50,0.2,0.8))
    #8033cc
    """
    return '#%02x%02x%02x' % tuple([round(x*255) for x in rgb])


def hex_to_rgb(hexrgb):
    """ Convert a hexadecimal color string to an rgb 3-tuple.
    
    Example:
    >>> print hex_to_rgb("#8033CC")
    (0.502, 0.2, 0.8)
    """
    hexrgb = hexrgb.lstrip('#')
    lv = len(hexrgb)
    return tuple(round(int(hexrgb[i:i+lv/3], 16)/255.0,4) for i in range(0, lv, lv/3))


def darken_hex(hexrgb, factor=0.5):
    """Take an rgb color of the form #RRGGBB and darken it by `factor' without
    changing the color. Specifically the RGB is converted to HSV and V ->
    V*factor.
    
    Example:
    >>> print darken_hex("#8033CC")
    '#401966'
    """
    rgb = hex_to_rgb(hexrgb)
    hsv = list(colorsys.rgb_to_hsv(*rgb))
    hsv[2] = hsv[2]*factor
    rgb = colorsys.hsv_to_rgb(*hsv)
    return rgb_to_hex(rgb)


def darken_rgb(rgb, factor=0.5):
    """Take an rgb 3-tuple and darken it by `factor', approximately
    preserving the hue.
    
    Example:
    >>> print darken_rgb((0.5,0.2,0.7))
    (0.251, 0.098, 0.3529)
    """
    hexrgb = darken_hex(rgb_to_hex(rgb), factor=factor)
    return hex_to_rgb(hexrgb)


def scale01(L):
    """Linearly rescale the values in `L` such that they fall between 0 and 1."""
    minx,maxx = 1.0*min(L),1.0*max(L)
    return [(x-minx)/(maxx-minx) for x in L]


def scale01_xy(xy):
    """Linearly rescale the xy-coordinates contained in the list `xy` so that
    they span the range [0,1]. The list `xy` is of the form
    [(x0,y0),(x1,y1),...].
    """
    X,Y = zip(*xy)
    return zip( scale01(X), scale01(Y) )


if __name__ == '__main__':
    
    # build a random network and connect it to cytoscape:
    G = networkx.random_geometric_graph(600, 0.05)
    C = Cytoscape(verbose=True, node_opacity=0.85, edge_opacity=0.85, network=G)
    
    # map node degree to color and size:
    C.map_node_color_continuous(G.degree(), "degree", match_border=True)#, ["#424FA4","#E6072A"])
    C.map_node_size(G.degree(), "degree", [20, 120])
    
    
    
    # do the nice layout and save the pdf:
    C.perform_yfiles_layout(wait=True)
    
    C.add_node_legend(name="degree", values=range(15), position=(1.0, 0.3))
    
    #C.set_node_labels(range(10),labels=["poop"]*10, fontsizes=[2*i+10 for i in range(10)])
    #C.rescale_fontsize(9)
    #C.save_pdf("foo.pdf")
    #C.quit()
