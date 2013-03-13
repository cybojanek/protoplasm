from IntermediateCode import *


class ASTContext(object):

    def __init__(self):
        self.defined = set()
        self.used = set()

    def get_undefined(self):
        return self.used.difference(self.defined)

    def clone(self):
        a = ASTContext()
        for x in self.defined:
            a.defined.add(x)
        for x in self.used:
            a.used.add(x)
        return a


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
        astc = ASTContext()
        for s in self.statements:
            if not s.wellformed(astc):
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


class ASTBlock(ASTNode):
    COLOR = "#FF7400"

    def __init__(self, p, statements):
        """AST block

        Arguments:
        p - pyl parser object
        statements - block statements

        """
        self.p = p
        self.statements = statements

    def wellformed(self, astc):
        for s in self.statements:
            if not s.wellformed(astc):
                return False
        return True

    def gencode(self, icc):
        for s in self.statements:
            s.gencode(icc)

    def to_stack(self):
        stack = []
        for s in self.statements:
            stack = s.to_stack() + stack
        return stack

    def add_edges_to_graph(self, graph, parent, counter):
        name = "block"
        graph.add_node(name, fillcolor=ASTBlock.COLOR)
        for s in self.statements:
            counter = s.add_edges_to_graph(graph, name, counter)
        return counter

    def __str__(self):
        return 'BLOCK: %s' % self.statements


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

    def wellformed(self, astc):
        return self.value.wellformed(astc)

    def gencode(self, icc):
        self.value.gencode(icc)

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

    def wellformed(self, astc):
        right_well = self.right.wellformed(astc)
        if not right_well:
            return False
        astc.defined.add(self.left)
        return True

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

    def wellformed(self, astc):
        if self.value not in astc.defined:
            print 'UNDEFINED VARIABLE: %s' % self
            return False
        astc.used.add(self.value)
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

    def wellformed(self, astc):
        return self.value.wellformed(astc)

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

    def wellformed(self, astc):
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

    def wellformed(self, astc):
        if isinstance(self.value, int) and (-(2 ** 31) <= self.value <= (2 ** 31 - 1)):
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
    TYPES = set(['-', '!'])

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
            raise TypeError('Unary operation: %s not supported' % self.type)

    def wellformed(self, astc):
        return self.value.wellformed(astc)

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
        return '%s: %s' % (self.type, self.value)


class ASTBinaryOp(ASTNode):
    COLOR = '#009999'
    TYPES = set(['+', '-', '*', '/', '%', '&&', '||', '==', '!=', '<', '<=',
                 '>', '>='])

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

    def wellformed(self, astc):
        return self.left.wellformed(astc) and self.right.wellformed(astc)

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


class ASTIf(ASTNode):
    COLOR = '#009999'

    def __init__(self, p, if_part, then_part, else_part=None):
        """AST if statements

        Arguments:
        p = pyl object
        if_part - algebraic expression of condition
        then_part - statement for then

        Keyword Arguments:
        else_part - optional else statement for if then

        """
        self.p = p
        self.if_part = if_part
        self.then_part = then_part
        self.else_part = else_part

    def wellformed(self, astc):
        # Then part can only check for usage, and not defined new variables
        # because its path is uncertain
        if not self.if_part.wellformed(astc):
            return False
        then_astc = astc.clone()
        if not self.then_part.wellformed(then_astc):
            return False
        if self.else_part is not None:
            else_astc = astc.clone()
            if not self.else_part.wellformed(else_astc):
                return False
            # Add only those which are defined in both paths
            for x in then_astc.defined.intersection(else_astc.defined):
                astc.defined.add(x)
        return True

    def gencode(self, icc):
        if_condition = icc.pop_var()
        current_block = icc.get_current_block()
        else_block = None
        # then_part -> to_stack, make extra block, after then_part finishes
        # get next block which will be the follow
        then_block = icc.new_block()
        then_stack = self.then_part.to_stack()
        while len(then_stack) != 0:
            s = then_stack.pop()
            s.gencode(icc)
        if self.else_part is not None:
            else_block = icc.new_block()
            else_stack = self.else_part.to_stack()
            while len(else_stack) != 0:
                s = else_stack.pop()
                s.gencode(icc)
        end_if_block = icc.new_block()
        # Add to follow and make ICIf adding it to the proper block
        current_block.add_follow(end_if_block)
        icc.add_instruction(ICIf(if_condition, then_block, else_block, end_if_block), current_block)

    def to_stack(self):
        # Let the if part happen before, so we can get the final result
        # Self will then make the recursive blocks
        return [self] + self.if_part.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'if then [else]')
        graph.add_node(name, fillcolor=ASTIf.COLOR)
        graph.add_edge(parent, name)
        counter = self.if_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.then_part.add_edges_to_graph(graph, name, counter + 1)
        if self.else_part is not None:
            counter = self.else_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'IF: [%s] THEN [%s]' % (self.if_part, self.then_part)
