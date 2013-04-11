class AsmInstruction(object):
    def __init__(self, op=None, arg1=None, arg2=None, arg3=None, comment=""):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.comment = comment

    def __str__(self):
        # to add the comments aligned correctly
        comment = lambda s: s + (" " * (30 - len(s))) + "# " + self.comment
        if self.arg1 is not None and self.arg2 is not None and self.arg3 is not None:
            return comment("%s %s, %s, %s" % (self.op, self.arg1, self.arg2, self.arg3))
        elif self.arg1 is not None and self.arg2 is not None:
            return comment("%s %s, %s" % (self.op, self.arg1, self.arg2))
        elif self.arg1 is not None:
            return comment("%s %s" % (self.op, self.arg1))
        else:
            return comment(self.op)


def write_asm_to_file(program_name, asm):
    """Write out program to a file called
    program_name.asm

    Arguments:
    program_name - name of program

    """
    out = open('%s.asm' % program_name, 'w')
    out.write('.data\n')
    out.write('out_of_bounds: .asciiz "Proto Runtime Error: Attempt to access array out of bounds.\\n"\n')
    out.write('.text\n')
    out.write('# Exception handler\n');
    out.write('exc_oob:\nli $v0, 4\nla $a0, out_of_bounds\nsyscall\n')
    out.write('li $a0, -1\nli $v0, 10\nsyscall\n')
    out.write("# Main code\n")
    out.write('main:\n')
    for a in asm:
        out.write('%s\n' % a)
    # Exit gracefully
    out.write('# Exit gracefully\nli $v0, 10\nsyscall\n')
