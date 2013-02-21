import ply.yacc as yacc

# Get tokens from lexer
from proto1lexer import tokens

# Precedence ordering lowest to highest
# Associativity: left / right
precedence = (
    ('right', 'PLUS', 'MINUS'),
    ('right', 'TIMES', 'DIVIDE', 'MODULUS'),
    ('right', 'UMINUS')
)


def p_pgm(p):
    '''pgm : stmt pgm
           | stmt'''
    print 'pgm: %s' % list(p)


def p_stmt(p):
    '''stmt : assign
            | print'''
    print 'stmt: %s' % list(p)


def p_assign(p):
    'assign : ID EQUALS rhs SEMICOLON'
    print 'assign: %s' % list(p)


def p_print(p):
    'print : PRINT LPAREN ae RPAREN'
    print 'print: %s' % list(p)


def p_rhs(p):
    '''rhs : INPUT LPAREN RPAREN
           | ae'''
    print 'rhs: %s' % list(p)


def p_ae(p):
    '''ae : t PLUS ae
          | t MINUS ae
          | t'''
    print 'ae: %s' % list(p)


def p_t(p):
    '''t : f TIMES t
         | f DIVIDE t
         | f MODULUS t
         | f'''
    print 't: %s' % list(p)


def p_f(p):
    '''f : MINUS f %prec UMINUS
         | LPAREN ae RPAREN
         | NUMBER
         | ID'''
    print 'f: %s' % list(p)


# Syntax errors
def p_error(p):
    print "Synax error!: %r" % p
