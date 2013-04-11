from IntermediateCode import *
import inspect

NODE_COLORS = {
    'ASTAssign': '#269926',
    'ASTBinaryOp': '#CC0909',
    'ASTBlock': '#FF7400',
    'ASTBoolean': '#C0C0C0',
    'ASTDeclareList': '#38a0ad',
    'ASTDeclareVariable': '#4380D3',
    'ASTDoWhile': '#009999',
    'ASTFor': '#009999',
    'ASTIf': '#FFCA7A',
    'ASTInput': '#BF7130',
    'ASTInteger': '#C0C0C0',
    'ASTNode': '#FFFFFF',
    'ASTPrint': '#FFBF00',
    'ASTStatement': '#FF7400',
    'ASTUnaryOp': '#FFFFFF',
    'ASTVariable': '#4380D3',
    'ASTWhileDo': '#009999',
    'ASTArray': '#fff'
}


class ASTContext(object):

    def __init__(self):
        """AST context during parsing.
        Keeps track of defined and used variables

        """
        self.defined = set()
        self.declared = set()
        self.used = set()
        self.rename = dict()
        self.counter = 0

    def get_new_var_name(self, name):
        n = '&%s%s' % (name, self.counter)
        self.counter += 1
        return n

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
        for k, v in self.rename.iteritems():
            a.rename[k] = v
        a.counter = self.counter
        return a

    def __str__(self):
        return 'Declared: [%s], Defined: [%s]' % (
               ','.join([repr(x) for x in self.declared]),
               ','.join([repr(x) for x in self.defined]))


class ASTNode(object):
    """ASTNode which represents different AST TYPES
    Exepects to implement wellformed, gencode
    add_edges_to_graph is optional for graph pygraphviz graph generation
    The default COLOR attribute is white
    """
    COLOR = NODE_COLORS['ASTNode']

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
        for d in self.declarations:
            counter = d.add_edges_to_graph(graph, name, counter)
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


class ASTAssign(ASTNode):
    COLOR = NODE_COLORS['ASTAssign']

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
        if not self.right.wellformed(astc):
           return False
        if not isinstance(self.left, ASTArray):
            if self.left.value in astc.rename:
                self.left.value = astc.rename[self.left.value]
            if self.left.value not in astc.declared:
                print astc
                print "%s assigned but not declared!" % self.left.value
                return False
            astc.defined.add(self.left.value)
        return True


    def gencode(self, icc):
        if not isinstance(self.left, ASTArray):
            src = icc.pop_var()
            dest = icc.pop_var()

            icc.add_instruction(ICAssign(dest, src))
            icc.push_var(dest)
        elif isinstance(self.left, ASTArray):
            src = icc.pop_var()      # value to put into array
            rvalue = icc.pop_var()   # pop the rvalue off the stack

            icc.add_instruction(ICStoreWord(src, rvalue._base, Integer(0), rvalue._elem))
            icc.push_var(src)



    def to_stack(self):
        return [self] + self.right.to_stack() + self.left.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, '=')
        counter += 1
        left = "%s\n%s" % (counter, self.left.value)
        graph.add_node(name, fillcolor=ASTAssign.COLOR)
        graph.add_edge(parent, name)
        # Left assign is always variable
        graph.add_node(left, fillcolor=ASTVariable.COLOR)
        graph.add_edge(name, left)
        return self.right.add_edges_to_graph(graph, name, counter + 1)

    def __str__(self):
        return 'ASSIGN: %s = %s' % (self.left, self.right)


class ASTBinaryOp(ASTNode):
    COLOR = NODE_COLORS['ASTBinaryOp']
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


class ASTBlock(ASTNode):
    COLOR = NODE_COLORS['ASTBlock']

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
        name = "%s\nBLOCK" % (counter)
        graph.add_node(name, fillcolor=ASTBlock.COLOR)
        graph.add_edge(parent, name)
        for d in self.declarations:
            counter = d.add_edges_to_graph(graph, name, counter)
        for s in self.statements:
            counter = s.add_edges_to_graph(graph, name, counter)
        return counter

    def __str__(self):
        return 'BLOCK: %s' % self.statements


class ASTBoolean(ASTNode):
    COLOR = NODE_COLORS['ASTBoolean']

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


class ASTDeclareList(ASTNode):
    COLOR = NODE_COLORS['ASTDeclareList']

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

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.dec_type)
        graph.add_node(name, fillcolor=ASTDeclareList.COLOR)
        graph.add_edge(parent, name)
        for d in self.declarations:
            counter = d.add_edges_to_graph(graph, name, counter)
        return counter

    def __str__(self):
        return 'DECLARE: %s %s' % (self.dec_type, ','.join([str(x) for x in self.declarations]))


class ASTDeclareVariable(ASTNode):
    COLOR = NODE_COLORS['ASTDeclareVariable']

    def __init__(self, p, value, dimensions):
        """AST variable

        Arguments:
        p - pyl parser object
        value - name of variable
        dimensions - number of dimensions

        """
        self.p = p
        self.value = value
        self.dimensions = dimensions

    def wellformed(self, astc):
        if self.value not in astc.declared:
            astc.declared.add(self.value)
        else:
            new_name = astc.get_new_var_name(self.value)
            astc.rename[self.value] = new_name
            self.value = new_name
            astc.declared.add(self.value)
        return True

    def gencode(self, icc):
        pass

    def to_stack(self):
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s[%dd]" % (counter, self.value, self.dimensions)
        graph.add_node(name, fillcolor=ASTDeclareVariable.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return '%s' % self.value


class ASTDoWhile(ASTNode):
    COLOR = NODE_COLORS['ASTDoWhile']

    def __init__(self, p, do_part, while_part):
        """AST if statements

        Arguments:
        p = pyl object
        do_part - do_part to execute in while loop
        while_part - condition while the loop runs

        """
        self.p = p
        self.do_part = do_part
        self.while_part = while_part

    def wellformed(self, astc):
        # Can do part variables be used in while part?
        # This assumes so
        stmt_astc = astc.clone()
        if not self.do_part.wellformed(stmt_astc):
            return False
        if not self.while_part.wellformed(stmt_astc):
            return False
        astc.counter = stmt_astc.counter
        return True

    def gencode(self, icc):
        # Build up do part
        do_part_block = icc.new_block()
        do_part_stack = self.do_part.to_stack()
        while len(do_part_stack) != 0:
            s = do_part_stack.pop()
            s.gencode(icc)
        # Build up while_part
        while_part_block = icc.new_block()
        while_part_stack = self.while_part.to_stack()
        while len(while_part_stack) != 0:
            s = while_part_stack.pop()
            s.gencode(icc)
        # The AE was just parsed and stored here
        while_var = icc.pop_var()
        # Next block after while loop
        next_block = icc.new_block()
        # while_part --> do_part
        while_part_block.add_follow(do_part_block)
        # Add to original block
        icc.add_instruction(ICDoWhile(do_part_block, while_var,
                            while_part_block, next_block),
                            while_part_block)

    def to_stack(self):
        # Self will handle other statements
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'do...while')
        graph.add_node(name, fillcolor=ASTDoWhile.COLOR)
        graph.add_edge(parent, name)
        counter = self.do_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.while_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'DO: [%s] WHILE [%s]' % (self.do_part, self.while_part)


class ASTFor(ASTNode):
    COLOR = NODE_COLORS['ASTFor']

    def __init__(self, p, init_part, cond_part, incr_part, stmt_part):
        """AST if statements

        Arguments:
        p = pyl object
        init_part - expression run on start of for loop
        cond_part - condition check of for loop
        incr_part - expression run on every loop
        stmt_part - statement in for loop

        """
        self.p = p
        self.init_part = init_part
        self.cond_part = cond_part
        self.incr_part = incr_part
        self.stmt_part = stmt_part

    def wellformed(self, astc):
        if not self.init_part.wellformed(astc):
            return False
        if not self.cond_part.wellformed(astc):
            return False
        if not self.incr_part.wellformed(astc):
            return False
        if not self.stmt_part.wellformed(astc):
            return False
        return True

    def gencode(self, icc):
        # Build up while_part
        cond_part_block = icc.new_block()
        cond_part_stack = self.cond_part.to_stack()
        while len(cond_part_stack) != 0:
            s = cond_part_stack.pop()
            s.gencode(icc)
        # The AE was just parsed and stored here
        cond_var = icc.pop_var()
        # cond_part --> stmt_part
        stmt_part_block = icc.new_block()
        stmt_part_stack = self.stmt_part.to_stack()
        while len(stmt_part_stack) != 0:
            s = stmt_part_stack.pop()
            s.gencode(icc)
        # stmt_part --> incr_part
        incr_part_block = icc.new_block()
        incr_part_stack = self.incr_part.to_stack()
        while len(incr_part_stack) != 0:
            s = incr_part_stack.pop()
            s.gencode(icc)
        # Block at the end of the stmt part
        # Might be different from incr_part, if other blocks added
        # Need this to tell this block to jump back to the cond_part
        end_for_block = icc.get_current_block()
        # Do not auto_follow because next_block does *not* follow the
        # statements in the while loop
        next_block = icc.new_block(auto_follow=False)
        # cond_part --> next_block
        cond_part_block.add_follow(next_block)
        # end_for --> cond_part (loop back)
        end_for_block.add_follow(cond_part_block)
        # Add to original block
        icc.add_instruction(ICFor(cond_var, cond_part_block, end_for_block,
                            next_block), cond_part_block)

    def to_stack(self):
        # Self will handle other statements
        return [self] + self.init_part.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'for...')
        graph.add_node(name, fillcolor=ASTFor.COLOR)
        graph.add_edge(parent, name)
        counter = self.init_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.cond_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.incr_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.stmt_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'for [%s; %s; %s] do...' % (self.init_part, self.cond_part,
                                           self.incr_part)


class ASTIf(ASTNode):
    COLOR = NODE_COLORS['ASTIf']

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
        astc.counter = then_astc.counter
        # If we have an else part then also make an astc clone
        if self.else_part is not None:
            else_astc = astc.clone()
            if not self.else_part.wellformed(else_astc):
                return False
            astc.counter = else_astc.counter
            # Add only those which are defined in *both* paths
            for x in then_astc.defined.intersection(else_astc.defined):
                # And make sure they weren't redefined
                if x not in then_astc.rename and x not in else_astc.rename:
                    astc.defined.add(x)
            # for x in then_astc.declared.intersection(else_astc.declared):
            #     astc.declared.add(x)
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
            counter = self.else_part.add_edges_to_graph(
                graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'IF: [%s] THEN [%s]' % (self.if_part, self.then_part)


class ASTInput(ASTNode):
    COLOR = NODE_COLORS['ASTInput']

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
    COLOR = NODE_COLORS['ASTInteger']

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


class ASTAlloc(ASTNode):
    COLOR = NODE_COLORS['ASTInteger']

    def __init__(self, p, size):
        """AST integer

        Argumets:
        p - pyl parser object
        size - size of array

        """
        self.p = p
        self.size = size

    def wellformed(self, astc):
        return self.size.wellformed(astc);

    def gencode(self, icc):
        var = icc.new_var();
        size = icc.pop_var();
        
        icc.add_instruction(ICAllocMemory(var, size))

        icc.add_instruction(ICStoreWord(size, var, Integer(0)))

        icc.push_var(var);

    def to_stack(self):
        return [self] + [self.size]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\nalloc(%s)" % (counter, self.size)
        graph.add_node(name, fillcolor=ASTInteger.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'ALLOC: %s' % self.size

class ASTArray(ASTNode):
    COLOR = NODE_COLORS['ASTVariable']

    def __init__(self, p, value, element):
        """AST variable

        Arguments:
        p - pyl parser object
        value - name of variable

        """
        self.p = p
        self.value = value
        self.element = element

    def wellformed(self, astc):
        return self.value.wellformed(astc);

    def gencode(self, icc):

        base = icc.pop_var()     # destination base addr
        elem = icc.pop_var()     # array element number

        val = icc.new_var()
        icc.add_instruction(ICBoundCheck(base, elem))

        icc.add_instruction(ICLoadWord(val, base, Integer(0), elem))

        val.is_pointer = True;
        val._elem = elem;
        val._base = base; 
        icc.push_var(val);

    def to_stack(self):
        return [self] + self.value.to_stack() + self.element.to_stack()

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s[%s]" % (counter, self.value, self.element)
        graph.add_node(name, fillcolor=ASTVariable.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'ARRAY: %s[%s]' % (self.value, self.element)



class ASTPrint(ASTNode):
    COLOR = NODE_COLORS['ASTPrint']

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


class ASTStatement(ASTNode):
    COLOR = NODE_COLORS['ASTStatement']

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


class ASTUnaryOp(ASTNode):
    COLOR = NODE_COLORS['ASTUnaryOp']
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


class ASTVariable(ASTNode):
    COLOR = NODE_COLORS['ASTVariable']

    def __init__(self, p, value, dimensions=0):
        """AST variable

        Arguments:
        p - pyl parser object
        value - name of variable

        """
        self.p = p
        self.value = value
        self.dimensions = dimensions

    def wellformed(self, astc):
        if self.value in astc.rename:
            self.value = astc.rename[self.value]
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
        return [self] + ( self.value.to_stack() if isinstance(self.value, ASTArray) else [] )

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, self.value)
        graph.add_node(name, fillcolor=ASTVariable.COLOR)
        graph.add_edge(parent, name)
        return counter

    def __str__(self):
        return 'ID: %s' % self.value



class ASTWhileDo(ASTNode):
    COLOR = NODE_COLORS['ASTWhileDo']

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
        astc.counter = stmt_astc.counter
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
        icc.add_instruction(ICWhileDo(while_var, while_part_block,
                            end_if_block, next_block), while_part_block)

    def to_stack(self):
        # Self will handle other statements
        return [self]

    def add_edges_to_graph(self, graph, parent, counter):
        name = "%s\n%s" % (counter, 'while...do')
        graph.add_node(name, fillcolor=ASTWhileDo.COLOR)
        graph.add_edge(parent, name)
        counter = self.while_part.add_edges_to_graph(graph, name, counter + 1)
        counter = self.do_part.add_edges_to_graph(graph, name, counter + 1)
        return counter

    def __str__(self):
        return 'WHILE: [%s] DO [%s]' % (self.while_part, self.do_part)
