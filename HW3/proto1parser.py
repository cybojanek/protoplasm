import ply.yacc as yacc

# Get tokens from lexer
from proto1lexer import tokens
from AbstractSyntaxTree import *

# Precedence ordering lowest to highest
# Associativity: left / right
precedence = (
    ('left', 'AND'),
    ('left', 'OR'),
    ('nonassoc', 'EQUALEQUAL', 'NOTEQUAL', 'LESSTHAN', 'LESSTHANEQUAL',
        'GREATERTHAN', 'GREATERTHANEQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULUS'),
    ('right', 'UNOT'),
    ('right', 'UMINUS')
)
start = 'pgm'

defined = set()


def p_pgm(p):
    '''pgm : stmtseq'''
    p[0] = p[1]


def p_stmtseq(p):
    '''stmtseq : stmt stmtseq
               | stmt'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_stmt(p):
    '''stmt : assign
            | print
            | block
            | if
            | while'''
    p[0] = ASTStatement(p, p[1])


def p_assign(p):
    '''assign : ID EQUALS rhs SEMICOLON'''
    p[0] = ASTAssign(p, p[1], p[3])
    defined.add(p[1])


def p_print(p):
    '''print : PRINT LPAREN ae RPAREN SEMICOLON'''
    p[0] = ASTPrint(p, p[3])


def p_block(p):
    '''block : LBRACKET stmtseq RBRACKET'''
    p[0] = ASTBlock(p, p[2])


def p_if_then_else(p):
    '''if : IF ae THEN stmt ELSE stmt'''
    p[0] = ASTIf(p, p[2], p[4], else_part=p[6])


def p_if_then(p):
    '''if : IF ae THEN stmt'''
    p[0] = ASTIf(p, p[2], p[4])


def p_while(p):
    '''while : WHILE ae DO stmt'''
    p[0] = ASTWhile(p, p[2], p[4])


def p_rhs(p):
    '''rhs : INPUT LPAREN RPAREN'''
    p[0] = ASTInput(p)


def p_rhs_ae(p):
    '''rhs : ae'''
    p[0] = p[1]


def p_ae_bin(p):
    '''ae : ae PLUS ae
          | ae MINUS ae
          | ae TIMES ae
          | ae DIVIDE ae
          | ae MODULUS ae
          | ae AND ae
          | ae OR ae
          | ae EQUALEQUAL ae
          | ae NOTEQUAL ae
          | ae LESSTHAN ae
          | ae LESSTHANEQUAL ae
          | ae GREATERTHAN ae
          | ae GREATERTHANEQUAL ae'''
    p[0] = ASTBinaryOp(p, p[1], p[3], p[2])


def p_ae_un_minus(p):
    '''ae : MINUS ae %prec UMINUS'''
    if isinstance(p[2], ASTInteger):
        p[0] = ASTInteger(p, - p[2].value)
    # Otherwise we need to do a unary operation on it
    else:
        p[0] = ASTUnaryOp(p, p[2], p[1])


def p_ae_un_not(p):
    '''ae : NOT ae %prec UNOT'''
    p[0] = ASTUnaryOp(p, p[2], p[1])


def p_ae_paren(p):
    '''ae : LPAREN ae RPAREN'''
    p[0] = p[2]


def p_ae_intconst(p):
    '''ae : NUMBER'''
    if not isinstance(p[1], int):
        raise TypeError('%r is not an integer' % p[1])
    p[0] = ASTInteger(p, p[1])


def p_f_id(p):
    '''ae : ID'''
    # Simple checking only, because this does not follow all paths
    if not p[1] in defined:
        raise NameError('%r is not defined at line: ??' % p[1])
    p[0] = ASTVariable(p, p[1])


# Syntax errors
def p_error(p):
    raise ValueError("Synax error!: %r" % p)
