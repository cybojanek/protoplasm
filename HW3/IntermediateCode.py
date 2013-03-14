from ASMCode import *
from Graph import UndirectedGraph
from ASMCode import AsmInstruction


class Variable(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Integer(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)


class Label(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "%s:"


class IC(object):
    def __init__(self):
        """Intermediate Code object

        """
        self.liveliness = {'in': set(), 'out': set(), 'used': set(),
                           'defined': set()}
        self.register_map = {}
        self.context = None

    def set_context(self, context, block):
        self.context = context
        self.block = block

    def add_used(self, variable):
        """Add a variable that is used. Automatically filters out Integers

        Arguments:
        variable - Variable object, others passed up on

        """
        if isinstance(variable, Variable):
            self.liveliness['used'].add(variable)

    def remove_used(self, variable):
        """Remove a variable from the set of used variables
        Checks for inclusion, so won't generate any excpetions on removal

        Arguments:
        variable - Variable object to be remove

        """
        if variable in self.liveliness['used']:
            self.liveliness['used'].remove(variable)

    def add_defined(self, dest):
        """Add a variable that is defined. Automatically filters out Integers

        Arguments:
        variable - Variable object, others passed up on

        """
        if isinstance(dest, Variable):
            self.liveliness['defined'].add(dest)

    def remove_defined(self, dest):
        """Remove a variable from the set of defined variables
        Checks for inclusion, so won't generate any excpetions on removal

        Arguments:
        variable - Variable object to be remove

        """
        if dest in self.liveliness['defined']:
            self.liveliness['defined'].remove(dest)

    def update_variable_sets(self, next_ic=None):
        """Update in and out sets.

        Keyword Arguments:
        next_ic - the intermediate code after this one (used to update out set)
            if None given, then Out not updated (good for last statement)

        Return:
        boolean of whether something was changed or not

        """
        changed = False
        if next_ic:
            # Out(n) = U In(n + 1)
            old_out = self.liveliness['out']
            self.liveliness['out'] = self.liveliness['out'].union(next_ic.liveliness['in'])
            changed = changed or not(old_out == self.liveliness['out'])
        # In(n) = Used(n) U (Out(n) - Defined(n))
        new_in = self.liveliness['used'].union(
            self.liveliness['out'].difference(self.liveliness['defined']))
        changed, self.liveliness['in'] = (
            (changed or not(self.liveliness['in'] == new_in)), new_in)
        return changed

    def set_register_map(self, reg_map):
        self.register_map = reg_map

    def get_register_or_value(self, variable):
        """Get the register or Integer value of a variable

        Arguments:
        variable - Integer/Variable object

        Return:
        Integer.value or register string name from register_map

        """
        if isinstance(variable, Integer):
            return variable.value
        else:
            return self.register_map[variable]

    def first_pass(self):
        pass

    def generate_assembly(self):
        raise NotImplemented()

    def rename_used(self, old, new):
        raise NotImplemented()

    def rename_defined(self, old, new):
        raise NotImplemented()


class ICAssign(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, dest, arg1):
        super(ICAssign, self).__init__()
        if not(isinstance(dest, Variable)and (isinstance(arg1, Variable) or
               isinstance(arg1, Integer))):
            raise ValueError("Unsupported Assignment")
        self.dest = dest
        self.arg1 = arg1
        self.add_defined(dest)
        self.add_used(arg1)

    def rename_used(self, old, new):
        if self.arg1 == old:
            self.remove_used(self.arg1)
            self.arg1 = new
            self.add_used(self.arg1)

    def rename_defined(self, old, new):
        if self.dest == old:
            self.remove_defined(self.dest)
            self.dest = new
            self.add_defined(self.dest)

    def generate_assembly(self):
        dest = self.get_register_or_value(self.dest)
        arg1 = self.get_register_or_value(self.arg1)
        if isinstance(self.arg1, Integer):
            # li Rd, Imm    Rd = Imm
            return [AsmInstruction('li', dest, arg1, comment=str(self))]
        else:
            # move Rd, Rs   Rs = Rs
            return [AsmInstruction('move', dest, arg1, comment=str(self))]

    def __str__(self):
        return "%s = %s" % (self.dest, self.arg1)


class ICBinaryOp(IC):
    """Do a binary operation
    """
    ASM_OPS = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'rem',
               '&&': None, '||': None, '==': 'seq', '!=': 'sne', '<': 'slt',
               '<=': 'sle', '>': 'sgt', '>=': 'sge'}

    def __init__(self, dest, arg1, arg2, op):
        super(ICBinaryOp, self).__init__()
        if not(isinstance(dest, Variable)
           and (isinstance(arg1, Variable) or isinstance(arg1, Integer))
           and (isinstance(arg2, Variable) or isinstance(arg2, Integer))
           and (op in ICBinaryOp.ASM_OPS)):
            raise ValueError("Unsupported binary operation")
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op
        self.add_defined(dest)
        self.add_used(arg1)
        self.add_used(arg2)

    def rename_used(self, old, new):
        if self.arg1 == old:
            self.remove_used(self.arg1)
            self.arg1 = new
            self.add_used(self.arg1)
        if self.arg2 == old:
            self.remove_used(self.arg2)
            self.arg2 = new
            self.add_used(self.arg2)

    def rename_defined(self, old, new):
        if self.dest == old:
            self.remove_defined(self.dest)
            self.dest = new
            self.add_defined(self.dest)

    def generate_assembly(self):
        if isinstance(self.arg1, Integer) or isinstance(self.arg2, Integer):
            raise ValueError("Cannot do binary operation on Integers!")
        op = ICBinaryOp.ASM_OPS[self.op]
        dest = self.get_register_or_value(self.dest)
        arg1 = self.get_register_or_value(self.arg1)
        arg2 = self.get_register_or_value(self.arg2)
        # Short circuit logic for &&
        if self.op == '&&':
            label_set_0 = self.context.new_label(suffix='set_0')
            label_done = self.context.new_label(suffix='done')
            return [AsmInstruction('beqz', arg1, label_set_0, comment=str(self)),
                    AsmInstruction('move', dest, arg2),
                    AsmInstruction('b', label_done),
                    AsmInstruction('%s:' % label_set_0),
                    AsmInstruction('li', dest, 0),
                    AsmInstruction('%s:' % label_done)]
        # Short circuit logic for ||
        elif self.op == '||':
            label_use_arg1 = self.context.new_label(suffix='use_arg1')
            label_done = self.context.new_label(suffix='done')
            return [AsmInstruction('bnez', arg1, label_use_arg1, comment=str(self)),
                    AsmInstruction('move', dest, arg2),
                    AsmInstruction('b', label_done),
                    AsmInstruction('%s:' % label_use_arg1),
                    AsmInstruction('move', dest, arg1),
                    AsmInstruction('%s:' % label_done)]
        # op Rd, Rs, Rt    Rd = Rs op Rt
        return [AsmInstruction(op, dest, arg1, arg2, comment=str(self))]

    def __str__(self):
        return "%s = %s %s %s" % (self.dest, self.arg1, self.op, self.arg2)


class ICUnaryOp(IC):
    """Do a unary operation
    """
    ASM_OPS = {'-': 'neg', '!': None}

    def __init__(self, dest, arg1, op):
        super(ICUnaryOp, self).__init__()
        if not(isinstance(dest, Variable)
           and (isinstance(arg1, Variable) or isinstance(arg1, Integer))
           and (op in ICUnaryOp.ASM_OPS)):
            raise ValueError("Unsupported unary operation")
        self.dest = dest
        self.arg1 = arg1
        self.op = op
        self.add_defined(dest)
        self.add_used(arg1)

    def rename_used(self, old, new):
        if self.arg1 == old:
            self.remove_used(self.arg1)
            self.arg1 = new
            self.add_used(self.arg1)

    def rename_defined(self, old, new):
        if self.dest == old:
            self.remove_defined(self.dest)
            self.dest = new
            self.add_defined(self.dest)

    def generate_assembly(self):
        dest = self.get_register_or_value(self.dest)
        arg1 = self.get_register_or_value(self.arg1)
        # Negation is a bit more complicated
        if self.op == '!':
            if isinstance(self.arg1, Integer):
                return [AsmInstruction('li', dest, arg1, comment=str(self)),
                        AsmInstruction('seq', dest, dest, 0)]
            else:
                return [AsmInstruction('seq', dest, arg1, 0, comment=str(self))]
        # Otherwise
        op = ICUnaryOp.ASM_OPS[self.op]
        # op Rd, Rs    Rd = op Rs
        if isinstance(self.arg1, Integer):
            return [AsmInstruction('li', dest, arg1, comment=str(self)),
                    AsmInstruction(op, dest, dest)]
        else:
            return [AsmInstruction(op, dest, arg1, comment=str(self))]

    def __str__(self):
        return "%s = %s %s" % (self.dest, self.op, self.arg1)


class ICPrint(IC):
    """Do a print statement for an integer
    """

    def __init__(self, arg1):
        super(ICPrint, self).__init__()
        if not(isinstance(arg1, Variable) or isinstance(arg1, Integer)):
            raise ValueError("Unsupported print operation")
        self.arg1 = arg1
        self.add_used(arg1)

    def rename_used(self, old, new):
        if self.arg1 == old:
            self.remove_used(self.arg1)
            self.arg1 = new
            self.add_used(self.arg1)

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        arg1 = self.get_register_or_value(self.arg1)
        asm = []
        if isinstance(self.arg1, Integer):
            # li Rd, Imm    Rd = Imm
            asm.append(AsmInstruction('li', '$a0', arg1, comment=str(self)))
        else:
            # move Rd, Rs   Rd = Rs
            asm.append(AsmInstruction('move', '$a0', arg1, comment=str(self)))
        # li Rd, Imm    Rd = Imm
        # syscall
        asm.append(AsmInstruction('li', '$v0', 1))
        asm.append(AsmInstruction('syscall'))
        # Add a newline
        asm.append(AsmInstruction('li', '$a0', ord('\n'), comment='newline'))
        asm.append(AsmInstruction('li', '$v0', 11))
        asm.append(AsmInstruction('syscall'))
        return asm

    def __str__(self):
        return "print(%s)" % (self.arg1)


class ICInput(IC):
    """Do an input statement for an integer
    """

    def __init__(self, dest):
        super(ICInput, self).__init__()
        if not(isinstance(dest, Variable)):
            raise ValueError("Unsupported input operation")
        self.dest = dest

    def rename_used(self, old, new):
        pass

    def rename_defined(self, old, new):
        if self.dest == old:
            self.remove_defined(self.dest)
            self.dest = new
            self.add_defined(self.dest)

    def generate_assembly(self):
        dest = self.get_register_or_value(self.dest)
        asm = []
        asm.append(AsmInstruction('li', '$a0', ord('>'), comment='prompt'))
        asm.append(AsmInstruction('li', '$v0', 11))
        asm.append(AsmInstruction('syscall'))
        # li Rd, Imm    Rd = Imm
        # syscall
        # move Rd, Rs   Rd = Rs
        asm.append(AsmInstruction('li', '$v0', 5, comment=str(self)))
        asm.append(AsmInstruction('syscall'))
        asm.append(AsmInstruction('move', dest, '$v0'))
        return asm

    def __str__(self):
        return "%s = input()" % (self.dest)


class ICIf(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, if_part, then_block, else_block, end_if_block):
        super(ICIf, self).__init__()
        if not(isinstance(if_part, Variable) or isinstance(if_part, Integer)):
            raise ValueError("Unsupported if statement")
        self.if_part = if_part
        self.add_used(if_part)
        self.then_block = then_block
        self.else_block = else_block
        self.end_if_block = end_if_block

    def rename_used(self, old, new):
        if self.if_part == old:
            self.remove_used(self.if_part)
            self.if_part = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        # Get the condition register
        arg1 = self.get_register_or_value(self.if_part)
        # Make a label for the end block
        end_if_label = self.context.new_label(suffix='end_if')
        # Add the label to the start of that block
        self.end_if_block.add_start_label(end_if_label)
        if self.else_block is None:
            # If false, then branch to next end if block
            return [AsmInstruction('beqz', arg1, end_if_label, comment=str(self))]
        # Make a label for the else block
        else_label = self.context.new_label(suffix='else')
        # Add the else label to the else block
        self.else_block.add_start_label(else_label)
        # Tell the then_block to branch to end_if_block (to skip else block)
        self.then_block.add_end_branch(end_if_label)
        # If false, then branch to the else_block
        return [AsmInstruction('beqz', arg1, else_label, comment=str(self))]

    def __str__(self):
        # return "if %s then... [%s]" % (self.if_part, self.then_part.statements.value.statements[0])
        return "if %s then...%s" % (self.if_part, '' if self.else_block is None else 'else...')


class ICWhile(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, if_part, condition_block, stmt_block, next_block):
        super(ICWhile, self).__init__()
        if not(isinstance(if_part, Variable) or isinstance(if_part, Integer)):
            raise ValueError("Unsupported if statement")
        self.if_part = if_part
        self.add_used(if_part)
        self.condition_block = condition_block
        self.stmt_block = stmt_block
        self.next_block = next_block

    def rename_used(self, old, new):
        if self.if_part == old:
            self.remove_used(self.if_part)
            self.if_part = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def first_pass(self):
        # Make a label for the condition block
        self.condition_label = self.context.new_label(suffix='while')
        self.condition_block.add_start_label(self.condition_label)

    def generate_assembly(self):
        # Get the condition register
        arg1 = self.get_register_or_value(self.if_part)

        # At end of statements, jump back to condition checking
        self.stmt_block.add_end_branch(self.condition_label)

        # Make a label for the end block
        end_while_label = self.context.new_label(suffix='end_while')
        self.next_block.add_start_label(end_while_label)

        return [AsmInstruction('beqz', arg1, end_while_label, comment=str(self))]

    def __str__(self):
        # return "if %s then... [%s]" % (self.if_part, self.then_part.statements.value.statements[0])
        return "while %s do..." % (self.if_part)


class ICContextBasicBlock(object):

    def __init__(self):
        """Collection of instructions in a basic block

        """
        self.start_label = None
        self.branch_label = None
        self.instructions = []
        self.follow = []

    def add_follow(self, block):
        self.follow.append(block)

    def add_start_label(self, name):
        self.start_label = name

    def add_end_branch(self, name):
        self.branch_label = name

    def generate_start_assembly(self):
        if self.start_label is not None:
            return [AsmInstruction('%s:' % self.start_label)]
        return []

    def generate_end_assembly(self):
        if self.branch_label is not None:
            return [AsmInstruction('b', self.branch_label)]
        return []

    def update_liveliness(self):
        if len(self.instructions) == 0:
            return
        # Keep looping while one of the sets has changed
        block_changed = False
        changed = True
        while changed:
            changed = False
            # The last one might not have a next so we have to do this first
            changed = changed or self.instructions[-1].update_variable_sets()
            # Then loop through its follows
            for follow in self.follow:
                if len(follow.instructions) >= 1:
                    changed = changed or self.instructions[-1].update_variable_sets(follow.instructions[0])
            # Bottom up, update in's and out's, using next statement
            for i in xrange(len(self.instructions) - 2, -1, -1):
                changed = changed or self.instructions[i].update_variable_sets(
                    next_ic=self.instructions[i + 1])
            block_changed = block_changed or changed
        return block_changed

    def __str__(self):
        s = ''
        for x in self.instructions:
            line = '%s' % x
            line = '%s%s' % (line, ' ' * (15 - len(line)))
            line = '%sOut: %s  In: %s\n' % (line, [str(y) for y in x.liveliness['out']], [str(y) for y in x.liveliness['in']])
            s += line
            #s += '%s\t%s\n' % (x, x.liveliness['out'])
        return s

class ICContext(object):
    TEMP_REGS = {
        '$t0': '#FF7400',
        '$t1': '#009999',
        '$t2': '#FF7373',
        '$t3': '#BF7130',
        '$t4': '#A60000',
        '$t5': '#008500',
        '$t6': '#00CC00',
        '$t7': '#D2006B',
        '$t8': '#574DD8',
        '$t9': '#B7F200'
    }
    ALL_TEMP_REGS = set(TEMP_REGS.keys())

    def __init__(self):
        """Keeps track of the ASTNode to address context translation

        """
        self.blocks = [ICContextBasicBlock()]
        self.variables = []
        self.counter = 0
        self.liveliness_graph = UndirectedGraph()
        self.variable_usage = {}

    def new_block(self, auto_follow=True):
        """Create a new instruction block
        Instructions pushed after this will be pushed onto this list

        Return:
        new ICContextBasicBlock object
        """
        # Make new block
        a = ICContextBasicBlock()
        # Add it as a follow of previous
        if auto_follow:
            self.blocks[-1].add_follow(a)
        # Add it as the current block
        self.blocks.append(a)
        return a

    def get_current_block(self):
        """Return the current block to which instructions are appended to

        Return:
        ICContextBasicBlock object
        """
        return self.blocks[-1]

    def add_instruction(self, ins, block=None):
        """Add a IC to the instruction list

        Arguments:
        ins - IC

        """
        if block is None:
            self.blocks[-1].instructions.append(ins)
            ins.set_context(self, self.blocks[-1])
        else:
            block.instructions.append(ins)
            ins.set_context(self, block)

    def new_var(self):
        """Create a new temporary variable.
        Autoincremented.

        """
        name = '@%s' % self.counter
        self.counter += 1
        return Variable(name)

    def new_label(self, suffix=''):
        """Create a new label name
        Autoincremented.

        """
        name = 'l_%s_%s' % (self.counter, suffix)
        self.counter += 1
        return name

    def push_var(self, var):
        """Add a variable to the stack

        Arguments:
        var - variable

        """
        self.variables.append(var)

    def pop_var(self):
        """Remove a variable from the stack

        Return:
        top variable form stack

        """
        return self.variables.pop()

    def gencode(self):
        """Converts the list of IC objects to ASMInstruction Objects,
           Returns AsmInstructionContext
        """
        for block in self.blocks:
            for ins in block.instructions:
                ins.first_pass()
        asm = []
        for block in self.blocks:
            asm = asm + block.generate_start_assembly()
            for ins in block.instructions:
                asm = asm + ins.generate_assembly()
            asm = asm + block.generate_end_assembly()
        return asm

    def registerize(self, ssa=False):
        """Perform optimization procedures and translate variables
        to use registers.

        Keyword Arguments:
        flatten_temp - look @ICContext.flatten_temporary_assignments
        ssa - look @ICContext.update_ssa

        """
        if ssa:
            self.update_ssa()
        self.mipsify()
        self.update_liveliness()
        # Keep looping until we allocated
        # will loop multiple times if not enough registers and we spill
        allocated = False
        while not allocated:
            self.update_liveliness()
            allocated = self.allocate_registers()

    def update_ssa(self):
        """Translate intermediate code to use Static Single Assignment
        variables.

        """
        return
        vc = {}
        for block in self.blocks:
            for i in block.instructions: 
                for x in i.liveliness['used']:
                    if isinstance(x, Variable) and x in vc and vc[x] != 0:
                        i.rename_used(x, Variable('%s%s' % (x, vc[x])))
                for x in i.liveliness['defined']:
                    if x in vc:
                        vc[x] += 1
                        i.rename_defined(x, Variable('%s%s' % (x, vc[x])))
                    else:
                        vc[x] = 0

    def mipsify(self):
        """Convert from generic intermediate code to mips three address compatible
        Some operations only accept registers: such as =*/%, while others,
        like +, cannot add two numbers > 16 bits each. This function splits up
        such instructions into multiple register assignments and adidtion.
        For all binary ops, put Integers into registers
        For if statements, make sure condition is in a variable

        """
        for block in self.blocks:
            i = 0
            while i < len(block.instructions):
                ins = block.instructions[i]
                if isinstance(ins, ICBinaryOp):
                    if isinstance(ins.arg1, Integer):
                        a = self.new_var()
                        block.instructions.insert(i, ICAssign(a, ins.arg1))
                        ins.arg1 = a
                        ins.add_used(a)
                        i += 1
                    if isinstance(ins.arg2, Integer):
                        a =self.new_var()
                        block.instructions.insert(i, ICAssign(a, ins.arg2))
                        ins.arg2 = a
                        ins.add_used(a)
                        i += 1
                if isinstance(ins, ICIf) and isinstance(ins.if_part, Integer):
                    a = self.new_var()
                    block.instructions.insert(i, ICAssign(a, ins.if_part))
                    ins.if_part = a
                    ins.add_used(a)
                    i += 1
                if isinstance(ins, ICWhile) and isinstance(ins.if_part, Integer):
                    a = self.new_var()
                    block.instructions.insert(i, ICAssign(a, ins.if_part))
                    ins.if_part = a
                    ins.add_used(a)
                    i += 1
                i += 1

    def update_liveliness(self):
        """Loop through all instructions and update their in and out sets.
        Calculate how many times a variable is used.

        """
        for block in self.blocks:
            for ins in block.instructions:
                # Clear up outs and ins
                ins.liveliness['out'] = set()
                ins.liveliness['int'] = set()
        # Update block liveliness
        # Last statement of each block sets its out to union of all follows
        changed = True
        while changed:
            changed = False
            for i in xrange(len(self.blocks) - 1, -1, -1):
                changed = changed or self.blocks[i].update_liveliness()
        # Now build up a graph of which variables need to be alive at the
        # same time
        self.liveliness_graph = UndirectedGraph()
        for block in self.blocks:
            for ins in block.instructions:
                # Add defined variables - will be single nodes if not conflicting
                for i in ins.liveliness['defined']:
                    self.liveliness_graph.add_node(i)
                # All the in variables that conflict with each other
                for i in ins.liveliness['in']:
                    self.liveliness_graph.add_node(i)
                    for j in ins.liveliness['in']:
                        if i != j:
                            self.liveliness_graph.add_edge(i, j)
        # Calculate how many times each variable is used
        # doesn't take any consideration of ifs nor whiles
        self.variable_usage = {}
        for block in self.blocks:
            for ins in block.instructions:
                for v in ins.liveliness['used']:
                    if v not in self.variable_usage:
                        self.variable_usage[v] = 1
                    else:
                        self.variable_usage[v] += 1

    def allocate_registers(self):
        """Allocate registers by coloring in a graph of liveliness

        """
        var_map = {}
        stack = []
        # Build up graph
        graph = self.liveliness_graph
        # Loop through all nodes
        while len(graph.nodes()) > 0:
            # Get the smallest degree node
            node = graph.smallest_degree_node()
            # If its less than amount of registers: we're okay
            if graph.degree(node) < len(ICContext.TEMP_REGS):
                # node, set of edges
                stack.append((node, graph.remove_node(node)))
            # Else we need to look through and find a good candidate
            else:
                # Find the node which has the
                # highest degree - amount of times used
                node = max(graph.nodes(),
                    key=lambda x: graph.degree(x) - self.variable_usage[x])
                stack.append((node, graph.remove_node(node)))
        # Now add back the nodes
        while len(stack) != 0:
            # Remove a node, edges from stack
            node, edges = stack.pop()
            graph.add_edges(node, edges)
            # Get all neighbhor colors
            neighbor_regs = set([graph.color(n) for n in edges])
            # Calculate all possible colors
            possible_regs = ICContext.ALL_TEMP_REGS.difference(
                neighbor_regs)
            # If we don't have something to color with, then spill
            # return false, and wait to be called again
            if len(possible_regs) == 0:
                raise ValueError("NOT ENOUGH REGISTERS")
                self.spill_variable(node)
                return False
            # Get one
            reg = possible_regs.pop()
            # Set the color
            graph.colorize(node, reg)
        # Now replace with graph colors with actual colors
        # and store variable to register mapping
        for node in graph.nodes():
            var_map[node] = graph.color(node)
            graph.colorize(node,
                ICContext.TEMP_REGS[graph.color(node)])
        # Rename all variables
        for block in self.blocks:
            for ic in block.instructions:
                ic.set_register_map(var_map)
        return True

    def spill_variable(self, var):
        """Spill a variable, and store it to a memory location

        Arguments:
        var - variable to be spilled

        """
        i = 0
        first_assign = True
        new_var = var
        label = self.new_label()
        while i < len(self.instructions):
            ins = self.instructions[i]
            if ins.dest == var and first_assign:
                self.instructions.insert(i + 1, ThreeAddress(
                    dest=label, arg1=new_var, op='store'))
                first_assign = False
                i += 2
                continue
            # If we're writing to the variable
            if ins.is_assignment() and ins.dest == var:
                new_var = self.new_var()
                ins.rename_dest(new_var)
                if ins.arg1 == var:
                    ins.rename_arg1(new_var)
                # Insert a store after this statement
                self.instructions.insert(i + 1, ThreeAddress(
                    dest=label, arg1=new_var, op='store'))
                i += 2
                continue
            # If the spill variable is used, restore before, rename
            # and store afterwards
            if var in ins.variables['used']:
                new_var = self.new_var()
                self.instructions.insert(i, ThreeAddress(
                    dest=new_var, arg1=label, op='load'))
                if ins.arg1 == var:
                    ins.rename_arg1(new_var)
                if ins.arg2 == var:
                    ins.rename_arg2(new_var)
                if ins.dest == var:
                    ins.rename_dest(new_var)
                    self.instructions.insert(i + 2, ThreeAddress(
                        dest=label, arg1=new_var, op='store'))
                    i += 1
                i += 2
                continue
            i += 1
        # print "#" * 80
        # print 'spill: %s' % var
        # for x in self.instructions:
        #     print x, x.variables['out']
        # print "#" * 80
        # self.update_liveliness()
        # print "#" * 80
        # print 'spill: %s' % var
        # for x in self.instructions:
        #     print x, x.variables['out']
        # print "#" * 80
        # sys.exit(1)

    def __str__(self):
        s = ''
        for x in self.blocks:
            s += '---------------------\n'
            s += str(x)
        return s
