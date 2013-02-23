from IntermediateCode import *


class AsmInstruction(object):
    def __init__(self, op, arg1=None, arg2=None, arg3=None, comment=""):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.comment = comment

    def __str__(self):
        if self.arg1 and self.arg2 and self.arg3:
            return "%s %s, %s, %s\t# %s" % (self.op, self.arg1, self.arg2, self.arg3, self.comment)       
        elif self.arg1 and self.arg2: 
            return "%s %s, %s\t# %s" % (self.op, self.arg1, self.arg2, self.comment)       
        elif self.arg1: 
            return "%s %s\t#%s" % (self.op, self.arg1, self.comment)       
        else: return self.op+"\t\t# "+self.comment

class AsmInstructionContext(object):
    def __init__(self):
        self.instructions = []

    def add_threeaddress(self, ins):
       # self.instructions.append(AsmInstruction("#", str(ins)))
        if ins.op:
            ops = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "div"}

            if ins.op in ops:
                if(str(ins.arg1).isdigit()):
                     self.instructions.append(AsmInstruction("li", ins.dest, ins.arg1,comment=str(ins)))  
                     self.instructions.append(AsmInstruction(ops[ins.op], ins.dest, ins.dest, ins.arg2))
                elif(str(ins.arg2).isdigit()):
                     self.instructions.append(AsmInstruction("li", ins.dest, ins.arg2,comment=str(ins)))  
                     self.instructions.append(AsmInstruction(ops[ins.op], ins.dest, ins.dest, ins.arg1))
                else:
                     self.instructions.append(AsmInstruction(ops[ins.op], ins.dest, ins.arg1, ins.arg2,comment=str(ins)))

            # For modulus, use divison and mfhi
            if ins.op == "%":
                self.instructions.append(AsmInstruction("mfhi", ins.dest))

            if ins.op=="print":
                self.instructions.append(AsmInstruction("li", "$v0", "1",comment=str(ins)))  
                if(str(ins.arg1).isdigit()):
                     self.instructions.append(AsmInstruction("li", "$a1", ins.arg1))
                else: 
                     self.instructions.append(AsmInstruction("add", "$a1", ins.arg1, "$0"))
                self.instructions.append(AsmInstruction("syscall"))

            if ins.op=="input":
                self.instructions.append(AsmInstruction("li", "$v0", "5",comment=str(ins)))  
                self.instructions.append(AsmInstruction("syscall"))
                self.instructions.append(AsmInstruction("add", ins.dest, "$a0", "$0"))

        else:
            if(str(ins.arg1).isdigit()):
                 self.instructions.append(AsmInstruction("li", ins.dest, ins.arg1, comment=str(ins)))
            else: # use li for an immiedate, or xor with $0 for a register
                 self.instructions.append(AsmInstruction("add", ins.dest, ins.arg1, "$0", comment=str(ins)))

