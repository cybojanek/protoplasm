class PBF:
    def __init__(self):
        raise NotImplementedError("PBF class not callable")

    def isNNF(self):
        raise NotImplementedError("isNNF not implemented")

    def toNNF(self):
        raise NotImplementedError("toNNF not implemented")


class OR(PBF):
    def __init__(self, f1, f2):
        if not isinstance(f1, PBF) or not isinstance(f2, PBF):
            raise TypeError("OR can only hold PBF types")
        self.lchild = f1
        self.rchild = f2

    def isNNF(self):
        return self.lchild.isNNF() and self.rchild.isNNF()

    def toNNF(self):
        return OR(self.lchild.toNNF(), self.rchild.toNNF())

    def __str__(self):
        return "%s %s |" % (self.lchild, self.rchild)


class AND(PBF):
    def __init__(self, f1, f2):
        if not isinstance(f1, PBF) or not isinstance(f2, PBF):
            raise TypeError("AND can only hold PBF types")
        self.lchild = f1
        self.rchild = f2

    def isNNF(self):
        return self.lchild.isNNF() and self.rchild.isNNF()

    def toNNF(self):
        return AND(self.lchild.toNNF(), self.rchild.toNNF())

    def __str__(self):
        return "%s %s &" % (self.lchild, self.rchild)


class NOT(PBF):
    def __init__(self, f):
        if not isinstance(f, PBF):
            raise TypeError("NOT can only hold PBF types")
        self.child = f

    def isNNF(self):
        return isinstance(self.child, PROP)

    def toNNF(self):
        if self.isNNF():
            return NOT(self.child.toNNF())
        elif isinstance(self.child, NOT):
            return self.child.child.toNNF()
        else:
            lchild = self.child.lchild.toNNF()
            lchild = lchild.child if isinstance(lchild, NOT) else NOT(lchild)
            rchild = self.child.rchild.toNNF()
            rchild = rchild.child if isinstance(rchild, NOT) else NOT(rchild)
            if isinstance(self.child, AND):
                return OR(lchild, rchild)
            elif isinstance(self.child, OR):
                return AND(lchild, rchild)

    def __str__(self):
        return "%s !" % (self.child)


class PROP(PBF):
    def __init__(self, p):
        if isinstance(p, PBF):
            raise TypeError("PROP cannot be a PBF")
        self.prop = p

    def isNNF(self):
        return True

    def toNNF(self):
        return PROP(self.prop)

    def __str__(self):
        return str(self.prop)
