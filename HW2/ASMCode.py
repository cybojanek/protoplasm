from IntermediateCode import *

MIN_SINT_16 = -(2 ** 15)
MAX_SINT_16 = (2 ** 15) - 1


def is_int(i):
    """Check if its an integer"""
    return isinstance(i, int)


def is_gt_16_bit(i):
    """Check if its out of bounds for 16 bit singed integer"""
    return is_int(i) and not (MIN_SINT_16 <= i <= MAX_SINT_16)


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

        if self.arg1 and self.arg2 and self.arg3:
            return comment("%s %s, %s, %s" % (self.op, self.arg1, self.arg2, self.arg3))
        elif self.arg1 and self.arg2:
            return comment("%s %s, %s" % (self.op, self.arg1, self.arg2))
        elif self.arg1:
            return comment("%s %s" % (self.op, self.arg1))
        else:
            return comment(self.op)


def asm_assign(ins, aic):
    if is_int(ins.arg1):
        # li Rd, Imm    Rd = Imm
        return [AsmInstruction('li', ins.dest, ins.arg1, comment=str(ins))]
    else:
        # move Rd, Rs   Rs = Rs
        return [AsmInstruction('move', ins.dest, ins.arg1)]


def asm_add(ins, aic):
    if ins.op != '+':
        raise TypeError('Instruction is not an addition operation!')
    if is_int(ins.arg1) or is_int(ins.arg2):
        raise TypeError('Addition can only use registers!')
    # add Rd, Rs, Rt
    return [AsmInstruction('add', ins.dest, ins.arg1, ins.arg2)]
    # TODO:
    # Re-implement addi - right now its too verbose and buggy
    # Adding two constants each > 16 bits is not allowed
    # if is_gt_16_bit(ins.arg1) and is_gt_16_bit(ins.arg2):
    #     raise TypeError('Cant add two integers which dont fit in 16 bits!')
    # # add Rd, Rs, Rt    Rd = Rs + Rt
    # elif not is_int(ins.arg1) and not is_int(ins.arg2):
    #     asm.append(AsmInstruction('add', ins.dest, ins.arg1, ins.arg2,
    #         comment=str(ins)))
    # # Two integers: at least one < 16 bits
    # elif is_int(ins.arg1) and is_int(ins.arg2):
    #     # arg1 is too big for addi
    #     if is_gt_16_bit(ins.arg1):
    #         asm.append(AsmInstruction('li', ins.dest, ins.arg1, comment=str(ins)))
    #         asm.append(AsmInstruction('addi', ins.dest, ins.dest, ins.arg2))
    #     # arg2 is too big for addi
    #     else:
    #         asm.append(AsmInstruction('li', ins.dest, ins.arg2, comment=str(ins)))
    #         asm.append(AsmInstruction('addi', ins.dest, ins.dest, ins.arg1))
    # elif is_int(ins.arg1):
    #     if is_gt_16_bit(ins.arg1):
    #         # li Rd, Imm        Rd = Imm
    #         # add Rd, Rs, Rt    Rd = Rs + Rt
    #         asm.append(AsmInstruction('li', ins.dest, ins.arg1, comment=str(ins)))
    #         asm.append(AsmInstruction('add', ins.dest, ins.dest, ins.arg2))
    #     else:
    #         asm.append(AsmInstruction('addi', ins.dest, ins.arg2, ins.arg1,
    #             comment=str(ins)))
    # elif is_int(ins.arg2):
    #     if is_gt_16_bit(ins.arg2):
    #         # li Rd, Imm        Rd = Imm
    #         # add Rd, Rs, Rt    Rd = Rs + Rt
    #         asm.append(AsmInstruction('li', ins.dest, ins.arg2, comment=str(ins)))
    #         asm.append(AsmInstruction('add', ins.dest, ins.dest, ins.arg1))
    #     else:
    #         asm.append(AsmInstruction('addi', ins.dest, ins.arg1, ins.arg2,
    #             comment=str(ins)))
    # else:
    #     raise TypeError('%s not translated' % ins)
    # return asm


def asm_div(ins, aic):
    if ins.op != '/':
        raise TypeError('Instruction is not a division operation!')
    if is_int(ins.arg1) or is_int(ins.arg2):
        raise TypeError('Divide can only use registers!')
    # div Rd, Rs, Rt    Rd = Rs / Rt (integer div)
    return [AsmInstruction('div', ins.dest, ins.arg1, ins.arg2,
        comment=str(ins))]


def asm_mod(ins, aic):
    if ins.op != '%':
        raise TypeError('Instruction is not a modulus operation!')
    if is_int(ins.arg1) or is_int(ins.arg2):
        raise TypeError('Modulus can only use registers!')
    # rem Rd, Rs, Rt    Rd = Rs % Rt
    return [AsmInstruction('rem', ins.dest, ins.arg1, ins.arg2,
        comment=str(ins))]


def asm_sub(ins, aic):
    if ins.op != '-':
        raise TypeError('Instruction is not a subtraction operation!')
    if is_int(ins.arg1) or is_int(ins.arg2):
        raise TypeError('Subtraction can only use registers!')
    # sub Rd, Rs, Rt    Rd = Rs - Rt
    return [AsmInstruction('sub', ins.dest, ins.arg1, ins.arg2,
        comment=str(ins))]


def asm_mul(ins, aic):
    if ins.op != '*':
        raise TypeError('Instruction is not a multiplication operation!')
    if is_int(ins.arg1) or is_int(ins.arg2):
        raise TypeError('Multiplication can only use registers')
    # mul Rd, Rs, Rt    Rd = Rs * Rt
    return [AsmInstruction('mul', ins.dest, ins.arg1, ins.arg2,
        comment=str(ins))]


def asm_neg(ins, aic):
    if ins.op != '-':
        raise TypeError('Instruction is not a negation operation!')
    asm = []
    if is_int(ins.arg1):
        # li Rd, Imm    Rd = Imm
        # neg Rd, Rs    Rd = -(Rs)
        asm.append(AsmInstruction('li', ins.dest, ins.arg1, comment=str(ins)))
        asm.append(AsmInstruction('neg', ins.dest, ins.dest))
    else:
        # neg Rd, Rs    Rd = -(Rs)
        asm.append(AsmInstruction('neg', ins.dest, ins.arg1, comment=str(ins)))
    return asm


def asm_print(ins, aic):
    if ins.op != 'print':
        raise TypeError('Instruction is not a print operation!')
    # Sycall for print integer: $v0 = 1, $a0 = int
    asm = []
    if is_int(ins.arg1):
        # li Rd, Imm    Rd = Imm
        asm.append(AsmInstruction('li', '$a0', ins.arg1, comment=str(ins)))
    else:
        # move Rd, Rs   Rd = Rs
        asm.append(AsmInstruction('move', '$a0', ins.arg1, comment=str(ins)))
    # li Rd, Imm    Rd = Imm
    # syscall
    asm.append(AsmInstruction('li', '$v0', 1))
    asm.append(AsmInstruction('syscall'))
    return asm


def asm_input(ins, aic):
    if ins.op != 'input':
        raise TypeError('Instruction is not an input operation!')
    # Syscall for read integer: $v0 = 5, $v0 = read int
    asm = []
    # li Rd, Imm    Rd = Imm
    # syscall
    # move Rd, Rs   Rd = Rs
    asm.append(AsmInstruction('li', '$v0', 5, comment=str(ins)))
    asm.append(AsmInstruction('syscall'))
    asm.append(AsmInstruction('move', ins.dest, '$v0'))
    return asm


def asm_store(ins, aic):
    if ins.op != 'store':
        raise TypeError('Instruction is not a store operations!')
    aic.data.append(ins.dest)
    # sw Rt, Address(Rs)    Word at M[Address + Rs] = Rt
    return [AsmInstruction('sw', ins.arg1, ins.dest)]


def asm_load(ins, aic):
    if ins.op != 'load':
        raise TypeError('Instruction is not a load operation!')
    # lw Rt, Address(Rs)    Rt = Word at M[Address + Rs]
    return [AsmInstruction('lw', ins.dest, ins.arg1)]


class AsmInstructionContext(object):
    def __init__(self):
        self.instructions = []
        self.data = []

    def add_threeaddress(self, ins):
        binary_ops = {
            '+': asm_add, '-': asm_sub,
            '*': asm_mul, '/': asm_div, '%': asm_mod
        }
        unary_ops = {
            '-': asm_neg
        }
        other_ops = {
            'input': asm_input,
            'print': asm_print,
            'store': asm_store,
            'load': asm_load
        }
        if ins.is_binary_op():
            asm = binary_ops[ins.op](ins, self)
        elif ins.is_unary_op():
            asm = unary_ops[ins.op](ins, self)
        elif ins.is_assignment():
            asm = asm_assign(ins, self)
        else:
            asm = other_ops[ins.op](ins, self)
        self.instructions = self.instructions + asm

    def write_to_file(self, program_name):
        """Write out program to a file called
        program_name.asm

        Arguments:
        program_name - name of program

        """
        out = open('%s.asm' % program_name, 'w')
        out.write('.data\n')
        for x in self.data:
            out.write('%s:    .word 0\n' % x)
        out.write('.text\n')
        out.write('main:\n')
        for x in self.instructions:
            out.write('%s\n' % x)
        # Exit gracefully
        out.write('# Exit gracefully\nli $v0, 10\nsyscall\n')
