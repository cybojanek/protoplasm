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
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class IC(object):
    # Constant registers
    REGISTER_CONSTANTS = {Variable('@stack'): '$sp'}

    def __init__(self):
        """Intermediate Code object

        """
        self.liveliness = {'in': set(), 'out': set(), 'used': set(),
                           'defined': set()}
        self.register_map = {}
        self.context = None

    def set_context(self, context, block):
        """Set the context and block of this instruction

        Arguments:
        context - ICContext
        block - ICContextBasicBlock

        """
        self.context = context
        self.block = block

    def set_register_map(self, reg_map):
        """Set the register mapping

        Arguments:
        reg_map - dictionary of Variable -> register string

        """
        self.register_map = reg_map

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

    def get_register_or_value(self, variable):
        """Get the register or Integer value of a variable

        Arguments:
        variable - Integer/Variable object

        Return:
        Integer.value or register string name from register_map

        """
        if isinstance(variable, Integer):
            return variable.value
        elif variable in IC.REGISTER_CONSTANTS:
            return IC.REGISTER_CONSTANTS[variable]
        else:
            return self.register_map[variable]

    def add_used(self, variable):
        """Add a variable that is used. Automatically filters out Integers
        and compiler constants defined in REGISTER_CONSTANTS

        Arguments:
        variable - Variable object, others passed up on

        """
        if isinstance(variable, Variable) and variable not in IC.REGISTER_CONSTANTS:
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

    def rename_used(self, old, new):
        """Rename a used variable. Should check for existance,
        and update used liveliness set
        """
        raise NotImplemented()

    def rename_defined(self, old, new):
        """Rename a defined variable. Should check for existance,
        and update defined liveliness set
        """
        raise NotImplemented()

    def first_pass(self):
        """First compiler pass. Good for setting some labels
        """
        pass

    def generate_assembly(self):
        """Return a list of AsmInstruction
        """
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
    """Binary operations
    """
    ASM_OPS = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'rem',
               '&&': None, '||': None, '==': 'seq', '!=': 'sne', '<': 'slt',
               '<=': 'sle', '>': 'sgt', '>=': 'sge'}

    def __init__(self, dest, arg1, arg2, op):
        super(ICBinaryOp, self).__init__()
        # Check that both arg1 and arg2 are variables or integers
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
        # We can accept Integer to arg1/arg2 but by here they should be moved
        # out and only registers accepted
        if isinstance(self.arg1, Integer) or isinstance(self.arg2, Integer):
            raise ValueError("Cannot do binary operation on Integers!")
        # Get instruction from op map
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
    """Unary operations
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
    def __init__(self, if_var, then_block, else_block, end_if_block):
        super(ICIf, self).__init__()
        if not(isinstance(if_var, Variable) or isinstance(if_var, Integer)):
            raise ValueError("Unsupported if statement")
        self.if_var = if_var
        self.add_used(if_var)
        self.then_block = then_block
        self.else_block = else_block
        self.end_if_block = end_if_block

    def rename_used(self, old, new):
        if self.if_var == old:
            self.remove_used(self.if_var)
            self.if_var = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        # Get the condition register
        arg1 = self.get_register_or_value(self.if_var)
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
        # return "if %s then... [%s]" % (self.if_var, self.then_part.statements.value.statements[0])
        return "if %s then...%s" % (self.if_var, '' if self.else_block is None else 'else...')


class ICWhileDo(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, while_var, while_part_block, end_if_block, next_block):
        super(ICWhileDo, self).__init__()
        if not(isinstance(while_var, Variable) or isinstance(while_var, Integer)):
            raise ValueError("Unsupported if statement")
        self.while_var = while_var
        self.add_used(while_var)
        self.while_part_block = while_part_block
        self.end_if_block = end_if_block
        self.next_block = next_block

    def rename_used(self, old, new):
        if self.while_var == old:
            self.remove_used(self.while_var)
            self.while_var = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def first_pass(self):
        # Make a label for the condition block
        self.condition_label = self.context.new_label(suffix='while')
        self.while_part_block.add_start_label(self.condition_label)

    def generate_assembly(self):
        # Get the condition register
        arg1 = self.get_register_or_value(self.while_var)

        # At end of statements, jump back to condition checking
        self.end_if_block.add_end_branch(self.condition_label)

        # Make a label for the end block
        end_while_label = self.context.new_label(suffix='end_while')
        self.next_block.add_start_label(end_while_label)

        return [AsmInstruction('beqz', arg1, end_while_label, comment=str(self))]

    def __str__(self):
        return "while %s do..." % (self.while_var)


class ICDoWhile(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, do_part_block, while_var, while_part_block, next_block):
        super(ICDoWhile, self).__init__()
        if not(isinstance(while_var, Variable) or isinstance(while_var, Integer)):
            raise ValueError("Unsupported if statement")
        self.do_part_block = do_part_block
        self.while_var = while_var
        self.add_used(while_var)
        self.while_part_block = while_part_block
        self.next_block = next_block

    def rename_used(self, old, new):
        if self.while_var == old:
            self.remove_used(self.while_var)
            self.while_var = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def first_pass(self):
        # Make a label for the do block
        self.do_label = self.context.new_label(suffix='do')
        self.do_part_block.add_start_label(self.do_label)

    def generate_assembly(self):
        # Get the condition register
        arg1 = self.get_register_or_value(self.while_var)

        # At end of statements, jump back to condition checking
        #self.end_if_block.add_end_branch(self.condition_label)

        # Make a label for the end block
        next_block_label = self.context.new_label(suffix='end_while')
        self.next_block.add_start_label(next_block_label)

        return [AsmInstruction('beqz', arg1, next_block_label, comment=str(self)),
                AsmInstruction('b', self.do_label, comment='do again')]

    def __str__(self):
        return "do...while %s" % (self.while_var)


class ICStoreWord(IC):
    """Store a word
    """
    def __init__(self, src, base=None, offset=None):
        """
        Arguments:
        src - variable name (register)
        dest - variable name (register)

        Keyword Arguments:
        base - label or variable
        offset - variable or integer

        Allowable combinations:
        label/var, var/int, label/None, None/var

        """
        super(ICStoreWord, self).__init__()
        if not(isinstance(src, Variable)):
            raise ValueError("Unsupported storage")
        # Check base

        if isinstance(base, Label) and isinstance(offset, Variable):
            # base is label and offset is register
            self.add_used(Variable)
        elif isinstance(base, Variable) and isinstance(offset, Integer):
            # base is register and offset is integer
            self.add_used(base)
        elif isinstance(base, Label):
            # base is label
            pass
        elif isinstance(offset, Variable):
            # offset is register
            self.add_used(offset)
        else:
            raise ValueError("Unsupported storage base/offset: %s, %s" % (base, offset))
        self.src = src
        self.base = base
        self.offset = offset
        self.add_used(src)

    def rename_used(self, old, new):
        if self.src == old:
            self.remove_used(self.src)
            self.src = new
            self.add_used(new)
        if self.base == old:
            self.remove_used(self.base)
            self.base = new
            self.add_used(new)
        if self.offset == old:
            self.remove_used(self.offset)
            self.offset = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        arg1 = self.get_register_or_value(self.src)
        arg2 = ''
        if isinstance(self.base, Label) and isinstance(self.offset, Variable):
            # base is label and offset is register
            arg2 = '%s(%s)' % (self.base, self.get_register_or_value(self.offset))
        elif isinstance(self.base, Variable) and isinstance(self.offset, Integer):
            # base is register and offset is integer
            arg2 = '%s(%s)' % (self.offset, self.get_register_or_value(self.base))
        elif isinstance(self.base, Label):
            # base is label
            arg2 = '%s'
        elif isinstance(self.offset, Variable):
            # offset is register
            arg2 = '(%s)' % (self.get_register_or_value(self.offset))
        return [AsmInstruction('sw', arg1, arg2, comment=str(self))]

    def __str__(self):
        return "%s[%s] = %s" % (self.base, self.offset, self.src)


class ICLoadWord(IC):
    """Load a word
    """
    def __init__(self, dest, base=None, offset=None):
        """
        Arguments:
        dest - variable name (register)

        Keyword Arguments:
        base - label or variable
        offset - variable or integer

        Allowable combinations:
        label/var, var/int, label/None, None/var

        """
        super(ICLoadWord, self).__init__()
        if not(isinstance(dest, Variable)):
            raise ValueError("Unsupported load")
        # Check base

        if isinstance(base, Label) and isinstance(offset, Variable):
            # base is label and offset is register
            self.add_used(Variable)
        elif isinstance(base, Variable) and isinstance(offset, Integer):
            # base is register and offset is integer
            self.add_used(base)
        elif isinstance(base, Label):
            # base is label
            pass
        elif isinstance(offset, Variable):
            # offset is register
            self.add_used(offset)
        else:
            raise ValueError("Unsupported load base/offset: %s, %s" % (base, offset))
        self.dest = dest
        self.base = base
        self.offset = offset
        self.add_defined(dest)

    def rename_used(self, old, new):
        if self.base == old:
            self.remove_used(self.base)
            self.base = new
            self.add_used(new)
        if self.offset == old:
            self.remove_used(self.offset)
            self.offset = new
            self.add_used(new)

    def rename_defined(self, old, new):
        if self.dest == old:
            self.remove_defined(self.dest)
            self.dest = new
            self.add_defined(new)

    def generate_assembly(self):
        arg1 = self.get_register_or_value(self.dest)
        arg2 = ''
        if isinstance(self.base, Label) and isinstance(self.offset, Variable):
            # base is label and offset is register
            arg2 = '%s(%s)' % (self.base, self.get_register_or_value(self.offset))
        elif isinstance(self.base, Variable) and isinstance(self.offset, Integer):
            # base is register and offset is integer
            arg2 = '%s(%s)' % (self.offset, self.get_register_or_value(self.base))
        elif isinstance(self.base, Label):
            # base is label
            arg2 = '%s'
        elif isinstance(self.offset, Variable):
            # offset is register
            arg2 = '(%s)' % (self.get_register_or_value(self.offset))
        return [AsmInstruction('lw', arg1, arg2, comment=str(self))]

    def __str__(self):
        return "%s = %s[%s]" % (self.dest, self.base, self.offset)


class ICContextBasicBlock(object):

    def __init__(self):
        """Collection of instructions in a basic block

        """
        self.start_label = None
        self.branch_label = None
        self.instructions = []
        self.follow = []
        self.liveliness = {'in': set(), 'out': set()}

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

            # Get all followers and loop through empty's
            # Should not loop indefinitely...in case of two emptys in a loop
            follower_blocks = []
            candidates = [x for x in self.follow]
            visited = set()
            while len(candidates) != 0:
                c = candidates.pop()
                if c not in visited:
                    visited.add(c)
                else:
                    continue
                if len(c.instructions) < 1:
                    for x in c.follow:
                        if x not in visited:
                            candidates.append(c)
                else:
                    follower_blocks.append(c)

            # Then loop through its follows
            for follow in follower_blocks:
                if len(follow.instructions) >= 1:
                    changed = changed or self.instructions[-1].update_variable_sets(next_ic=follow.instructions[0])
                    # old = self.livelines['out']
                    # self.livelines['out'] = self.livelines['out'].union(follow.livelines['in'])
                    # changed = changed or old == self.livelines['out']
            # Bottom up, update in's and out's, using next statement
            for i in xrange(len(self.instructions) - 2, -1, -1):
                changed = changed or self.instructions[i].update_variable_sets(
                    next_ic=self.instructions[i + 1])
            # old = self.livelines['in']
            # self.livelines['in'] = self.livelines['in'].union()
            block_changed = block_changed or changed
        return block_changed

    def graph_label(self):
        s = ''
        for x in self.instructions:
            line = '%s' % x
            line = '%s%s\l' % (line, ' ' * (15 - len(line)))
            # line = '%sOut: %s  In: %s\l' % (line, [str(y) for y in x.liveliness['out']], [str(y) for y in x.liveliness['in']])
            s += line
            #s += '%s\t%s\n' % (x, x.liveliness['out'])
        return s

    def __str__(self):
        s = ''
        for x in self.instructions:
            line = '%s' % x
            line = '%s%s\n' % (line, ' ' * (15 - len(line)))
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
        self.stack_pointer = 0

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

    def new_stack_var(self):
        """Return the next available stack location: rounded to 4
        Autoincremented.

        """
        s = self.stack_pointer
        self.stack_pointer += 4
        return s

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
        if self.stack_pointer > 0:
            asm.append(AsmInstruction('addi', '$sp', '$sp', -self.stack_pointer))
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
        # if ssa:
            # self.update_ssa()
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
        """Convert from generic intermediate code to mips three address
        compatible. Some operations only accept registers: such as =*/%, while
        others, like +, cannot add two numbers > 16 bits each. This function
        splits up such instructions into multiple register assignments and
        adidtion.
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
                if isinstance(ins, ICIf) and isinstance(ins.if_var, Integer):
                    a = self.new_var()
                    block.instructions.insert(i, ICAssign(a, ins.if_var))
                    ins.if_var = a
                    ins.add_used(a)
                    i += 1
                if isinstance(ins, ICWhileDo) and isinstance(ins.while_var, Integer):
                    a = self.new_var()
                    block.instructions.insert(i, ICAssign(a, ins.while_var))
                    ins.while_var = a
                    ins.add_used(a)
                    i += 1
                if isinstance(ins, ICDoWhile) and isinstance(ins.while_var, Integer):
                    a = self.new_var()
                    block.instructions.insert(i, ICAssign(a, ins.while_var))
                    ins.while_var = a
                    ins.add_used(a)
                    i += 1
                i += 1

    def update_liveliness(self):
        """Loop through all instructions and update their in and out sets.
        Calculate how many times a variable is used.

        """
        for block in self.blocks:
            block.liveliness['out'] = set()
            block.liveliness['in'] = set()
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
                # Add defined variables
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
                # raise ValueError("NOT ENOUGH REGISTERS")
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
            graph.colorize(node, ICContext.TEMP_REGS[graph.color(node)])
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
        stack_counter = self.new_stack_var()
        for block in self.blocks:
            i = 0
            while i < len(block.instructions):
                ins = block.instructions[i]
                if isinstance(ins, ICAssign) and var in ins.liveliness['defined']:
                    if var in ins.liveliness['used']:
                        # Restore before instruction
                        block.instructions.insert(i, ICLoadWord(var,
                            base=Variable('@stack'), offset=Integer(stack_counter)))
                        i += 1
                    block.instructions.insert(i + 1, ICStoreWord(var,
                        base=Variable('@stack'), offset=Integer(stack_counter)))
                    i += 2
                    continue
                elif var in ins.liveliness['used']:
                    # Restore before instruction
                    block.instructions.insert(i, ICLoadWord(var,
                        base=Variable('@stack'), offset=Integer(stack_counter)))
                    i += 2
                    continue
                else:
                    i += 1

    def basic_blocks_to_png(self, program_name):
        """Output a graph of basic bocks to a file called
        program_name_basic_blocks.png

        Arguments:
        program_name - name of program

        """
        # Only try if pygraphviz is available
        try:
            import pygraphviz as pgz
        except ImportError:
            return
        graph = pgz.AGraph(directed=True)
        graph.node_attr['shape']='rectangle'
        for i in range(len(self.blocks)):
            a = "%s\n%s" % (i, self.blocks[i].graph_label())
            graph.add_node(a)
            for follow in self.blocks[i].follow:
                graph.add_edge(a, "%s\n%s" % (self.blocks.index(follow), follow.graph_label()))
        # graph.node_attr['style'] = 'filled'
        # for node in self.nodes():
            # graph.add_node(node, fillcolor=self.node_colors[node])
        # for nodeA in self.edges:
            # for nodeB in self.edges[nodeA]:
                # graph.add_edge(nodeA, nodeB)
        graph.draw('%s_basic_blocks.png' % program_name, prog='dot')

    def __str__(self):
        s = ''
        for x in self.blocks:
            s += '---------------------\n'
            s += str(x)
        return s
