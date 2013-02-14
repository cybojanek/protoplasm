"""
TODO
Read program and convert to statements
Tokenize with python's tokenize
Abstract classes for intermediate code representation
Liveliness
MIPS

* Static semantics - valid grammar and all variables defined
* Dynamic semantics - how ops are run
"""

import os
import sys
import tokenize


def proto_tokenize(file_name=None, lines=None):
    """Use python's tokenizer to tokenize a chunk of proto code.
    Uses file_name if not None, otherwise lines

    Keyword Arguments:
    file_name - name of proto file
    lines - array of new line termianted strings

    """
    tokens = []
    if file_name is not None:
        g = tokenize.generate_tokens(open(file_name, 'r').readline)
    elif lines is not None:
        it = iter(lines).next
        g = tokenize.generate_tokens(it)
    for toknum, tokval, start, end, line in g:
        # Don't add newlines: we're looking for ;
        if toknum in (tokenize.NL, tokenize.NEWLINE):
            continue
        tokens.append([toknum, tokval, start, end, line])
    for x in tokens:
        tokenize.printtoken(*x)
    return tokens


class ProtoSyntaxChecker(object):

    @staticmethod
    def RaiseError(exp, msg, x):
        """Raise a syntax checker exception

        Arguments:
        exp - exception type to raise
        msg - message to add
        x - tokenizer token for more info

        """
        toknum, tokval, start, end, line = x[0]
        raise exp('%s near line %s, column %s: %r' %
            (msg, start[0], start[1], line))

    SUM_OP = set(['+', '-'])
    PROD_OP = set(['*', '/', '%'])

    def __init__(self, tokens):
        """Create a syntax checker for a list of tokens.
        Implements CFG from Homework 2

        Arguments:
        tokens - list of tuples (toknum, tokval, start, end, line)

        """
        self.tokens = tokens
        self.def_vars = set()

    def check(self):
        """Start parser and check for syntax errors.
        Raise SyntaxError on bad syntax.

        """
        self.parse_PRGM(self.tokens)

    def parse_PRGM(self, x):
        """
        Pgm -> Stmt Pgm
            | Stmt
        """
        rest = self.parse_STMT(x)
        if not rest:
            return True
        else:
            return self.parse_PRGM(rest)

    def parse_STMT(self, x):
        """
        Stmt -> Assign
             | Print
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        # Peek at print
        if toknum == tokenize.NAME and tokval == 'print':
            return self.parse_PRINT(x)
        # Peek at variable
        elif toknum == tokenize.NAME:
            return self.parse_ASSIGN(x)
        # Peek at end of tokens
        elif toknum == tokenize.ENDMARKER:
            return []
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Incorrent STMT!', x)

    def parse_PRINT(self, x):
        """
        Print -> 'print' '(' AE ')' ';'
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME and tokval == 'print':
            return self.consume_SEMICOLON(self.consume_RPAREN(self.parse_AE(
                self.consume_LPAREN(tail))))
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Expected PRINT', x)

    def parse_ASSIGN(self, x):
        """
        Assign -> var '=' Rhs ';'
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME:
            # Add LHS variable
            rest = self.consume_SEMICOLON(self.parse_RHS(
                self.consume_EQUAL(tail)))
            self.def_vars.add(tokval)
            return rest
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Expected NAME', x)

    def parse_RHS(self, x):
        """
        Rhs -> 'input' '(' ')'
            | AE
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.NAME and tokval == 'input':
            return self.consume_RPAREN(self.consume_LPAREN(tail))
        else:
            return self.parse_AE(x)

    def parse_AE(self, x):
        """
        AE -> T SumOp AE
           | T
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        rest = self.parse_T(x)
        if rest and rest[0][1] in ProtoSyntaxChecker.SUM_OP:
            return self.parse_AE(rest[1:])
        else:
            return rest

    def parse_T(self, x):
        """
        T -> F ProdOp T
          | F
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        rest = self.parse_F(x)
        if rest and rest[0][1] in ProtoSyntaxChecker.PROD_OP:
            return self.parse_T(rest[1:])
        else:
            return rest

    def parse_F(self, x):
        """
        F -> '-' F
          | '(' AE ')'
          | intconst
          | var
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if toknum == tokenize.MINUS:
            return self.parse_F(tail)
        elif toknum == tokenize.OP and tokval == '(':
            return self.consume_RPAREN(self.parse_AE(tail))
        elif toknum == tokenize.NAME:
            # Check RHS variable
            if tokval not in self.def_vars:
                ProtoSyntaxChecker.RaiseError(
                    NameError, 'Undefined variable: %s' % tokval, x)
            return tail
        elif toknum == tokenize.NUMBER and tokval.isdigit():
            return tail
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Bad statement!', x)

    def consume_LPAREN(self, x):
        """Consume a LPAREN from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == '(':
            return tail
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Missing LPAREN', x)

    def consume_RPAREN(self, x):
        """Consume a RPAREN from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == ')':
            return tail
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Missing RPAREN', x)

    def consume_EQUAL(self, x):
        """Consume an EQUAL from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == '=':
            return tail
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError, 'Missing EQUAL sign', x)

    def consume_SEMICOLON(self, x):
        """Consume a SEMICOLON from head and return tail
        """
        head, tail = x[0], x[1:]
        toknum, tokval, _, _, _ = head
        if x and toknum == tokenize.OP and tokval == ';':
            return tail
        else:
            ProtoSyntaxChecker.RaiseError(SyntaxError,
                'Missing SEMICOLON sign', x)


def main(file_name):
    statement_tokens = proto_tokenize(file_name)
    psc = ProtoSyntaxChecker(statement_tokens)
    psc.check()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: %s FILE" % (sys.argv[0])
        sys.exit(1)
    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print "%s does not exist" % (file_name)
        sys.exit(1)
    main(file_name)
    sys.exit(0)
