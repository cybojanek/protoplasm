

def ast_to_png(statements, file_name):
    """Output an AST using graphviz

    Arguments:
    statements - list of ASTStatement
    file_name - output name for file

    """
    # Only try if pygraphviz is available
    try:
        import pygraphviz as pgz
    except ImportError:
        return
    graph = pgz.AGraph(directed=True)
    graph.node_attr['style'] = 'filled'
    counter = 0
    for s in statements:
        counter = s.add_edges_to_graph(graph, 'Program', counter + 1)
    graph.draw(file_name, prog='dot')


class ASTNode(object):
    """ASTNode which represents different AST TYPES
    Exepects to implement wellformed, gencode
    add_edges_to_graph is optional for graph pygraphviz graph generation
    The default COLOR attribute is white
    """
    COLOR = "#FFFFFF"

    def __init__(self):
        raise NotImplemented()

    def wellformed(self):
        raise NotImplemented()

    def gencode(self):
        raise NotImplemented()

    def add_edges_to_graph(self, graph, parent, counter):
        pass


class ASTStatement(ASTNode):
    COLOR = "#FF0000"

    def __init__(self, p, value):
        """AST statement

        Arguments:
        p - pyl parser object
        value - things this statement does

        """
        self.p = p
        self.value = value

    def __str__(self):
        return 'STMT: %s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'STMT')
        graph.add_node(name, fillcolor=ASTStatement.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)


class ASTAssign(ASTNode):

    def __init__(self, p, left, right):
        """AST assignment operation

        Arguments:
        p - pyl parser object
        left - variable being assigned to
        right - stuff being assigned to variable

        """
        self.p = p
        self.left = left
        self.right = right

    def __str__(self):
        return 'ASSIGN: %s = %s' % (self.left, self.right)

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, '=')
        counter += 1
        left = "%s\n%s" % (counter, self.left)
        graph.add_node(name, fillcolor=ASTAssign.COLOR)
        graph.add_edge(parent, name)
        # Left assign is always variable
        graph.add_node(left, fillcolor=ASTVariable.COLOR)
        graph.add_edge(name, left)
        return self.right.add_edges_to_graph(graph, name, counter + 1)


class ASTVariable(ASTNode):

    def __init__(self, p, value):
        """AST variable

        Arguments:
        p - pyl parser object
        value - name of variable

        """
        self.p = p
        self.value = value

    def __str__(self):
        return 'ID:%s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTVariable.COLOR)
        graph.add_edge(parent, name)
        return counter


class ASTPrint(ASTNode):

    def __init__(self, p, value):
        """AST print statement

        Arguments:
        p - pyl parser object
        value - stuff to print

        """
        self.p = p
        self.value = value

    def __str__(self):
        return 'PRINT: %s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'print')
        graph.add_node(name, fillcolor=ASTPrint.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)


class ASTInput(ASTNode):

    def __init__(self, p):
        """AST input

        Arguments:
        p - pyl parser object

        """
        self.p = p

    def __str__(self):
        return 'INPUT'

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'input')
        graph.add_node(name, fillcolor=ASTInput.COLOR)
        graph.add_edge(parent, name)
        return counter


class ASTInteger(ASTNode):

    def __init__(self, p, value):
        """AST integer

        Argumets:
        p - pyl parser object
        value - python integer value

        """
        self.p = p
        self.value = value

    def __str__(self):
        return 'INTEGER: %s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTInteger.COLOR)
        graph.add_edge(parent, name)
        return counter


class ASTUnaryOp(ASTNode):
    TYPES = '-'
    NEGATE = TYPES

    def __init__(self, p, value, type):
        """AST unary operator (ie, -, ~).
        Throws TypeError if type not in ASTUnaryOp.TYPES

        Arguments:
        p - pyl parser object
        value - ASTNode to use op on
        type - one of ASTUnaryOp.TYPES

        """
        self.p = p
        self.value = value
        self.type = type
        if self.type not in ASTUnaryOp.TYPES:
            raise TypeError('Unary operation: %r not supported')

    def __str__(self):
        return 'NEGATE: %s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.type)
        graph.add_node(name, fillcolor=ASTUnaryOp.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)


class ASTParen(ASTNode):
    """NOTE: might not actualy be needed"""

    def __init__(self, p, value):
        """AST paren - holds a reference to a child

        Arguments:
        p - pyl parser object
        value - ASTNode child

        """
        self.p = p
        self.value = value

    def __str__(self):
        return 'PAREN: %s' % self.value

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, '( )')
        graph.add_node(name, fillcolor=ASTParen.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)


class ASTBinaryOp(ASTNode):
    TYPES = '-', '+', '*', '/', '%'
    MINUS, PLUS, TIMES, DIVIDE, MODULUS = TYPES

    def __init__(self, p, left, right, type):
        """AST binary operator (ie, +, -, *).
        Throws TypeError if type not in ASTBinaryOp.TYPES

        Arguments:
        p - pyl object
        left - left side
        right - right side
        type - one of ASTBinaryOp.TYPES

        """
        self.p = p
        self.left, self.right = left, right
        self.type = type
        if self.type not in ASTBinaryOp.TYPES:
            raise TypeError('Binary operation: %r not supported')

    def __str__(self):
        return 'BINARY_OP %s: %s, %s' % (self.type, self.left, self.right)

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.type)
        graph.add_node(name, fillcolor=ASTBinaryOp.COLOR)
        graph.add_edge(parent, name)
        counter = self.right.add_edges_to_graph(graph, name, counter + 1)
        return self.left.add_edges_to_graph(graph, name, counter + 1)
