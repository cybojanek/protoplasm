from ParseTree import ParseTreeNode


class ASTNode(object):
    """ASTNode"""

    def __init__(self):
        raise NotImplemented()

    def wellformed(self):
        raise NotImplemented()

    def gencode(self):
        raise NotImplemented()


class ASTStatement(ASTNode):

    def __init__(self, p, value):
        self.p = p
        self.value = value

    def __str__(self):
        return 'STMT: %s' % self.value


class ASTAssign(ASTNode):

    def __init__(self, p, left, right):
        self.p = p
        self.left = left
        self.right = right

    def __str__(self):
        return 'ASSIGN: %s = %s' % (self.left, self.right)


class ASTVariable(ASTNode):

    def __init__(self, p, value):
        self.p = p
        self.value = value

    def __str__(self):
        return 'ID:%s' % self.value


class ASTPrint(ASTNode):

    def __init__(self, p, value):
        self.p = p
        self.value = value

    def __str__(self):
        return 'PRINT: %s' % self.value


class ASTInput(ASTNode):

    def __init__(self, p):
        self.p = p

    def __str__(self):
        return 'INPUT'


class ASTInteger(ASTNode):

    def __init__(self, p, value):
        self.p = p
        self.value = value

    def __str__(self):
        return 'INTEGER: %s' % self.value


class ASTUnaryOp(ASTNode):
    TYPES = '-'
    NEGATE = TYPES

    def __init__(self, p, value, type):
        self.p = p
        self.value = value
        self.type = type
        if self.type not in ASTUnaryOp.TYPES:
            raise TypeError('Unary operation: %r not supported')

    def __str__(self):
        return 'NEGATE: %s' % self.value


class ASTParen(ASTNode):

    def __init__(self, p, value):
        self.p = p
        self.value = value

    def __str__(self):
        return 'PAREN: %s' % self.value


class ASTBinaryOp(ASTNode):
    TYPES = '-', '+', '*', '/', '%'
    MINUS, PLUS, TIMES, DIVIDE, MODULUS = TYPES

    def __init__(self, p, left, right, type):
        self.p = p
        self.left, self.right = left, right
        self.type = type
        if self.type not in ASTBinaryOp.TYPES:
            raise TypeError('Binary operation: %r not supported')

    def __str__(self):
        return 'BINARY_OP %s: %s, %s' % (self.type, self.left, self.right)
