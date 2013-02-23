

class UndirectedGraph(object):
    DEFAULT_COLOR = '#FFFFFF'

    def __init__(self):
        """New undirected graph

        """
        self.edges = {}
        self.node_colors = {}

    def add_node(self, node):
        """Add a node

        Arguments:
        node - node

        """
        if node not in self.edges:
            self.edges[node] = set()
        if node not in self.node_colors:
            self.node_colors[node] = UndirectedGraph.DEFAULT_COLOR

    def colorize(self, node, color):
        """Set a node to a color

        Arguments:
        node - node
        color - #FFFFFF type color

        """
        self.node_colors[node] = color

    def color(self, node):
        """Return the color of a node

        Return:
        node color
        """
        return self.node_colors[node]

    def remove_node(self, node):
        """Remove a node and return its set of edges

        Arguments:
        node - node

        Return:
        set of nodes

        """
        for x in self.edges[node]:
            self.edges[x].remove(node)
        edges = self.edges[node]
        del self.edges[node]
        del self.node_colors[node]
        return edges

    def add_edge(self, nodeA, nodeB):
        """Add an edge between two nodes.
        Adds nodes if they don't yet exist.
        Does not allow for nodeA == nodeB

        Arguments:
        nodeA - nodeA
        nodeB - nodeB

        """
        self.add_node(nodeA)
        if nodeA == nodeB:
            return
        self.add_node(nodeB)
        self.edges[nodeA].add(nodeB)
        self.edges[nodeB].add(nodeA)

    def add_edges(self, nodeA, other_nodes):
        """Add edges between nodeA to other_nodes

        Arguments:
        nodeA - node
        other_nodes - array of other nodes

        """
        self.add_node(nodeA)
        for node in other_nodes:
            self.add_edge(nodeA, node)

    def remove_edge(self, nodeA, nodeB):
        """Remove an edge between nodes A and B

        """
        self.edges[nodeA].remove(nodeB)
        self.edges[nodeB].remove(nodeA)

    def degree(self, node):
        """Return the degree of a node

        Return:
        integer of number of edges incident on node

        """
        return len(self.edges[node])

    def nodes(self):
        """Return a set of all node names

        """
        return set(self.edges.keys())

    def copy(self):
        g = UndirectedGraph()
        for nodeA in self.edges:
            g.add_node(nodeA)
            g.colorize(nodeA, self.color(nodeA))
            for nodeB in self.edges[nodeA]:
                g.add_edge(nodeA, nodeB)
        return g

    def to_png(self, file_name):
        """Output an graph of liveliness

        Arguments:
        file_name - output name for file

        """
        # Only try if pygraphviz is available
        try:
            import pygraphviz as pgz
        except ImportError:
            return
        graph = pgz.AGraph(directed=False)
        graph.node_attr['style'] = 'filled'
        for node in self.nodes():
            graph.add_node(node, fillcolor=self.node_colors[node])
        for nodeA in self.edges:
            for nodeB in self.edges[nodeA]:
                graph.add_edge(nodeA, nodeB)
        for i in ['circo', 'fdp']:
            graph.draw('%s_%s' % (i, file_name), prog=i)
