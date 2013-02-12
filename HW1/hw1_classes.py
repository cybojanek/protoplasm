class PBF:
    """Propositional Boolean Formula superclass
    Expects subclasses to implement __init__, isNNF, and toNNF

    """
    def __init__(self):
        raise NotImplementedError("PBF class not callable")

    def isNNF(self):
        """Check for Negation Normal Form

        Return:
        True - in NNF form
        False - not in NNF form

        """
        raise NotImplementedError("isNNF not implemented")

    def toNNF(self):
        """Convert to Negation Normal Form

        Return:
        New PBF object in NNF form

        """
        raise NotImplementedError("toNNF not implemented")


class OR(PBF):
    def __init__(self, f1, f2):
        """Propositional Boolean Formula for OR

        Arguments:
        f1 - PBF object
        f2 - PBF object

        """
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
        """Propositional Boolean Formula for AND

        Arguments:
        f1 - PBF object
        f2 - PBF object

        """
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
        """Propositional Boolean Formula for NOT

        Arguments:
        f - PBF object

        """
        if not isinstance(f, PBF):
            raise TypeError("NOT can only hold PBF types")
        self.child = f

    def isNNF(self):
        return isinstance(self.child, PROP)

    def toNNF(self):
        # If we're in NNF, return new self
        if self.isNNF():
            return NOT(self.child.toNNF())
        # If we have a NOT as a child, return that child's NNF
        elif isinstance(self.child, NOT):
            return self.child.child.toNNF()
        # Otherwise, we are AND or OR and need to check children
        else:
            # Follow De Morgan's Law to return NNF
            # Convert child to NNF
            lchild = self.child.lchild.toNNF()
            rchild = self.child.rchild.toNNF()
            # Negate NOT
            lchild = lchild.child if isinstance(lchild, NOT) else NOT(lchild)
            rchild = rchild.child if isinstance(rchild, NOT) else NOT(rchild)
            # Flip AND and OR
            if isinstance(self.child, AND):
                return OR(lchild, rchild)
            elif isinstance(self.child, OR):
                return AND(lchild, rchild)

    def __str__(self):
        return "%s !" % (self.child)


class PROP(PBF):
    def __init__(self, p):
        """Propositional Boolean Formula for PROP

        Arguments:
        f1 - any value, except a PBF object

        """
        if isinstance(p, PBF):
            raise TypeError("PROP cannot be a PBF")
        self.prop = p

    def isNNF(self):
        return True

    def toNNF(self):
        return PROP(self.prop)

    def __str__(self):
        return str(self.prop)


import re


class ParseError(Exception):
    pass


class TokenError(Exception):
    pass


class PBFToken(object):
    """Token representation of a PBF object
    """
    # Token types
    PROP, NOT, OR, AND = "PROP", "NOT", "OR", "AND"
    # Static single char tokens
    STATIC_TOKENS = {
        '&': AND,
        '|': OR,
        '!': NOT
    }
    # Dynamic regex matching tokens
    DYNAMIC_TOKENS = [
        (r'^[a-zA-z]+$', PROP)
    ]

    def __init__(self, value):
        """Create a Token

        Arguments:
        value - simple value to tokenize

        """
        self.value = value
        self.type = PBFToken.tokenize(value)

    def __str__(self):
        return '%s: %r' % (self.type, self.value)

    def __repr__(self):
        return '<PBFToken> %s' % (str(self))

    @staticmethod
    def tokenize(value):
        """Return the Token type. Raise TokenError if not recognized

        Arguments:
        value - simple value to tokenize

        """
        if value in PBFToken.STATIC_TOKENS:
            return PBFToken.STATIC_TOKENS[value]
        for regex, token in PBFToken.DYNAMIC_TOKENS:
            if re.match(regex, value):
                return token
        raise TokenError('Uknown PBFToken type for: %r' % value)


def parse(formula):
    """Parse a postfix string into a PBF object. Raise ParseError on error

    Arguments:
    formila - string in postfix notation with whitespace between tokens

    """
    tokens = [PBFToken(x) for x in formula.split()]
    stack = list()
    try:
        while not len(tokens) == 0:
            token = tokens.pop(0)
            if token.type == PBFToken.PROP:
                stack.append(PROP(token.value))
            elif token.type == PBFToken.NOT:
                stack.append(NOT(stack.pop()))
            elif token.type == PBFToken.AND:
                stack.append(AND(stack.pop(-2), stack.pop()))
            elif token.type == PBFToken.OR:
                stack.append(OR(stack.pop(-2), stack.pop()))
    except IndexError:
        raise ParseError('Missing arguments to: %r' % (token.type))
    if len(stack) > 1:
        raise ParseError('Too many arguments!')
    return stack.pop()
