from IntermediateCode import *


class ASTContext(object):

    def __init__(self):
        """AST context during parsing.
        Keeps track of defined and used variables

        """
        self.defined = set()
        self.declared = set()
        self.used = set()

    def clone(self):
        """Clone this ASTContext

        Return:
        ASTContext with the same defined and used sets

        """
        a = ASTContext()
        for x in self.defined:
            a.defined.add(x)
        for x in self.used:
            a.used.add(x)
        for x in self.declared:
            a.declared.add(x)
        return a

    def __str__(self):
        return 'Declared: [%s], Defined: [%s]' % (','.join([repr(x) for x in self.declared]), ','.join([repr(x) for x in self.defined]))


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
        """Check language semantics.
        Undefined variables, integers out of range.

        """
        raise NotImplemented()

    def gencode(self, icc):
        """Generate IntermediateCode

        Arguments:
        icc - IntermediateCodeContext

        """
        raise NotImplemented()

    def to_stack(self):
        """Convert from internal tree representation to an
        in order stack representation

        Return:
        array of ASTNode in reverse order of operations

        """
        raise NotImplemented()

    def add_edges_to_graph(self, graph, parent, counter):
        """Add nodes and edges to a graph

        Arguments:
        graph - pygraphviz object
        parent - name of parent
        counter - unique node id counter

        Return:
        counter

        """
        pass


class ASTProgram(ASTNode):

    def __init__(self, declarations, statements):
        """Encapsulates ASTStatements

        Arguments:
        declarations - array of ASTDeclare
        statements - array of ASTStatement

        """
        self.declarations = declarations
        self.statements = statements

    def wellformed(self):
        astc = ASTContext()
        for d in self.declarations:
            if not d.wellformed(astc):
                return False
        for s in self.statements:
            if not s.wellformed(astc):
                return False
        return True

    def gencode(self):
        icc = ICContext()
        stack = self.to_stack()
        while len(stack) != 0:
            s = stack.pop()
            s.gencode(icc)
        return icc

    def to_stack(self):
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

    def __str__(self):
        return 'PROGRAM:\n%s\n%s' % ('\n'.join([str(x) for x in self.declarations]), '\n'.join([str(x) for x in self.statements]))


class ASTBlock(ASTNode):
    COLOR = "#FF7400"

    def __init__(self, p, declarations, statements):
        """AST block

        Arguments:
        p - pyl parser object
        declarations - declarations
        statements - block statements

        """
        self.p = p
        self.declarations = declarations
        self.statements = statements

    def wellformed(self, astc):
        for d in self.declarations:
            if not d.wellformed(astc):
                return False
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


class ASTDeclareList(ASTNode):
    COLOR = ASTNode.COLOR

    def __init__(self, p, dec_type, declarations):
        """AST Declaration list

        Arguments:
        p - pyl parser object
        dec_type - declaration type (ignored for now)
        declarations - array of variable names
        """
        self.p = p
        self.dec_type = dec_type
        self.declarations = declarations

    def wellformed(self, astc):
        for d in self.declarations:
            if not d.wellformed(astc):
                return False
        return True

    def gencode(self, icc):
        pass

    def to_stack(self):
        stack = []
        for s in self.declarations:
            stack = s.to_stack() + stack
        return stack

    def __str__(self):
        return 'DECLARE: %s %s' % (self.dec_type, ','.join([str(x) for x in self.declarations]))


class ASTDeclareVariable(ASTNode):
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
        astc.declared.add(self.value)
        return True

    def gencode(self, icc):
        pass

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTDeclareVariable.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return '%s' % self.value


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
        if self.left.value not in astc.declared:
            print astc
            print "%s assigned but not declared!" % self.left.value
            return False
        astc.defined.add(self.left.value)
        return True

    def gencode(self, icc):
        dest = Variable(self.left.value)
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
        if self.value in astc.declared and self.value not in astc.defined:
            print '%s declared but used before definition!' % (self.value)
            return False
        elif self.value not in astc.declared:
            print '%s not declared!' % (self.value)
            return False
        elif self.value not in astc.defined:
            print '%s declared but not defined!' % (self.value)
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


class ASTBoolean(ASTNode):
    COLOR = "#C0C0C0"

    def __init__(self, p, value):
        """AST integer

        Argumets:
        p - pyl parser object
        value - python boolean value

        """
        self.p = p
        self.value = value

    def wellformed(self, astc):
        return True

    def gencode(self, icc):
        if self.value:
            icc.push_var(Integer(1))
        else:
            icc.push_var(Integer(0))

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTBoolean.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'BOOLEAN: %s' % self.value


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
        if isinstance(self.value, int) and \
           (-(2 ** 31) <= self.value <= (2 ** 31 - 1)):
            return True
        else:
            raise ValueError('%s is out of bounds for 32 bit integer value' % (
                self.value))

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
        if not self.if_part.wellformed(astc):
            return False
        # Then part can only check for usage, and not defined new variables
        # because its path is uncertain
        then_astc = astc.clone()
        if not self.then_part.wellformed(then_astc):
            return False
        # If we have an else part then also make an astc clone
        if self.else_part is not None:
            else_astc = astc.clone()
            if not self.else_part.wellformed(else_astc):
                return False
            # Add only those which are defined in *both* paths
            for x in then_astc.defined.intersection(else_astc.defined):
                astc.defined.add(x)
            for x in then_astc.declared.intersection(else_astc.declared):
                astc.declared.add(x)
        return True

    def gencode(self, icc):
        # The AE was evaluated on the stack before use so get the result var
        if_var = icc.pop_var()
        # Store reference to current block
        current_block = icc.get_current_block()
        # then_part -> to_stack, make extra block, after then_part finishes
        # get next block which will be the follow
        # current_block --> then_block
        then_block = icc.new_block()
        then_stack = self.then_part.to_stack()
        while len(then_stack) != 0:
            s = then_stack.pop()
            s.gencode(icc)
        if self.else_part is None:
            # No else block, so make a new block for ending of if
            else_block = None
            # last block from stack --> end_if_block
            end_if_block = icc.new_block()
            # Add to follow, bc current_block --> end_if_block
            current_block.add_follow(end_if_block)
        else:
            # What's happening here you might ask...
            # If the then block had other statements inside of it that
            # created a new block...then our then block (which we care about
            # only for the purpose of putting in the unconditional branch)
            # is now something new. Because its part of the same scope,
            # it logically follows, so thats why we add the follow
            # and change the then_block pointer
            # The then_block refers to the block we're jumping OUT OF
            # and NOT the block we're jumping INTO (bc we never do)
            if icc.get_current_block() != then_block:
                then_block.add_follow(icc.get_current_block())
                then_block = icc.get_current_block()
            # then_block !-> else_block
            else_block = icc.new_block(auto_follow=False)
            else_stack = self.else_part.to_stack()
            while len(else_stack) != 0:
                s = else_stack.pop()
                s.gencode(icc)
            # else_block --> end_if_block
            end_if_block = icc.new_block()
            # then_block --> end_if_block
            then_block.add_follow(end_if_block)
            # current_block --> else_block
            current_block.add_follow(else_block)
        # Now add the instructions, starting with the if AE part added to the
        # original first block
        icc.add_instruction(ICIf(if_var, then_block, else_block, end_if_block),
                            current_block)

    def to_stack(self):
        # Let the if part happen before, so we can get the final result
        # Self will then make the recursive blocks
        return [self] + self.if_part.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'if then%s' % (
            '' if self.else_part is None else ' else'))
        graph.add_node(name, fillcolor=ASTIf.COLOR)
        graph.add_edge(parent, name)
        counter = self.if_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.then_part.add_edges_to_graph(graph, name, counter + 1)
        if self.else_part is not None:
            counter = self.else_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'IF: [%s] THEN [%s]' % (self.if_part, self.then_part)


class ASTWhile(ASTNode):
    COLOR = '#009999'

    def __init__(self, p, while_part, do_part):
        """AST if statements

        Arguments:
        p = pyl object
        while_part - condition while the loop runs
        do_part - do_part to execute in while loop

        """
        self.p = p
        self.while_part = while_part
        self.do_part = do_part

    def wellformed(self, astc):
        # Then part can only check for usage, and not defined new variables
        # because its path is uncertain
        if not self.while_part.wellformed(astc):
            return False
        stmt_astc = astc.clone()
        if not self.do_part.wellformed(stmt_astc):
            return False
        return True

    def gencode(self, icc):
        # Build up while_part
        while_part_block = icc.new_block()
        while_part_stack = self.while_part.to_stack()
        while len(while_part_stack) != 0:
            s = while_part_stack.pop()
            s.gencode(icc)
        # The AE was just parsed and stored here
        while_var = icc.pop_var()
        # while_part --> do_part
        do_part_block = icc.new_block()
        do_part_stack = self.do_part.to_stack()
        while len(do_part_stack) != 0:
            s = do_part_stack.pop()
            s.gencode(icc)
        # Block at the end of the then statement
        # Might be different from do_part, if other blocks added
        # Need this to tell this block to jump back to the while_part_block
        end_if_block = icc.get_current_block()
        # Do not auto_follow because next_block does *not* follow the
        # statements in the while loop
        next_block = icc.new_block(auto_follow=False)
        # while_part --> next_block
        while_part_block.add_follow(next_block)
        # do_part --> while_part (loop back)
        do_part_block.add_follow(while_part_block)
        # Add to original block
        icc.add_instruction(ICWhile(while_var, while_part_block,
                            end_if_block, next_block), while_part_block)

    def to_stack(self):
        # Self will handle other statements
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'while')
        graph.add_node(name, fillcolor=ASTIf.COLOR)
        graph.add_edge(parent, name)
        counter = self.while_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.do_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'WHILE: [%s] DO [%s]' % (self.while_part, self.do_part)
