from IntermediateCode import *


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

    def gencode(self, tac):
        raise NotImplemented()

    def to_stack(self):
        raise NotImplemented()

    def add_edges_to_graph(self, graph, parent, counter):
        pass


class ASTProgram(ASTNode):

    def __init__(self, statements):
        """Encapsulates ASTStatements

        Arguments:
        statements - array of ASTStatement

        """
        self.statements = statements

    def wellformed(self):
        for s in self.statements:
            if not s.wellformed:
                return False
        return True

    def gencode(self):
        """Translates all statements to three address form

        Return:
        ICContext

        """
        icc = ICContext()
        stack = self._to_stack()
        while len(stack) != 0:
            s = stack.pop()
            s.gencode(icc)
        return icc

    def _to_stack(self):
        """Convert from internal tree representation to an
        in order stack representation

        Return:
        array of ASTNode in reverse order of operations

        """
        stack = []
        for s in self.statements:
            stack = s.to_stack() + stack
        return stack

    def add_edges_to_graph(self, graph, parent, counter):
        name = "program"
        graph.add_node(name, fillcolor=ASTProgram.COLOR)
        for s in self.statements:
            counter = s.add_edges_to_graph(graph, name, counter)
        return counter

    def to_png(self, program_name):
        """Output an AST using graphviz to a file called
        program_name.ast.png

        Arguments:
        program_name - name of program

        """
        # Only try if pygraphviz is available
        try:
            import pygraphviz as pgz
        except ImportError:
            return
        graph = pgz.AGraph(directed=True)
        graph.node_attr['style'] = 'filled'
        counter = 0
        self.add_edges_to_graph(graph, None, counter + 1)
        graph.draw('%s.ast.png' % program_name, prog='dot')


class ASTStatement(ASTNode):
    COLOR = "#FF7400"

    def __init__(self, p, value):
        """AST statement

        Arguments:
        p - pyl parser object
        value - things this statement does

        """
        self.p = p
        self.value = value

    def wellformed(self):
        return self.value.wellformed()

    def gencode(self, icc):
        return self.value.gencode(icc)

    def to_stack(self):
        return self.value.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'STMT')
        graph.add_node(name, fillcolor=ASTStatement.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)

    def __str__(self):
        return 'STMT: %s' % self.value


class ASTAssign(ASTNode):
    COLOR = '#269926'

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

    def wellformed(self):
        return self.right.wellformed()

    def gencode(self, icc):
        dest = Variable(self.left)
        icc.add_instruction(ICAssign(dest, icc.pop_var()))
        icc.push_var(dest)

    def to_stack(self):
        return [self] + self.right.to_stack()

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

    def __str__(self):
        return 'ASSIGN: %s = %s' % (self.left, self.right)


class ASTVariable(ASTNode):
    COLOR = '#4380D3'

    def __init__(self, p, value):
        """AST variable

        Arguments:
        p - pyl parser object
        value - name of variable

        """
        self.p = p
        self.value = value

    def wellformed(self):
        return True

    def gencode(self, icc):
        icc.push_var(Variable(self.value))

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTVariable.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'ID:%s' % self.value


class ASTPrint(ASTNode):
    COLOR = '#FFBF00'

    def __init__(self, p, value):
        """AST print statement

        Arguments:
        p - pyl parser object
        value - stuff to print

        """
        self.p = p
        self.value = value

    def wellformed(self):
        return self.value.wellformed()

    def gencode(self, icc):
        icc.add_instruction(ICPrint(icc.pop_var()))

    def to_stack(self):
        return [self] + self.value.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'print')
        graph.add_node(name, fillcolor=ASTPrint.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)

    def __str__(self):
        return 'PRINT: %s' % self.value


class ASTInput(ASTNode):
    COLOR = '#BF7130'

    def __init__(self, p):
        """AST input

        Arguments:
        p - pyl parser object

        """
        self.p = p

    def wellformed(self):
        return True

    def gencode(self, icc):
        var = icc.new_var()
        icc.add_instruction(ICInput(var))
        icc.push_var(var)

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'input')
        graph.add_node(name, fillcolor=ASTInput.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'INPUT'


class ASTInteger(ASTNode):
    COLOR = "#C0C0C0"

    def __init__(self, p, value):
        """AST integer

        Argumets:
        p - pyl parser object
        value - python integer value

        """
        self.p = p
        self.value = value

    def wellformed(self):
        if isinstance(self.value, int) and ((2 ** 31) <= self.value <= (2 ** 31 - 1)):
            return True
        else:
            raise ValueError('%s is out of bounds for 32 bit integer value' % self.value)

    def gencode(self, icc):
        icc.push_var(Integer(self.value))

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTInteger.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'INTEGER: %s' % self.value


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

    def wellformed(self):
        return self.value.wellformed()

    def gencode(self, icc):
        var = icc.new_var()
        icc.add_instruction(ICUnaryOp(var, icc.pop_var(), self.type))
        icc.push_var(var)

    def to_stack(self):
        return [self] + self.value.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.type)
        graph.add_node(name, fillcolor=ASTUnaryOp.COLOR)
        graph.add_edge(parent, name)
        return self.value.add_edges_to_graph(graph, name, counter + 1)

    def __str__(self):
        return 'NEGATE: %s' % self.value


class ASTBinaryOp(ASTNode):
    COLOR = '#009999'
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

    def wellformed(self):
        return self.left.wellformed() and self.right.wellformed()

    def gencode(self, icc):
        var = icc.new_var()
        arg2 = icc.pop_var()
        arg1 = icc.pop_var()
        icc.add_instruction(ICBinaryOp(var, arg1, arg2, self.type))
        icc.push_var(var)

    def to_stack(self):
        return [self] + self.right.to_stack() + self.left.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.type)
        graph.add_node(name, fillcolor=ASTBinaryOp.COLOR)
        graph.add_edge(parent, name)
        counter = self.left.add_edges_to_graph(graph, name, counter + 1)
        return self.right.add_edges_to_graph(graph, name, counter + 1)

    def __str__(self):
        return 'BINARY_OP %s: %s, %s' % (self.type, self.left, self.right)
