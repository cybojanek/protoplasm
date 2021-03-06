from ASMCode import *
from Graph import UndirectedGraph


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
        if dest is not None:
            self.variables['defined'].add(dest)
        # TODO: make this nicer
        if arg1 is not None and not str(arg1).isdigit():
            self.variables['used'].add(arg1)
        if arg2 is not None and not str(arg2).isdigit():
            self.variables['used'].add(arg2)
        # Load and store use memory addresses and not variables
        if op == 'load':
            self.variables['defined'] = set([self.dest])
            self.variables['used'] = set()
        elif op == 'store':
            self.variables['used'] = set([self.arg1])
            self.variables['defined'] = set()

    def rename_dest(self, dest):
        """Rename destination variable.
        ONLY FOR THIS STATEMENT
        Updates defined set

        Arguments:
        dest - new name for destination

        """
        self.variables['defined'].remove(self.dest)
        if dest is not None:
            self.variables['defined'].add(dest)
        self.dest = dest
        if self.op == 'load':
            self.variables['defined'] = set([self.dest])
            self.variables['used'] = set()
        elif self.op == 'store':
            self.variables['used'] = set([self.arg1])
            self.variables['defined'] = set()

    def rename_arg1(self, arg1):
        """Rename arg1 variable.
        ONLY FOR THIS STATEMENT
        Updates used set

        Arguments:
        arg1 - new name for arg1

        """
        if self.arg1 in self.variables['used']:
            self.variables['used'].remove(self.arg1)
        if isinstance(arg1, str):
            self.variables['used'].add(arg1)
        self.arg1 = arg1
        if self.op == 'load':
            self.variables['defined'] = set([self.dest])
            self.variables['used'] = set()
        elif self.op == 'store':
            self.variables['used'] = set([self.arg1])
            self.variables['defined'] = set()

    def rename_arg2(self, arg2):
        """Rename arg2 variable.
        ONLY FOR THIS STATEMENT
        Updates used set

        Arguments:
        arg2 - new name for arg2

        """
        if self.arg2 in self.variables['used']:
            self.variables['used'].remove(self.arg2)
        if isinstance(arg2, str):
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

    def rename_variables_to_registers(self, variable_map):
        """Rename variables to registers.
        DOES NOT UPDATE LIVELINESS

        Arguments:
        variable_map - dict of name : register

        """
        if self.dest:
            self.dest = variable_map[self.dest]
        if self.arg1 is not None and isinstance(self.arg1, str):
            self.arg1 = variable_map[self.arg1]
        if self.arg2 is not None and isinstance(self.arg2, str):
            self.arg2 = variable_map[self.arg2]

    def is_binary_op(self):
        return self.dest is not None and self.arg1 is not None and self.arg2 is not None and self.op is not None

    def is_assignment(self):
        return self.dest is not None and self.arg1 is not None and self.arg2 is None and self.op is None

    def is_unary_op(self):
        return self.dest is not None and self.arg1 is not None and self.arg2 is None and self.op in ['-']

    def __str__(self):
        if self.dest and self.arg1 is not None and self.arg2 is not None and self.op:
            return '%s = %s %s %s' % (self.dest, self.arg1, self.op, self.arg2)
        elif self.dest and self.arg1 is not None and self.op:
            return '%s = %s %s' % (self.dest, self.op, self.arg1)
        elif self.dest and self.arg1 is not None and self.op:
            return '%s = %s %s' % (self.dest, self.op, self.arg1)
        elif self.dest and self.arg1 is not None:
            return '%s = %s' % (self.dest, self.arg1)
        elif self.dest and self.op:
            return '%s = %s' % (self.dest, self.op)
        elif self.arg1 is not None and self.op:
            return '%s %s' % (self.op, self.arg1)


class ThreeAddressContext(object):
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
        self.instructions = []
        self.variables = []
        self.counter = 0
        self.liveliness_graph = UndirectedGraph()
        self.variable_usage = {}

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

    def new_label(self):
        """Create a new label name
        Autoincremented.

        """
        name = 'label_%s' % self.counter
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

    def gencode(self):
        """Converts the list of ThreeAddress objects to ASMInstruction Objects,
           Returns AsmInstructionContext
        """
        asm = AsmInstructionContext()
        for i in self.instructions:
            asm.add_threeaddress(i)
        return asm

    def registerize(self, flatten_temp=False, ssa=False,
            propagate_variables=False, propagate_constants=False,
            eliminate_dead_code=False):
        """Perform optimization procedures and translate variables
        to use registers.

        Keyword Arguments:
        flatten_temp - look @ThreeAddressContext.flatten_temporary_assignments
        ssa - look @ThreeAddressContext.update_ssa

        """
        if flatten_temp:
            self.flatten_temporary_assignments()
        if propagate_variables:
            self.propagate_variables()
        if propagate_constants:
            self.propagate_constants()
        if ssa:
            self.update_ssa()
        if eliminate_dead_code:
            self.eliminate_dead_code()
        self.mipsify()
        # Keep looping until we allocated
        # will loop multiple times if not enough registers and we spill
        allocated = False
        while not allocated:
            self.update_liveliness()
            allocated = self.allocate_registers()
        # Remove self assignments
        self.eliminate_self_assignment()

    def flatten_temporary_assignments(self):
        """Loop through all instructions and flatten temp assignments like so:
        @1 = @0 * 2   --> a = @0 * 2
        a = @1
        Assumptions: any variable of the form @x where x is a number, will NOT
        be used after it is assigned to a variable.
        """
        i = 1
        # While loop, because we pop stuff
        while i < len(self.instructions):
            ins = self.instructions[i]
            prev_ins = self.instructions[i - 1]
            # Look for current assignment == previous destination
            # and previous destination is a temp var: @...
            if(ins.is_assignment() and prev_ins.dest == ins.arg1
                and prev_ins.dest[0] == '@'):
                prev_ins.rename_dest(ins.dest)
                self.instructions.pop(i)
            else:
                i += 1

    def propagate_variables(self):
        """Propagate variables and remove self assignments:
        a = 1;
        b = a;      --> a = a;        --> NOP
        b = b;      --> a = a;        --> NOP
        print(b);   --> print(a);

        """
        # Array of: (int, a,b)
        # from int onwards, change a to b
        changes = []
        for i in xrange(len(self.instructions) - 1, -1, -1):
            ins = self.instructions[i]
            # If we're doing: a = b then from here on, we can change
            # all a's to b's
            if ins.is_assignment() and isinstance(ins.arg1, str):
                changes.insert(0, (i, ins.dest, ins.arg1))
        # Rename everything using limits
        for i in xrange(len(self.instructions) - 1, -1, -1):
            ins = self.instructions[i]
            # Rename from bottom up
            for c in xrange(len(changes) - 1, -1, -1):
                line, orig, new = changes[c]
                if i >= line:
                    if ins.arg1 == orig:
                        ins.rename_arg1(new)
                    if ins.arg2 == orig:
                        ins.rename_arg2(new)
                    if ins.dest == orig:
                        ins.rename_dest(new)
            # Remove if it becomes self-referencing
            if ins.is_assignment() and ins.dest == ins.arg1:
                self.instructions.pop(i)

    def propagate_constants(self):
        """Solve constants: ie
        a = 2 + 3;    -->    a = 5;
        b = 4 * a;    -->    b = 20;
        print(b);     -->    print(20);

        """
        values = {}
        ops = {
            '-': lambda x, y: x - y,
            '+': lambda x, y: x + y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '%': lambda x, y: x % y
        }
        for i in self.instructions:
            # Replace arg1 if its defined
            if i.arg1 in values:
                i.rename_arg1(values[i.arg1])
            # Replace arg2 if its defined
            if i.arg2 in values:
                i.rename_arg2(values[i.arg2])
            # If its a binary op and both are ints, we can calculate now
            # Changes it to an assignment statement
            if i.is_binary_op() and isinstance(i.arg1, int) and \
                isinstance(i.arg2, int):
                result = ops[i.op](i.arg1, i.arg2)
                i.rename_arg1(result)
                i.rename_arg2(None)
                i.op = None
            # If its an assignment and the source is an int
            # we can save it for future lookup
            if i.is_assignment() and isinstance(i.arg1, int):
                values[i.dest] = i.arg1

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

    def eliminate_dead_code(self):
        """Eliminate unused variables and self assignments

        """
        used = set()
        add_only_variables = lambda x: used.add(x) if isinstance(x, str) else None
        # Move bottom up
        for i in xrange(len(self.instructions) - 1, -1, -1):
            ins = self.instructions[i]
            # If the result is not used below us...then remove it
            if (ins.is_assignment() or ins.is_binary_op() or ins.is_unary_op()) \
                and ins.dest not in used:
                self.instructions.pop(i)
            # If its used, but its self referencing...then remove it
            elif ins.is_assignment() and ins.dest == ins.arg1:
                self.instructions.pop(i)
            # Otherwise add both arguments (filters to only strings)
            else:
                add_only_variables(ins.arg1)
                add_only_variables(ins.arg2)

    def mipsify(self):
        """Convert from generic three address to mips three address compatible
        Some operations only accept registers: such as =*/%, while others,
        like +, cannot add two numbers > 16 bits each. This function splits up
        such instructions into multiple register assignments and adidtion.
        addi is currently not implemented

        """
        i = 0
        while i < len(self.instructions):
            ins = self.instructions[i]
            # Replace with registers if either is an int
            if ins.is_binary_op() and ins.op in ('/', '*', '%', '-', '+'):
                if isinstance(ins.arg1, int):
                    a = self.new_var()
                    self.instructions.insert(i, ThreeAddress(dest=a, arg1=ins.arg1))
                    ins.rename_arg1(a)
                    i += 1
                if isinstance(ins.arg2, int):
                    a = self.new_var()
                    self.instructions.insert(i, ThreeAddress(dest=a, arg1=ins.arg2))
                    ins.rename_arg2(a)
                    i += 1
            i += 1

    def eliminate_self_assignment(self):
        """After assigning registers, some assignments might be of the form:
        b = a;    -->    $t0 = $t0;
        This function removes such assignments.
        NOTE: propagate variables and constants ALREADY tries to do this
        before registers are assigned!!

        """
        i = 0
        while i < len(self.instructions):
            ins = self.instructions[i]
            if ins.is_assignment() and ins.dest == ins.arg1:
                self.instructions.pop(i)
            else:
                i += 1

    def update_liveliness(self):
        """Loop through all instructions and update their in and out sets.
        Calculate how many times a variable is used.

        """
        if len(self.instructions) == 0:
            return
        for ins in self.instructions:
            ins.variables['out'] = set()
            ins.variables['int'] = set()
        # Keep looping while one of the sets has changed
        changed = True
        while changed:
            changed = False
            # The last one doesn't have a next
            changed = changed or self.instructions[-1].update_variable_sets()
            # Bottom up, update in's and out's, using next statement
            for i in xrange(len(self.instructions) - 2, -1, -1):
                changed = changed or self.instructions[i].update_variable_sets(
                    next_ta=self.instructions[i + 1])
        # Now build up a graph of which variables need to be alive at the
        # same time
        self.liveliness_graph = UndirectedGraph()
        for ta in self.instructions:
            # Add defined variables - will be single nodes if not conflicting
            for i in ta.variables['defined']:
                self.liveliness_graph.add_node(i)
            # All the in variables that conflict with each other
            for i in ta.variables['in']:
                self.liveliness_graph.add_node(i)
                for j in ta.variables['in']:
                    if i != j:
                        self.liveliness_graph.add_edge(i, j)
        # Calculate how many times each variable is used
        self.variable_usage = {}
        for ins in self.instructions:
            for v in ins.variables['used']:
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
            if graph.degree(node) < len(ThreeAddressContext.TEMP_REGS):
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
            possible_regs = ThreeAddressContext.ALL_TEMP_REGS.difference(
                neighbor_regs)
            # If we don't have something to color with, then spill
            # return false, and wait to be called again
            if len(possible_regs) == 0:
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
                ThreeAddressContext.TEMP_REGS[graph.color(node)])
        # Rename all variables
        for ta in self.instructions:
            if ta.op == 'load':
                ta.rename_dest(var_map[ta.dest])
            elif ta.op == 'store':
                ta.rename_arg1(var_map[ta.arg1])
            else:
                ta.rename_variables_to_registers(var_map)
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
        for x in self.instructions:
            s += '%s\n' % (x)
        return s
