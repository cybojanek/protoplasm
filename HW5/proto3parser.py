import ply.yacc as yacc

# Get tokens from lexer
from proto3lexer import tokens
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
    '''pgm : declseq stmtseq'''
    p[0] = ASTProgram(p[1], p[2])


def p_stmtseq(p):
    '''stmtseq : stmt stmtseq
               | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_stmt(p):
    '''stmt : se SEMICOLON'''
    p[0] = ASTStatement(p, p[1])


def p_stmt_print(p):
    '''stmt : PRINT LPAREN ae RPAREN SEMICOLON'''
    p[0] = ASTStatement(p, ASTPrint(p, p[3]))


def p_stmt_block(p):
    '''stmt : LCURLY declseq stmtseq RCURLY'''
    p[0] = ASTStatement(p, ASTBlock(p, p[2], p[3]))


def p_stmt_if_then_else(p):
    '''stmt : IF ae THEN stmt ELSE stmt'''
    p[0] = ASTStatement(p, ASTIf(p, p[2], p[4], p[6]))


def p_stmt_if_then(p):
    '''stmt : IF ae THEN stmt'''
    p[0] = ASTStatement(p, ASTIf(p, p[2], p[4]))


def p_stmt_while_do(p):
    '''stmt : WHILE ae DO stmt'''
    p[0] = ASTStatement(p, ASTWhileDo(p, p[2], p[4]))


def p_stmt_for(p):
    ''' stmt : FOR LPAREN seopt SEMICOLON aeopt SEMICOLON seopt RPAREN stmt'''
    p[0] = ASTFor(p, p[3], p[5], p[7], p[9])


def p_stmt_do_while(p):
    '''stmt : DO stmt WHILE ae SEMICOLON'''
    p[0] = ASTStatement(p, ASTDoWhile(p, p[2], p[4]))


def p_seopt_se(p):
    '''seopt : se'''
    p[0] = p[1]


def p_seopt_e(p):
    '''seopt : empty'''
    pass


def p_aeopt_ae(p):
    '''aeopt : ae'''
    p[0] = p[1]


def p_aeopt_e(p):
    '''aeopt : empty'''
    pass


def p_declseq_d(p):
    '''declseq : decl declseq
               | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_decl(p):
    '''decl : type varlist SEMICOLON'''
    p[0] = ASTDeclareList(p, p[1], p[2])


def p_type(p):
    '''type : INT
            | BOOL'''
    # Not needed for homework 4
    p[0] = p[1]


def p_varlist(p):
    '''varlist : var COMMA varlist
               | var'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_var(p):
    '''var : ID dimstar'''
    # For now ignore brackets in dimstar
    p[0] = ASTDeclareVariable(p, p[1], (p[2] if p[2] else 0))


def p_se_assign(p):
    '''se : lhs EQUALS ae'''
    p[0] = ASTAssign(p, p[1], p[3])


def p_se_increment(p):
    '''se : lhs PLUSPLUS
          | lhs MINUSMINUS
          | PLUSPLUS lhs
          | MINUSMINUS lhs'''
    if p[2] in ("++", "--"):
        p[0] = ASTPrePostIncrement(p, p[1], p[2], 1);
    elif p[1] in ("++", "--"):
        p[0] = ASTPrePostIncrement(p, p[2], p[1], 0);

def p_lhs(p):
    '''lhs : ID
           | lhs LBRACE ae RBRACE'''
    if len(p) == 2:
        p[0] = ASTVariable(p, p[1])
    elif len(p) == 5:
        p[0] = ASTArray(p, p[1], p[3])
    else:
        raise NotImplementedError("Fix it")



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


def p_ae_lhs(p):
    '''ae : lhs
          | se'''
    p[0] = p[1]


def p_ae_paren(p):
    '''ae : LPAREN ae RPAREN'''
    p[0] = p[2]


def p_ae_input(p):
    '''ae : INPUT LPAREN RPAREN'''
    p[0] = ASTInput(p)


def p_ae_intconst(p):
    '''ae : NUMBER'''
    if not isinstance(p[1], int):
        raise TypeError('%r is not an integer' % p[1])
    p[0] = ASTInteger(p, p[1])


def p_ae_true(p):
    '''ae : TRUE'''
    p[0] = ASTBoolean(p, True)


def p_ae_false(p):
    '''ae : FALSE'''
    p[0] = ASTBoolean(p, False)


def p_ae_array(p):
    '''ae : NEW type dimexpr dimstar'''
    p[0] = ASTAlloc(p, p[3]);


def p_dimexpr(p):
    '''dimexpr : LBRACE ae RBRACE'''
    p[0] = p[2];


def p_dimstar_d(p):
    '''dimstar : LBRACE RBRACE dimstar
               | empty'''
    if len(p) == 4:  # Count how many dimensions
        p[0] = 1 + (p[3] if p[3] else 0);
    pass


# def p_f_id(p):
#     '''ae : ID'''
#     # Simple checking only, because this does not follow all paths
#     if not p[1] in defined:
#         raise NameError('%r is not defined at line: ??' % p[1])
#     p[0] = ASTVariable(p, p[1])


# Empty productions
def p_empty(p):
    '''empty :'''
    pass


# Syntax errors
def p_error(p):
    raise ValueError("Synax error!: %r" % p)
