from ASMCode import *

class ThreeAddress(object):

    def __init__(self, dest=None, arg1=None, arg2=None, op=None):
        """A new three address object: dest = arg1 [op] [arg2]
        Have the form:
        dest = arg1
        dest = op arg1
        dest = arg1 op arg2

        Arguments:
                Keyword Arguments:
        dest - destination variable
        arg1 - first argument
        arg2 - second argument
        op - operator



        """
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op
        self.variables = {
            'in': set(),
            'out': set(),
            'used': set(),
            'defined': set()
        }
        if dest:
            self.variables['defined'].add(dest)
        # TODO: make this nicer
        if arg1 and not str(arg1).isdigit():
            self.variables['used'].add(arg1)
        if arg2 and not str(arg2).isdigit():
            self.variables['used'].add(arg2)

    def rename_dest(self, dest):
        """Rename destination variable.
        ONLY FOR THIS STATEMENT
        Updates defined set

        Arguments:
        dest - new name for destination

        """
        self.variables['defined'].remove(self.dest)
        self.variables['defined'].add(dest)
        self.dest = dest

    def rename_arg1(self, arg1):
        """Rename arg1 variable.
        ONLY FOR THIS STATEMENT
        Updates used set

        Arguments:
        arg1 - new name for arg1

        """
        self.variables['used'].remove(self.arg1)
        self.variables['used'].add(arg1)
        self.arg1 = arg1

    def rename_arg2(self, arg2):
        """Rename arg2 variable.
        ONLY FOR THIS STATEMENT
        Updates used set

        Arguments:
        arg2 - new name for arg2

        """
        self.variables['used'].remove(self.arg2)
        self.variables['used'].add(arg2)
        self.arg2 = arg2

    def update_variable_sets(self, next_ta=None):
        """Update in and out sets.

        Keyword Arguments:
        next_ta - the three address after this one (used to update out set)
            if None given, then Out not updated (good for last statement)

        Return:
        boolean of whether something was changed or not

        """
        changed = False
        if next_ta:
            # Out(n) = In(n + 1)
            changed, self.variables['out'] = (
                not(self.variables['out'] == next_ta.variables['in']),
                next_ta.variables['in'])
        # In(n) = Used(n) U (Out(n) - Defined(n))
        new_in = self.variables['used'].union(
            self.variables['out'].difference(self.variables['defined']))
        changed, self.variables['in'] = (
            (changed or not(self.variables['in'] == new_in)), new_in)
        return changed

    def __str__(self):
        if self.dest and self.arg1 and self.arg2 and self.op:
            return '%s = %s %s %s' % (self.dest, self.arg1, self.op, self.arg2)
        elif self.dest and self.arg1 and self.op:
            return '%s = %s %s' % (self.dest, self.op, self.arg1)
        elif self.dest and self.arg1 and self.op:
            return '%s = %s %s' % (self.dest, self.op, self.arg1)
        elif self.dest and self.arg1:
            return '%s = %s' % (self.dest, self.arg1)
        elif self.dest and self.op:
            return '%s = %s' % (self.dest, self.op)
        elif self.arg1 and self.op:
            return '%s %s' % (self.op, self.arg1)


class ThreeAddressContext(object):

    def __init__(self):
        """Keeps track of the ASTNode to address context translation

        """
        self.instructions = []
        self.variables = []
        self.counter = 0

    def add_instruction(self, ins):
        """Add a ThreeAddress to the instruction list

        Arguments:
        ins - ThreeAddress

        """
        self.instructions.append(ins)

    def new_var(self):
        """Create a new temporary variable.
        Autoincremented.

        """
        name = '@%s' % self.counter
        self.counter += 1
        return name

    def add_var(self, var):
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

    def registerize(self, flatten_temp=False, ssa=False):
        """Perform optimization procedures and translate variables
        to use registers.

        Keyword Arguments:
        flatten_temp - look @ThreeAddressContext.flatten_temporary_assignments
        ssa - look @ThreeAddressContext.update_ssa

        """
        self.update_immediates()

        if flatten_temp:
            self.flatten_temporary_assignments()
        if ssa:
            self.update_ssa()
        self.update_liveliness()

    def update_immediates(self):
        """
        Loop through all instructions and replace silly immiedates like this
        a = 2 + 2   --> a = 4
        """
        for i in self.instructions:
            if i.op and i.arg1 and i.arg2:
                if(str(i.arg1).isdigit() and str(i.arg2).isdigit()):
                    if i.op == "+": i.arg1 = i.arg1 + i.arg2
                    if i.op == "-": i.arg1 = i.arg1 + i.arg2
                    if i.op == "*": i.arg1 = i.arg1 * i.arg2
                    if i.op == "/": i.arg1 = i.arg1 / i.arg2
                    if i.op == "%": i.arg1 = i.arg1 % i.arg2
                    i.arg2 = None
                    i.op = None


    def flatten_temporary_assignments(self):
        """TODO:
        Its not really necessary to do this fully
        you only really need to replace a = $1, because liveliness analysis
        will detect that the rest don't actually conflict.
        ALTHOUGH, you do save a register when building up the value of a

        Loop through all instructions and flatten temp assignments like this:
        $1 = $0 * 2   --> a = $0 * 2
        a = $1
        Assumptions: any variable of the form $x where x is a number, will NOT
        be used after it is assigned to a variable.
        """
        pass

    def update_ssa(self):
        """Translate three address code to use Static Single Assignment
        variables.

        """
        vc = {}
        for i in self.instructions:
            # If its been declared before and updated, use updated
            # TODO: clean this up
            if isinstance(i.arg1, str) and i.arg1 in vc and vc[i.arg1] != 0:
                i.rename_arg1('%s%s' % (i.arg1, vc[i.arg1]))
            if isinstance(i.arg2, str) and i.arg2 in vc and vc[i.arg2] != 0:
                i.rename_arg2('%s%s' % (i.arg2, vc[i.arg2]))
            # If i.dest is not None and its been declared before, update it
            if i.dest and i.dest in vc:
                vc[i.dest] += 1
                i.rename_dest('%s%s' % (i.dest, vc[i.dest]))
            # Otherwise, first time, so use 0
            elif i.dest:
                vc[i.dest] = 0

    def update_liveliness(self):
        """Loop through all instructions and update their in and out sets.

        """
        if len(self.instructions) == 0:
            return
        changed = True
        while changed:
            changed = False
            changed = changed or self.instructions[-1].update_variable_sets()
            for i in xrange(len(self.instructions) - 2, -1, -1):
                changed = changed or self.instructions[i].update_variable_sets(
                    next_ta=self.instructions[i + 1])

    def gencode(self):
        """Converts the list of ThreeAddress objects to ASMInstruction Objects,
           Returns AsmInstructionContext
        """
        asm = AsmInstructionContext()
        for i in self.instructions:
            asm.add_threeaddress(i)
        return asm

    def liveliness_to_png(self, file_name):
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
        for ta in self.instructions:
            # Add defined variables - will be single nodes if not conflicting
            for i in ta.variables['defined']:
                graph.add_node(i)
            # All the in variables that conflict with each other
            for i in ta.variables['in']:
                graph.add_node(i)
                for j in ta.variables['in']:
                    if i != j:
                        graph.add_edge(i, j)
        # The last one also needs out, bc the next in is empty
        for i in self.instructions[-1].variables['out']:
            for j in self.instructions[-1].variables['out']:
                if i != j:
                    graph.add_edge(i, j)
        for i in ['circo', 'fdp']:
            graph.draw('%s_%s' % (i, file_name), prog=i)

    def __str__(self):
        s = ''
        for x in self.instructions:
            s += '%s\n' % (x)
        return s
