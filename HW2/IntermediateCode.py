

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
        name = '$%s' % self.counter
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

    def __str__(self):
        s = ''
        for x in self.instructions:
            s += '%s\n' % (x)
        return s
