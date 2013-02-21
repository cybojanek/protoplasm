import pygraphviz as pgz
import tokenize


def proto_tokenize(file_name=None, lines=None):
    """Use python's tokenizer to tokenize a chunk of proto code.
    Uses file_name if not None, otherwise lines

    Keyword Arguments:
    file_name - name of proto file
    lines - array of new line termianted strings

    """
    tokens = []
    if file_name is not None:
        g = tokenize.generate_tokens(open(file_name, 'r').readline)
    elif lines is not None:
        it = iter(lines).next
        g = tokenize.generate_tokens(it)
    for toknum, tokval, start, end, line in g:
        # Don't add newlines: we're looking for ;
        if toknum in (tokenize.NL, tokenize.NEWLINE):
            continue
        tokens.append([toknum, tokval, start, end, line])
    for x in tokens:
        tokenize.printtoken(*x)
    return tokens


class ParseTreeNode(object):
    """N-arry tree for keeping track of parse tree
    All children are either ParseTreeNodes or tuples of (obj, type)
    Can output a colored graph of parse tree to an image
    """
    # Node Types
    TYPES = ('statement_sequence', 'assign', 'print', 'input', 'binary_op',
        'single_op', 'paranthesis', 'integer', 'variable')
    STATEMENT_SEQUENCE, ASSIGN, PRINT, INPUT, BINARY_OP, SINGLE_OP, \
        PARANTHESIS, INTEGER, VARIABLE = TYPES
    # Node type colors gor graphviz
    GRAPH_COLORS = {
        STATEMENT_SEQUENCE: '#FF6C00',
        ASSIGN: '#9BED00',
        PRINT: '#BE008A',
        INPUT: '#BE008A',
        BINARY_OP: '#0776A0',
        SINGLE_OP: '#0776A0',
        PARANTHESIS: '#0B5FA5',
        INTEGER: '#FFFFFF',
        VARIABLE: '#FFFFFF'
    }

    def __init__(self, value, type):
        """Create a new ParseTreeNode

        Arguments:
        value - node name
        type - one of ParseTreeNode.TYPES

        """
        self.value = value
        self.type = type
        self.children = []

    def add_child(self, child, type=None):
        """Add a child to this node. Order preserving, without limit.
        Raises TypeError if child and or type is not valid

        Arguments:
        child - object to append to childs (assumes that child is either a
            ParseTreeNode or already a (child, type) tuple)

        Keyword Arguments:
        type - if type is specified, then a tuple of (child, type) is added

        """
        if type:
            if type not in ParseTreeNode.TYPES:
                raise TypeError("%r is not a ParseTreeNode type" % type)
            self.children.append((child, type))
        elif isinstance(child, ParseTreeNode):
            self.children.append(child)
        else:
            try:
                if child[1] not in ParseTreeNode.TYPES:
                    raise TypeError("%r is not a ParseTreeNode type" % (
                        child[1]))
            except (IndexError, TypeError):
                raise TypeError("%r is not a len-2 tuple/list" % child)
            self.children.append(child)

    def pop_child(self):
        """Remove and return the last child

        Return:
        last child from children of this node

        """
        return self.children.pop()

    def __str__(self):
        return "%s -> [%s]" % (self.value, ','.join(
            [str(x) for x in self.children]))

    def add_edges_to_graph(self, graph, counter):
        """Loop through children in order and add them to a pygraphviz AGraph.
        Each node receives a prefix number to avoid name collision.
        If calling for the first time, counter should be 0

        Arguments:
        graph - pygraphviz AGraph
        counter - prefix for this node

        Return:
        integer value of counter used for last child

        """
        # Set parent name
        parent = "%s\n%s" % (counter, self.value)
        # Add parent and set color
        graph.add_node(parent, fillcolor=ParseTreeNode.GRAPH_COLORS[self.type])
        # Loop through all children
        for child in self.children:
            # Increment counter for children
            counter += 1
            # Set child name and type
            if isinstance(child, ParseTreeNode):
                child_name = "%s\n%s" % (counter, child.value)
                child_type = child.type
            else:
                child_name = "%s\n%s" % (counter, child[0])
                child_type = child[1]
            # Add the node and fill color
            graph.add_node(child_name,
                fillcolor=ParseTreeNode.GRAPH_COLORS[child_type])
            # Add the edge
            graph.add_edge(parent, child_name)
            # If the child is a tree, then recurse down into it
            if isinstance(child, ParseTreeNode):
                counter = child.add_edges_to_graph(graph, counter)
        return counter

    def graphvizify(self):
        """Generate a parse tree graph using pygraphviz
        """
        g = pgz.AGraph(directed=True)
        g.node_attr['style'] = 'filled'
        self.add_edges_to_graph(g, 0)
        g.draw('parse_tree.png', prog='dot')


class ProtoParser(object):

    @staticmethod
    def RaiseError(exp, msg, x):
        """Raise a syntax checker exception

        Arguments:
        exp - exception type to raise
        msg - message to add
        x - tokenizer token for more info

        """
        toknum, tokval, start, end, line = x[0]
        raise exp('%s near line %s, column %s: %r' %
            (msg, start[0], start[1], line))

    SUM_OP = set(['+', '-'])
    PROD_OP = set(['*', '/', '%'])

    def __init__(self, tokens):
        """Create a syntax checker for a list of tokens.
        Implements CFG from Homework 2

        Arguments:
        tokens - list of tuples (toknum, tokval, start, end, line)

        """
        self.tokens = tokens
        self.def_vars = set()
        self.parse_tree = ParseTreeNode(None, ParseTreeNode.STATEMENT_SEQUENCE)

    def check(self):
        """Start parser and check for syntax errors.
        Raise SyntaxError on bad syntax.

        """
        self.parse_PRGM(self.tokens, self.parse_tree)

    def parse_PRGM(self, x, root):
        """
        Pgm -> Stmt Pgm
            | Stmt
        """
        rest = self.parse_STMT(x, root)
        if not rest:
            return True
        else:
            return self.parse_PRGM(rest, root)

    def parse_STMT(self, x, root):
        """
        Stmt -> Assign
             | Print
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        # Peek at print
        if toknum == tokenize.NAME and tokval == 'print':
            return self.parse_PRINT(x, root)
        # Peek at variable
        elif toknum == tokenize.NAME:
            return self.parse_ASSIGN(x, root)
        # Peek at end of tokens
        elif toknum == tokenize.ENDMARKER:
            return []
        else:
            ProtoParser.RaiseError(SyntaxError, 'Incorrent STMT!', x)

    def parse_PRINT(self, x, root):
        """
        Print -> 'print' '(' AE ')' ';'
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME and tokval == 'print':
            a = ParseTreeNode(tokval, ParseTreeNode.PRINT)
            root.add_child(a)
            return self.consume_SEMICOLON(self.consume_RPAREN(self.parse_AE(
                self.consume_LPAREN(tail), a)))
        else:
            ProtoParser.RaiseError(SyntaxError, 'Expected PRINT', x)

    def parse_ASSIGN(self, x, root):
        """
        Assign -> var '=' Rhs ';'
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME:
            a = ParseTreeNode('=', ParseTreeNode.ASSIGN)
            root.add_child(a)
            a.add_child(tokval, ParseTreeNode.VARIABLE)
            # Add LHS variable
            rest = self.consume_SEMICOLON(self.parse_RHS(
                self.consume_EQUAL(tail), a))
            self.def_vars.add(tokval)
            return rest
        else:
            ProtoParser.RaiseError(SyntaxError, 'Expected NAME', x)

    def parse_RHS(self, x, root):
        """
        Rhs -> 'input' '(' ')'
            | AE
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME and tokval == 'input':
            root.add_child(tokval, ParseTreeNode.INPUT)
            return self.consume_RPAREN(self.consume_LPAREN(tail))
        else:
            return self.parse_AE(x, root)

    def parse_AE(self, x, root):
        """
        AE -> T SumOp AE
           | T
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        rest = self.parse_T(x, root)
        if rest and rest[0][1] in ProtoParser.SUM_OP:
            a = ParseTreeNode(rest[0][1], ParseTreeNode.BINARY_OP)
            a.add_child(root.pop_child())
            root.add_child(a)
            return self.parse_AE(rest[1:], a)
        else:
            return rest

    def parse_T(self, x, root):
        """
        T -> F ProdOp T
          | F
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        rest = self.parse_F(x, root)
        if rest and rest[0][1] in ProtoParser.PROD_OP:
            a = ParseTreeNode(rest[0][1], ParseTreeNode.BINARY_OP)
            a.add_child(root.pop_child())
            root.add_child(a)
            return self.parse_T(rest[1:], a)
        else:
            return rest

    def parse_F(self, x, root):
        """
        F -> '-' F
          | '(' AE ')'
          | intconst
          | var
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.OP and tokval == '-':
            a = ParseTreeNode(tokval, ParseTreeNode.SINGLE_OP)
            root.add_child(a)
            return self.parse_F(tail, a)
        elif toknum == tokenize.OP and tokval == '(':
            a = ParseTreeNode('( )', ParseTreeNode.PARANTHESIS)
            root.add_child(a)
            return self.consume_RPAREN(self.parse_AE(tail, a))
        elif toknum == tokenize.NAME:
            root.add_child(tokval, ParseTreeNode.VARIABLE)
            # Check RHS variable
            if tokval not in self.def_vars:
                ProtoParser.RaiseError(
                    NameError, 'Undefined variable: %s' % tokval, x)
            return tail
        elif toknum == tokenize.NUMBER and tokval.isdigit():
            root.add_child(tokval, ParseTreeNode.INTEGER)
            return tail
        else:
            ProtoParser.RaiseError(SyntaxError, 'Bad statement!', x)

    def consume_LPAREN(self, x):
        """Consume a LPAREN from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == '(':
            return tail
        else:
            ProtoParser.RaiseError(SyntaxError, 'Missing LPAREN', x)

    def consume_RPAREN(self, x):
        """Consume a RPAREN from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == ')':
            return tail
        else:
            ProtoParser.RaiseError(SyntaxError, 'Missing RPAREN', x)

    def consume_EQUAL(self, x):
        """Consume an EQUAL from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == '=':
            return tail
        else:
            ProtoParser.RaiseError(SyntaxError, 'Missing EQUAL sign', x)

    def consume_SEMICOLON(self, x):
        """Consume a SEMICOLON from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == ';':
            return tail
        else:
            ProtoParser.RaiseError(SyntaxError,
                'Missing SEMICOLON sign', x)