from Graph import UndirectedGraph
from ASMCode import AsmInstruction


class Variable(object):
    def __init__(self, value):
        self.value = value
        self.is_pointer = False

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)


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
    REGISTER_CONSTANTS = {
        Variable('@stack'): '$sp',
        Variable('@frame'): '$fp'
    }

    def __init__(self):
        """Intermediate Code object

        """
        self.liveliness = {'in': set(), 'out': set(), 'used': set(),
                           'defined': set()}
        self.register_map = {}
        self.context = None
        self.stack_offset = 0

    def set_stack_offset(self, offset):
        """Set the additional stack offset to be used
        by the function of these blocks to accont
        for spilled variables

        Arguments:
        offset - offset in bytes

        """
        self.stack_offset = offset

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

    def register_or_tmp(self, variable, tmp_reg):
        if isinstance(variable, Variable): 
            return [], self.get_register_or_value(variable);
        else:
            return [AsmInstruction("li", tmp_reg, self.get_register_or_value(variable))], tmp_reg

    def to_tmp(self, variable, tmp_reg):
        if isinstance(variable, Variable): 
            return [AsmInstruction("move", tmp_reg, self.get_register_or_value(variable))], tmp_reg
        else:
            return [AsmInstruction("li", tmp_reg, self.get_register_or_value(variable))], tmp_reg

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
        if not(isinstance(dest, Variable) and (isinstance(arg1, Variable) or
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
        # Get instruction from op map
        op = ICBinaryOp.ASM_OPS[self.op]
        dest = self.get_register_or_value(self.dest)

        a = []
        if isinstance(self.arg1, Integer):
            arg1 = '$t0'
            a = a + [AsmInstruction('li', '$t0', self.arg1)]
        else:
            arg1 = self.get_register_or_value(self.arg1)
        if isinstance(self.arg1, Integer):
            arg2 = '$t1'
            a = a + [AsmInstruction('li', '$t1', self.arg2)]
        else:
            arg2 = self.get_register_or_value(self.arg2)

        # Short circuit logic for &&
        if self.op == '&&':
            label_set_0 = self.context.new_label(suffix='set_0')
            label_done = self.context.new_label(suffix='done')
            return a + [AsmInstruction('beqz', arg1, label_set_0, comment=str(self)),
                    AsmInstruction('move', dest, arg2),
                    AsmInstruction('b', label_done),
                    AsmInstruction('%s:' % label_set_0),
                    AsmInstruction('li', dest, 0),
                    AsmInstruction('%s:' % label_done)]
        # Short circuit logic for ||
        elif self.op == '||':
            label_use_arg1 = self.context.new_label(suffix='use_arg1')
            label_done = self.context.new_label(suffix='done')
            return a + [AsmInstruction('bnez', arg1, label_use_arg1, comment=str(self)),
                    AsmInstruction('move', dest, arg2),
                    AsmInstruction('b', label_done),
                    AsmInstruction('%s:' % label_use_arg1),
                    AsmInstruction('move', dest, arg1),
                    AsmInstruction('%s:' % label_done)]
        # op Rd, Rs, Rt    Rd = Rs op Rt
        return a + [AsmInstruction(op, dest, arg1, arg2, comment=str(self))]

    def __str__(self):
        return "%s = %s %s %s" % (self.dest, self.arg1, self.op, self.arg2)


class ICFunctionArgumentLoad(IC):
    """Load an argument at the start of a function call
    """

    def __init__(self, dest, number):
        super(ICFunctionArgumentLoad, self).__init__()
        if not(isinstance(dest, Variable)):
            raise ValueError("Unsupported destination")
        self.dest = dest
        self.number = number
        self.add_defined(dest)

    def generate_assembly(self):
        dest = self.get_register_or_value(self.dest)
        if 0 <= self.number <= 3:
            return [AsmInstruction('move', dest, '$a%s' % self.number, comment=str(self))]
        else:
            return [AsmInstruction('lw', dest, '%s($fp)' % (-4 * (self.number - 3)), comment=str(self))]

    def __str__(self):
        return '%s = arg%s' % (self.dest, self.number)


class ICFunctionArgumentSave(IC):
    """Save an argument for a function call
    """

    def __init__(self, src, number):
        super(ICFunctionArgumentSave, self).__init__()
        if not(isinstance(src, Variable) or isinstance(src, Integer)):
            raise ValueError("Unsupported source")
        self.src = src
        self.number = number
        self.add_used(src)

    def generate_assembly(self):
        if isinstance(self.src, Variable):
            src = self.get_register_or_value(self.src)
            if 0 <= self.number <= 3:
                return [AsmInstruction('move', '$a%s' % self.number, src, comment=str(self))]
            else:
                return [AsmInstruction('sw', src, '%s($sp)' % (-4 * (self.number - 3)), comment=str(self))]
        else:
            if 0 <= self.number <= 3:
                return [AsmInstruction('li', '$a%s' % self.number, self.src, comment=str(self))]
            else:
                return [AsmInstruction('li', '$t0', self.src, comment=str(self)),
                        AsmInstruction('sw', '$t0', '%s($sp)' % (-4 * (self.number - 3)))]

    def __str__(self):
        return 'arg%s = %s' % (self.number, self.src)


class ICFunctionCall(IC):
    """Call a function
    """

    def __init__(self, dest, name, arguments):
        super(ICFunctionCall, self).__init__()
        if not isinstance(dest, Variable):
            raise ValueError("Unsupported destination")
        self.dest = dest
        self.name = name
        self.arguments = arguments
        self.add_defined(dest)
        # for arg in self.arguments:
            # self.add_used(arg)

    def first_pass(self):
        pass

    def generate_assembly(self):
        dest = self.get_register_or_value(self.dest)
        a = [AsmInstruction('move', '$fp', '$sp', comment='Save frame pointer')]
        if len(self.arguments) > 4:
            a = a + [AsmInstruction('addi', '$sp', '$sp', -4 * (len(self.arguments) - 4))]
        return a + [AsmInstruction('jal', 'func_%s' % self.name, comment=str(self)),
                    AsmInstruction('move', dest, '$v0')]

    def __str__(self):
        return "%s = %s()" % (self.dest, self.name)


class ICFunctionDeclare(IC):
    """Declare a function and its body code
    """

    def __init__(self, name, body_block):
        super(ICFunctionDeclare, self).__init__()
        self.name = name
        self.body_block = body_block

    def first_pass(self):
        # Make a label for the body block
        self.body_block.add_start_label('func_%s' % (self.name))

    def generate_assembly(self):
        # Get parameters
        # Save s0 - s8 and ra
        used_registers = set(self.register_map.values()).intersection(ICContext.ALL_TEMP_REGS)
        a = [AsmInstruction('addi', '$sp', '$sp', -4 * (len(used_registers) + 2), comment=str(self))]
        for i, v in enumerate(used_registers):
            a.append(AsmInstruction('sw', v, '%s($sp)' % (i * 4), comment='Save: %s' % v))
        a.append(AsmInstruction('sw', '$ra', '%s($sp)' % (4 * (len(used_registers))), comment='Save return address'))
        a.append(AsmInstruction('sw', '$fp', '%s($sp)' % (4 * (len(used_registers) + 1)), comment='Save frame pointer'))
        a.append(AsmInstruction('addi', '$sp', '$sp', -self.stack_offset, comment='Offset for spilled variables'))
        return a

    def __str__(self):
        return 'function: %s' % (self.name)


class ICFunctionReturn(IC):
    """Return from a function
    """

    def __init__(self, variable):
        super(ICFunctionReturn, self).__init__()
        if not(isinstance(variable, Variable) or isinstance(variable, Integer) or variable is None):
            raise ValueError("Unsupported return type")
        self.variable = variable
        if isinstance(variable, Variable):
            self.add_used(variable)

    def first_pass(self):
        pass

    def generate_assembly(self):
        if self.variable is None:
            a = []
        elif isinstance(self.variable, Integer):
            a = [AsmInstruction('li', '$v0', self.variable, comment=str(self))]
        elif isinstance(self.variable, Variable):
            src = self.get_register_or_value(self.variable)
            a = [AsmInstruction('move', '$v0', src, comment=str(self))]
        # Restore ra and sp
        a.append(AsmInstruction('addi', '$sp', '$sp', self.stack_offset))
        used_registers = set(self.register_map.values()).intersection(ICContext.ALL_TEMP_REGS)
        for i, v in enumerate(used_registers):
            a.append(AsmInstruction('lw', v, '%s($sp)' % (i * 4), comment='Load: $s%s' % i))
        a.append(AsmInstruction('lw', '$ra', '%s($sp)' % (4 * (len(used_registers))), comment='Load return address'))
        a.append(AsmInstruction('lw', '$fp', '%s($sp)' % (4 * (len(used_registers) + 1)), comment='Load frame pointer'))
        a.append(AsmInstruction('move', '$sp', '$fp', comment='Restore stack pointer'))
        # a.append(AsmInstruction('addi', '$sp', '$sp', 4 * (len(used_registers) + 1), comment=str(self)))
        return a + [AsmInstruction('jr', '$ra')]

    def __str__(self):
        return 'return: %s' % (self.variable)


class ICDoWhile(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, do_part_block, while_var, while_part_block, next_block):
        super(ICDoWhile, self).__init__()
        if not(isinstance(while_var, Variable) or
               isinstance(while_var, Integer)):
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
        if isinstance(self.while_var, Integer):
            arg1 = '$t0'
            a = [AsmInstruction('li', '$t0', self.while_var)]
        else:
            arg1 = self.get_register_or_value(self.while_var)
            a = []

        # At end of statements, jump back to condition checking
        #self.end_if_block.add_end_branch(self.condition_label)

        # Make a label for the end block
        next_block_label = self.context.new_label(suffix='end_while')
        self.next_block.add_start_label(next_block_label)
        return a + [AsmInstruction('beqz', arg1, next_block_label, comment=str(self)),
                AsmInstruction('b', self.do_label, comment='do again')]

    def __str__(self):
        return "do...while %s" % (self.while_var)


class ICFor(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, cond_var, cond_part_block, end_for_block, next_block):
        super(ICFor, self).__init__()
        if not(isinstance(cond_var, Variable) or
               isinstance(cond_var, Integer)):
            raise ValueError("Unsupported for statement")
        self.cond_var = cond_var
        self.add_used(cond_var)
        self.cond_part_block = cond_part_block
        self.end_for_block = end_for_block
        self.next_block = next_block

    def rename_used(self, old, new):
        if self.cond_var == old:
            self.remove_used(self.cond_var)
            self.cond_var = new
            self.add_used(new)

    def rename_defined(self, old, new):
        pass

    def first_pass(self):
        # Make a label for the do block
        self.cond_label = self.context.new_label(suffix='for_cond')
        self.cond_part_block.add_start_label(self.cond_label)
        # At end of statements, jump back to condition checking
        self.end_for_block.add_end_branch(self.cond_label)

    def generate_assembly(self):
        # Get the condition register
        if isinstance(self.cond_var, Integer):
            arg1 = '$t0'
            a = [AsmInstruction('li', '$t0', self.cond_var)]
        else:
            arg1 = self.get_register_or_value(self.cond_var)
            a = []

        # Make a label for the end block
        next_block_label = self.context.new_label(suffix='end_for')
        self.next_block.add_start_label(next_block_label)

        return a + [AsmInstruction('beqz', arg1, next_block_label, comment=str(self))]

    def __str__(self):
        return "for... %s" % (self.cond_var)


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
        if isinstance(self.if_var, Integer):
            arg1 = '$t0'
            a = [AsmInstruction('li', '$t0', self.if_var)]
        else:
            arg1 = self.get_register_or_value(self.if_var)
            a = []
        # Make a label for the end block
        end_if_label = self.context.new_label(suffix='end_if')
        # Add the label to the start of that block
        self.end_if_block.add_start_label(end_if_label)
        if self.else_block is None:
            # If false, then branch to next end if block
            return a + [AsmInstruction('beqz', arg1, end_if_label, comment=str(self))]
        # Make a label for the else block
        else_label = self.context.new_label(suffix='else')
        # Add the else label to the else block
        self.else_block.add_start_label(else_label)
        # Tell the then_block to branch to end_if_block (to skip else block)
        self.then_block.add_end_branch(end_if_label)
        # If false, then branch to the else_block
        return a + [AsmInstruction('beqz', arg1, else_label, comment=str(self))]

    def __str__(self):
        return "if %s then...%s" % (
            self.if_var, '' if self.else_block is None else 'else...')


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


class ICLoadWord(IC):
    """Load a word
    """
    def __init__(self, dest, base=None, offset=None, elem=None):
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

        if isinstance(elem, Variable):
            self.add_used(elem)

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
        self.elem = elem
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
        if self.elem:
            asm1, elem = self.to_tmp(self.elem, "$t0")
            asm2, base = self.to_tmp(self.base, "$t1")
            dest = self.get_register_or_value(self.dest)
            asm = asm1 + asm2
            asm.append(AsmInstruction("addi", elem, elem, "1"))
            asm.append(AsmInstruction("sll", elem, elem, "2"))
            asm.append(AsmInstruction("add", elem, elem, base))
            asm.append(AsmInstruction("lw", dest, "(" + elem + ")", comment=str(self)))
            return asm
        else:
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
                arg2 = '%s' % (self.base)
            elif isinstance(self.offset, Variable):
                # offset is register
                arg2 = '(%s)' % (self.get_register_or_value(self.offset))

            return [AsmInstruction('lw', arg1, arg2, comment=str(self))]

    def __str__(self):
        return "%s = %s[%s]" % (self.dest, self.base, self.offset)


class ICLoadGlobal(ICLoadWord):
    """Load a global argument
    """
    def __init__(self, variable):
        super(ICLoadGlobal, self).__init__(variable, base=Label('global_%s' % variable))
        self.variable = variable

    def __str__(self):
        return "%s = global %s" % (self.variable, self.variable)


class ICAllocMemory(IC):
    """Allocate memory
    """

    def __init__(self, dest, length):
        super(ICAllocMemory, self).__init__()
        if not(isinstance(dest, Variable) or isinstance(dest, Integer)):
            raise ValueError("Bad memory allocation dest")
        if not(isinstance(length, Variable) or isinstance(length, Integer)):
            raise ValueError("Bad memory allocation len")
        self.dest = dest
        self.length = length
        self.add_defined(dest)
        self.add_used(length)

    def rename_used(self, old, new):
        if self.dest == old:
            self.remove_used(self.dest)
            self.dest = new
            self.add_used(self.dest)
        if self.length == old:
            self.remove_used(self.length)
            self.length = new
            self.add_used(self.dest)

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        asm, dest = self.register_or_tmp(self.dest, "$t1")
        length = self.get_register_or_value(self.length)

        if isinstance(self.length, Integer):
            # li Rd, Imm    Rd = Imm
            asm.append(AsmInstruction('li', '$a0', (length+1)*4, comment=str(self)))
        else:
            # move Rd, Rs   Rd = Rs
            asm.append(AsmInstruction('move', '$a0', length, comment=str(self)))

            # Add one word to the the length, and multiply by 4
            asm.append(AsmInstruction('addi', '$a0', '$a0', 1, comment=str(self)))
            asm.append(AsmInstruction('sll', '$a0', '$a0', 2, comment=str(self)))

        # li Rd, Imm    Rd = Imm
        # syscall
        asm.append(AsmInstruction('li', '$v0', 9))
        asm.append(AsmInstruction('syscall'))

        # move Rd, Rs   Rd = Rs
        asm.append(AsmInstruction('move', dest, "$v0", comment=str(self)))

        return asm

    def __str__(self):
        return "%s = AllocMemory(%s)" % (self.dest, str(self.length))


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


class ICBoundCheck(IC):
    """Do a print statement for an integer
    """

    def __init__(self, base, elem):
        super(ICBoundCheck, self).__init__()
        if not(isinstance(base, Variable)):
            raise ValueError("Unsupported bound check operation")
        self.base = base
        self.elem = elem

        self.add_used(base)
        self.add_used(elem)

    def rename_used(self, old, new):
        if self.base == old:
            self.remove_used(self.base)
            self.base = new
            self.add_used(self.base)
        if self.elem == old:
            self.remove_used(self.elem)
            self.elem = new
            self.add_used(self.elem)       

    def rename_defined(self, old, new):
        pass

    def generate_assembly(self):
        base = self.get_register_or_value(self.base)
        asm, elem = self.register_or_tmp(self.elem, "$t1")

        asm.append(AsmInstruction('lw', "$t0", "0("+base+")", comment=str(self)))
        asm.append(AsmInstruction('bge', elem, "$t0", "exc_oob", comment=str(self)))

        return asm

    def __str__(self):
        return "array_bound_check(%s, %s)" % (self.base, self.elem)


class ICStoreWord(IC):
    """Store a word
    """
    def __init__(self, src, base=None, offset=None, elem=None):
        """
        Arguments:
        src - variable name (register)

        Keyword Arguments:
        base - label or variable
        offset - variable or integer

        Allowable combinations:
        label/var, var/int, label/None, None/var

        """
        super(ICStoreWord, self).__init__()
        if isinstance(elem, Variable):
            self.add_used(elem)

        if isinstance(base, Label) and isinstance(offset, Variable):
            # base is label and offset is register
            self.add_used(offset)
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
        self.elem = elem
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
        if self.elem:
            asm1, addr = self.to_tmp(self.elem, "$t0")
            asm2, arg1 = self.to_tmp(self.src, "$t1")
            asm3, base = self.to_tmp(self.base, "$t3")

            asm = asm1+asm2+asm3
            asm.append(AsmInstruction("addi", addr, addr, "1"))
            asm.append(AsmInstruction("sll", addr, addr, "2"))
            asm.append(AsmInstruction("add", addr, base, addr))

            return asm+[AsmInstruction('sw', arg1, "("+addr+")", comment=str(self))]

        else:
            asm, arg1 = self.register_or_tmp(self.src, "$t3")
            arg2 = ''

            if isinstance(self.base, Label) and isinstance(self.offset, Variable):
                # base is label and offset is register
                arg2 = '%s(%s)' % (self.base, self.get_register_or_value(self.offset))
            elif isinstance(self.base, Variable) and isinstance(self.offset, Integer):
                # base is register and offset is integer
                arg2 = '%s(%s)' % (self.offset, self.get_register_or_value(self.base))
            elif isinstance(self.base, Label):
                # base is label
                arg2 = '%s' % self.base
            elif isinstance(self.offset, Variable):
                # offset is register
                arg2 = '(%s)' % (self.get_register_or_value(self.offset))
            return asm+[AsmInstruction('sw', arg1, arg2, comment=str(self))]

    def __str__(self):
        return "*(%s+%s) = %s" % (self.base, self.offset, self.src)


class ICStoreGlobal(ICStoreWord):
    """Store a global
    """

    def __init__(self, src, dest):
        super(ICStoreGlobal, self).__init__(src, base=Label('global_%s' % dest))
        self.src, self.dest = src, dest

    def __str__(self):
        return "global %s = %s" % (self.dest, self.src)


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


class ICWhileDo(IC):
    """Assign variable to variable, or Integer to variable
    """
    def __init__(self, while_var, while_part_block, end_if_block, next_block):
        super(ICWhileDo, self).__init__()
        if not(isinstance(while_var, Variable) or
               isinstance(while_var, Integer)):
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
        if isinstance(self.while_var, Integer):
            arg1 = '$t0'
            a = [AsmInstruction('li', '$t0', self.while_var)]
        else:
            arg1 = self.get_register_or_value(self.while_var)
            a = []

        # At end of statements, jump back to condition checking
        self.end_if_block.add_end_branch(self.condition_label)

        # Make a label for the end block
        end_while_label = self.context.new_label(suffix='end_while')
        self.next_block.add_start_label(end_while_label)

        return a + [AsmInstruction('beqz', arg1, end_while_label, comment=str(self))]

    def __str__(self):
        return "while %s do..." % (self.while_var)


class ICContextBasicBlock(object):

    def __init__(self):
        """Collection of instructions in a basic block

        """
        self.start_label = None
        self.branch_label = None
        self.instructions = []
        self.follow = []
        self.precede = []
        self.liveliness = {'in': set(), 'out': set()}

    def get_root_and_children(self):
        visited = set()
        q = [self]
        ret = []
        while len(q) != 0:
            b = q.pop()
            ret.append(b)
            for follow in b.follow:
                if follow not in visited:
                    q.append(follow)
                    visited.add(follow)
        return ret

    def add_follow(self, block):
        self.follow.append(block)
        block.precede.append(self)

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
            # BFS like traversal
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
                if len(c.instructions) == 0:
                    for x in c.follow:
                        if x not in visited:
                            candidates.append(x)
                else:
                    follower_blocks.append(c)

            # Then loop through its follows
            for follow in follower_blocks:
                changed = changed or self.instructions[-1].update_variable_sets(next_ic=follow.instructions[0])
            # Bottom up, update in's and out's, using next statement
            for i in xrange(len(self.instructions) - 2, -1, -1):
                changed = changed or self.instructions[i].update_variable_sets(
                    next_ic=self.instructions[i + 1])
            block_changed = block_changed or changed
        return block_changed

    def graph_label(self):
        s = ''
        for x in self.instructions:
            line = '%s\l' % x
            # line = '%s%s\l' % (line, ' ' * (15 - len(line)))
            # line = '%sOut: %s  In: %s\l' % (line, [str(y) for y in x.liveliness['out']], [str(y) for y in x.liveliness['in']])
            s += line
            #s += '%s\t%s\n' % (x, x.liveliness['out'])
        return s

    def __str__(self):
        s = ''
        for x in self.instructions:
            line = '%s' % x
            # line = '%s%s' % (line, ' ' * (20 - len(line)))
            # line = '%sOut: %s  In: %s\n' % (line, [str(y) for y in x.liveliness['out']], [str(y) for y in x.liveliness['in']])
            # line = '%sOut: %s  Def: %s\n' % (line, [str(y) for y in x.liveliness['out']], [str(y) for y in x.liveliness['defined']])
            s += line
            #s += '%s\t%s\n' % (x, x.liveliness['out'])
        return s


class ICContext(object):
    TEMP_REGS = {
        '$s0': '#FF7400',
        '$s1': '#009999',
        '$s2': '#FF7373',
        '$s3': '#BF7130',
        '$s4': '#A60000',
        '$s5': '#008500',
        '$s6': '#00CC00',
        '$s7': '#D2006B',
        # '$s8': '#574DD8',
    }
    ALL_TEMP_REGS = set(TEMP_REGS.keys())

    def __init__(self, globals):
        """Keeps track of the ASTNode to address context translation

        """
        self.blocks = [ICContextBasicBlock()]
        self.variables = []
        self.counter = 0
        self.liveliness_graph = UndirectedGraph()
        self.all_graphs = []
        self.variable_usage = {}
        self.spilled_variables = set()
        self.stack_pointer = 0
        self.globals = globals

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
        self.mipsify()
        starter_blocks = filter(lambda x: len(x.precede) == 0, self.blocks)
        starter_blocks = map(lambda x: x.get_root_and_children(), starter_blocks)

        # self.update_liveliness()
        # Keep looping until we allocated
        # will loop multiple times if not enough registers and we spill
        for blocks in starter_blocks:
            self.liveliness_graph = UndirectedGraph()
            self.spilled_variables = set()
            self.stack_pointer = 0
            allocated = False
            while not allocated:
                self.update_liveliness(blocks)
                allocated = self.allocate_registers(blocks)
            self.all_graphs.append((self.blocks.index(blocks[0]), self.liveliness_graph))

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
                i += 1

    def update_liveliness(self, blocks):
        """Loop through all instructions and update their in and out sets.
        Calculate how many times a variable is used.

        """
        for block in blocks:
            block.liveliness['out'] = set()
            block.liveliness['in'] = set()
            for ins in block.instructions:
                # Clear up outs and ins
                ins.liveliness['out'] = set()
                ins.liveliness['in'] = set()
        # Update block liveliness
        # Last statement of each block sets its out to union of all follows
        changed = True
        while changed:
            changed = False
            for i in xrange(len(blocks) - 1, -1, -1):
                changed = changed or blocks[i].update_liveliness()
        # Now build up a graph of which variables need to be alive at the
        # same time
        self.liveliness_graph = UndirectedGraph()
        for block in blocks:
            for ins in block.instructions:
                # Add defined variables
                for i in ins.liveliness['defined']:
                    self.liveliness_graph.add_node(i)
                    # Need to still add this
                    for j in ins.liveliness['out']:
                        self.liveliness_graph.add_edge(i, j)
                # All the in variables that conflict with each other
                for i in ins.liveliness['in']:
                    self.liveliness_graph.add_node(i)
                    for j in ins.liveliness['in']:
                        if i != j:
                            self.liveliness_graph.add_edge(i, j)
        # Calculate how many times each variable is used
        # doesn't take any consideration of ifs nor whiles
        self.variable_usage = {}
        for block in blocks:
            for ins in block.instructions:
                # TODO: why does this break liveliness, but
                # get(x, 0) in lambda key does not?
                #for v in ins.liveliness['defined']:
                #    self.variable_usage[v] = 0
                for v in ins.liveliness['used']:
                    if v not in self.variable_usage:
                        self.variable_usage[v] = 1
                    else:
                        self.variable_usage[v] += 1

    def allocate_registers(self, blocks):
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
                # get its value, or 0, not used
                nodes = sorted(graph.nodes(),
                    key=lambda x: graph.degree(x) - self.variable_usage.get(x, 0))
                node = None
                for n in nodes:
                    if n not in self.spilled_variables:
                        node = n
                        break
                if node is None:
                    # Shit nothing else to spill right now
                    # So select one that hasnt been spilled yet
                    all_nodes = set([x[0] for x in stack] + [x for x in graph.nodes()])
                    possible_nodes = all_nodes.difference(self.spilled_variables)
                    if len(possible_nodes) == 0:
                        raise RuntimeError('Already spilled all the variables!')
                    node = max(possible_nodes,
                        key=lambda x: self.variable_usage.get(x, 0))
                    self.spill_variable(node, blocks)
                    return False
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
                self.spill_variable(node, blocks)
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
        for block in blocks:
            for ic in block.instructions:
                ic.set_register_map(var_map)
                ic.set_stack_offset(self.stack_pointer)
        return True

    def spill_variable(self, var, blocks):
        """Spill a variable, and store it to a memory location

        Arguments:
        var - variable to be spilled

        """
        self.spilled_variables.add(var)
        stack_counter = self.new_stack_var()
        for block in blocks:
            i = 0
            while i < len(block.instructions):
                ins = block.instructions[i]
                # If its being defined now
                if var in ins.liveliness['defined']:
                    # Its also used, so restore it
                    if var in ins.liveliness['used']:
                        # Restore before instruction
                        load = ICLoadWord(var, base=Variable('@stack'), offset=Integer(stack_counter))
                        load.set_context(self, block)
                        block.instructions.insert(i, load)   
                        i += 1
                    # Now save it back again
                    store = ICStoreWord(var, base=Variable('@stack'), offset=Integer(stack_counter))
                    store.set_context(self, block)
                    block.instructions.insert(i + 1, store)
                    i += 2
                    continue
                # Restore before instruction
                elif var in ins.liveliness['used']:
                    load = ICLoadWord(var, base=Variable('@stack'), offset=Integer(stack_counter))
                    load.set_context(self, block)
                    block.instructions.insert(i, load)
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
        if len(self.blocks) >= 1:
            graph.add_node("%s\n%s" % (0, self.blocks[0].graph_label()), style='filled', color='#458B00')
        for i in range(len(self.blocks)):
            a = "%s\n%s" % (i, self.blocks[i].graph_label())
            if len(self.blocks[i].follow) == 0:
                graph.add_node(a, style='filled', color='#DB2929')
            else:
                graph.add_node(a)
            for follow in self.blocks[i].follow:
                b = "%s\n%s" % (self.blocks.index(follow), follow.graph_label())
                if len(follow.follow) == 0:
                    graph.add_node(b, style='filled', color='#DB2929')
                graph.add_edge(a, b)
        graph.draw('%s_basic_blocks.png' % program_name, prog='dot')

    def __str__(self):
        s = ''
        for x in self.blocks:
            s += '---------------------\n'
            s += str(x)
        return s
