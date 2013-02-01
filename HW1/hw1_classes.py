
class PBF:
    pass

class OR(PBF):
    
    def __init__(self, f1, f2):
        self.lchild = f1
        self.rchild = f2

    def __str__(self):
        return str(self.lchild) + " " + str(self.rchild) + " |"


class AND(PBF):

    def __init__(self, f1, f2):
        self.lchild = f1
        self.rchild = f2

    def __str__(self):
        return str(self.lchild) + " " + str(self.rchild) + " &"


class NOT(PBF):

    def __init__(self, f):
        self.child = f

    def __str__(self):
        return str(self.child) + " !"


class PROP(PBF):

    def __init__(self, p):
        self.prop = p

    def __str__(self):
        return self.prop


    
