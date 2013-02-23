from IntermediateCode import *


class AsmInstruction(object):
    def __init__(self, op, arg1=None, arg2=None, arg3=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __str__(self):
        if self.arg1 and self.arg2 and self.arg3:
            return "%s %s %s %s" % (self.op, self.arg1, self.arg2, self.arg3)       
        elif self.arg1 and self.arg2: 
            return "%s %s %s" % (self.op, self.arg1, self.arg2)       
        elif self.arg1: 
            return "%s %s" % (self.op, self.arg1)       
        else: return self.op

class AsmInstructionContext(object):
    def __init__(self):
        self.instructions = []

    def add_threeaddress(self, ins):
        self.instructions.append(AsmInstruction("#", str(ins)))
        if ins.op:
           # if ins.op=="+":
               # if(str(ins.arg1).isdigit()) and if(str(ins.arg2).isdigit()):
                   #  self.instructions.append(AsmInstruction("li", ins.dest, ins.arg1))

            if ins.op=="print":
                self.instructions.append(AsmInstruction("li", "$v0", "1"))  
                if(str(ins.arg1).isdigit()):
                     self.instructions.append(AsmInstruction("li", "$t1", ins.arg1))
                else: # use li for an immiedate, or xor with $0 for a register
                     self.instructions.append(AsmInstruction("xor", "$t1", "$0", ins.arg1))
                self.instructions.append(AsmInstruction("syscall"))

