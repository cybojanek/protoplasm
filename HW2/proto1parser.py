import ply.yacc as yacc

# Get tokens from lexer
from proto1lexer import tokens
from AbstractSyntaxTree import *

# Precedence ordering lowest to highest
# Associativity: left / right
precedence = (
    ('right', 'PLUS', 'MINUS'),
    ('right', 'TIMES', 'DIVIDE', 'MODULUS'),
    ('right', 'UMINUS')
)
start = 'pgm'

defined = set()

def p_pgm(p):
    '''pgm : stmt pgm
           | stmt'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_stmt(p):
    '''stmt : assign
            | print'''
    p[0] = ASTStatement(p, p[1])


def p_assign(p):
    '''assign : ID EQUALS rhs SEMICOLON'''
    p[0] = ASTAssign(p, p[1], p[3])
    defined.add(p[1])


def p_print(p):
    '''print : PRINT LPAREN ae RPAREN SEMICOLON'''
    p[0] = ASTPrint(p, p[3])


def p_rhs(p):
    '''rhs : INPUT LPAREN RPAREN'''
    p[0] = ASTInput(p)


def p_rhs_ae(p):
    '''rhs : ae'''
    p[0] = p[1]


def p_ae(p):
    '''ae : t PLUS ae
          | t MINUS ae'''
    p[0] = ASTBinaryOp(p, p[1], p[3], p[2])


def p_ae_t(p):
    '''ae : t'''
    p[0] = p[1]


def p_t(p):
    '''t : f TIMES t
         | f DIVIDE t
         | f MODULUS t'''
    p[0] = ASTBinaryOp(p, p[1], p[3], p[2])


def p_t_f(p):
    '''t : f'''
    p[0] = p[1]


def p_f_paren(p):
    '''f : LPAREN ae RPAREN'''
    #p[0] = ASTParen(p, p[2])
    p[0] = p[2]


def p_f_uminus(p):
    '''f : MINUS f %prec UMINUS'''
    p[0] = ASTUnaryOp(p, p[2], p[1])


def p_f_number(p):
    '''f : NUMBER'''
    if not isinstance(p[1], int):
        raise TypeError('%r is not an integer' % p[1])
    # We can't check here: bc - is one greater, and negation is done above
    # with unrary operator...
    # if not(-(2 ** 31) <= p[1] <= (2 ** 31 - 1)):
        # raise TypeError('%r is out of bounds for 32 bit signed integer' % p[1])
    p[0] = ASTInteger(p, p[1])


def p_f_id(p):
    '''f : ID'''
    if not p[1] in defined:
        raise NameError('%r is not defined at line: ??' % p[1])
    p[0] = ASTVariable(p, p[1])


# Syntax errors
def p_error(p):
    raise ValueError("Synax error!: %r" % p)
