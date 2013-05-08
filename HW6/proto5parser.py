import ply.yacc as yacc

# Get tokens from lexer
from proto5lexer import tokens, colorize, find_column
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


def p_pgm(p):
    '''pgm : pgm_seq'''
    p[0] = ASTProgram(p, p[1])

def p_pgm_decl(p):
    '''pgm_seq : decl pgm_seq'''
    p[0] = [p[1]] + p[2]


def p_pgm_empty(p):
    '''pgm_seq : empty'''
    p[0] = []


def p_decl_vardecl(p):
    '''decl : vardecl'''
    p[0] = p[1]


def p_decl_fundecl(p):
    '''decl : fundecl'''
    p[0] = p[1]


def p_decl_classdecl(p):
    '''decl : classdecl'''
    p[0] = p[1]

def p_dimstar_d(p):
    '''dimstar : LBRACE RBRACE dimstar
               | empty'''
    if len(p) == 4:  # Count how many dimensions
        p[0] = 1 + (p[3] if p[3] else 0);

def p_var(p):
    '''var : ID dimstar'''
    p[0] = (p[1], (p[2] if p[2] else 0))


def p_vardecl(p):
    '''vardecl : type varlist SEMICOLON'''
    p[0] = ASTDeclareList(p, p[1][0], 
        [ASTDeclareVariable(v, v[0], (p[1][0], v[1])) for v in p[2]] )

def p_vardecl_star(p):
    '''vardecl_star : vardecl vardecl_star
                    | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_fundecl(p):
    '''fundecl : type dimstar ID LPAREN formals_question RPAREN stmt
               | type ID LPAREN formals_question RPAREN stmt'''
    if len(p) == 7:
        p[0] = ASTFunctionDeclare(p, p[1], p[2], p[4], p[6])
    elif len(p) == 8:
        p[0] = ASTFunctionDeclare(p, (p[1][0], (p[2] if p[2] else 0)), p[3], p[5], p[7])

def p_classdecl(p):
    '''classdecl : CLASS CLASSID EXTENDS CLASSID LCURLY vardecl_star  RCURLY
                 | CLASS CLASSID LCURLY vardecl_star  RCURLY'''
    if len(p) == 6:            
        p[0] = ASTDeclareClass(p, p[2], p[4])
    elif len(p) == 8:
        p[0] = ASTDeclareClass(p, p[2], p[6], p[4])

def p_type(p):
    '''type : INT
            | BOOL
            | VOID
            | CLASSID'''
    p[0] = (p[1], 0)

def p_varlist(p):
    '''varlist : var COMMA varlist
               | var'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_formals(p):
    '''formals : type var COMMA formals
               | type var'''
    if len(p) == 5:
        p[0] = [ASTDeclareVariable(p, p[2][0], (p[1][0], p[2][1]))] + p[4]
    else:
        p[0] = [ASTDeclareVariable(p, p[2][0], (p[1][0], p[2][1]))] 

def p_formals_question(p):
    '''formals_question : formals'''
    p[0] = p[1]


def p_formals_question_empty(p):
    '''formals_question : empty'''
    p[0] = []


def p_stmt(p):
    '''stmt : se SEMICOLON'''
    p[0] = ASTStatement(p, p[1])


def p_stmt_print(p):
    '''stmt : PRINT LPAREN ae RPAREN SEMICOLON'''
    p[0] = ASTStatement(p, ASTPrint(p, p[3]))


def p_stmt_block(p):
    '''stmt : LCURLY vardecl_star stmt_star RCURLY'''
    p[0] = ASTStatement(p, ASTBlock(p, p[2], p[3] + [ASTEndBlock(p)]))


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
    '''stmt : FOR LPAREN se_question SEMICOLON ae_question SEMICOLON se_question RPAREN stmt'''
    p[0] = ASTFor(p, p[3], p[5], p[7], p[9])


def p_stmt_do_while(p):
    '''stmt : DO stmt WHILE ae SEMICOLON'''
    p[0] = ASTStatement(p, ASTDoWhile(p, p[2], p[4]))


def p_stmt_return(p):
    '''stmt : RETURN ae_question SEMICOLON'''
    p[0] = ASTFunctionReturn(p, p[2])


def p_stmt_star(p):
    '''stmt_star : stmt stmt_star
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


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


def p_se_question(p):
    '''se_question : se'''
    p[0] = p[1]


def p_se_question_empty(p):
    '''se_question : empty'''
    p[0] = ASTNoOp(p)


def p_lhs_field(p):
    '''lhs : fieldaccess'''
    p[0] = p[1]


def p_lhs_array(p):
    '''lhs : arrayaccess'''
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


def p_ae_primary(p):
    '''ae : primary'''
    p[0] = p[1]


def p_ae_se(p):
    '''ae : se'''
    p[0] = p[1]


def p_ae_newarray(p):
    '''ae : newarray'''
    p[0] = p[1]


def p_ae_question(p):
    '''ae_question : ae'''
    p[0] = p[1]


def p_ae_question_empty(p):
    '''ae_question : empty'''
    p[0] = ASTNoOp(p)


def p_primary_int(p):
    '''primary : NUMBER'''
    if not isinstance(p[1], int):
        raise TypeError('%r is not an integer' % p[1])
    p[0] = ASTInteger(p, p[1])


def p_primary_true(p):
    '''primary : TRUE'''
    p[0] = ASTBoolean(p, True)


def p_primary_false(p):
    '''primary : FALSE'''
    p[0] = ASTBoolean(p, False)


def p_primary_input(p):
    '''primary : INPUT LPAREN RPAREN'''
    p[0] = ASTInput(p)


def p_primary_ae(p):
    '''primary : LPAREN ae RPAREN'''
    p[0] = p[2]


def p_primary_field(p):
    '''primary : fieldaccess'''
    p[0] = p[1]


def p_primary_array(p):
    '''primary : arrayaccess'''
    p[0] = p[1]


def p_primary_function(p):
    '''primary : functioncall'''
    p[0] = p[1]


def p_primary_object(p):
    '''primary : newobject'''
    p[0] = p[1]


def p_array_acccess(p):
    '''arrayaccess : primary LBRACE ae RBRACE'''
    p[0] = ASTArray(p, p[1], p[3])


def p_field_acccess(p):
    '''fieldaccess : primary DOT ID'''
    p[0] = ASTFieldAccess(p, p[1], p[3])


def p_field_access_id(p):
    '''fieldaccess : ID'''
    p[0] = ASTVariable(p, p[1])


def p_function_call(p):
    '''functioncall : ID LPAREN args_question RPAREN'''
    p[0] = ASTFunctionCall(p, p[1], p[3])


def p_args(p):
    '''args : ae COMMA args
            | ae'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_args_question(p):
    '''args_question : args'''
    p[0] = p[1]


def p_args_question_empty(p):
    '''args_question : empty'''
    p[0] = []


def p_new_object(p):
    '''newobject : NEW CLASSID LPAREN RPAREN'''
    p[0] = ASTAllocObject(p, p[2])


def p_new_array(p):
    '''newarray : NEW type dimexpr dim_star'''
    p[0] = ASTAlloc(p, p[2], p[3], p[4] + 1)


def p_dimexpr(p):
    '''dimexpr : LBRACE ae RBRACE'''
    p[0] = p[2]


def p_dim(p):
    '''dim : LBRACE RBRACE'''
    p[0] = None


def p_dim_star(p):
    '''dim_star : dim dim_star'''
    p[0] = 1 + p[2]


def p_dim_star_empty(p):
    '''dim_star : empty'''
    p[0] = 0


# Empty productions
def p_empty(p):
    '''empty :'''
    pass

#########################################
#  _____ ____  ____   ___  ____  ____   #
# | ____|  _ \|  _ \ / _ \|  _ \/ ___|  #
# |  _| | |_) | |_) | | | | |_) \___ \  #
# | |___|  _ <|  _ <| |_| |  _ < ___) | #
# |_____|_| \_\_| \_\\___/|_| \_\____/  #
#########################################




    # pass
# def p_error(p):
#     print "MEOW"
    # print p.__dict__
    # p.parser.errok()


# def p_stmt_error(p):
#     '''stmt : se error'''
#     p.parser.proto_errors += 1
#     print p.parser.__dict__
#     # print p.slice[1][1]
#     # print_expected_error(p, 1, "expected ';' after statement", ';')
#     p.parser.errok()
# def p_stmt_if_then_error(p):
#     '''stmt : IF ae error stmt'''
#     print_expected_error(p, 1, "expected 'then' in 'if' statement")


def p_type_rbrace_error(p):
    ''' type : type LBRACE error'''
    print_expected_error(p, 2, "expected ']' after '['", ']')


def p_type_lbrace_error(p):
    ''' type : type error RBRACE'''
    print_expected_error(p, 3, "expected '[' before ']'", '[', aug=2)


def p_varlist_error(p):
    '''varlist : var COMMA error'''
    print_expected_error(p, 2, "expected variable after ','")


def p_stmt_print_semi_error(p):
    '''stmt : PRINT LPAREN ae RPAREN error'''
    print_expected_error(p, 4, "expected ';' after print statement", ';')


def p_stmt_print_lparen_error(p):
    '''stmt : PRINT error ae RPAREN SEMICOLON'''
    print_expected_error(p, 1, "expected '(' after print", '(', aug=-3)


def p_stmt_print_lrparen_error(p):
    '''stmt : PRINT error ae error SEMICOLON'''
    print_expected_error(p, 1, "expected '(' after print", '(', aug=-3)
    print_expected_error(p, 5, "expected ')' before ';'", ')', aug=2)


def p_primary_ae_rparen_error(p):
    '''primary : LPAREN ae error'''
    print_expected_error(p, 1, "unmatched '('", aug=2)


def p_function_call_rparen_error(p):
    '''functioncall : ID LPAREN args_question error'''
    print_expected_error(p, 2, "unmatched '('", aug=2)


def print_expected_error(p, t, message, missing=None, aug=1):
    p.parser.proto_errors += 1
    lineno, col = p.lineno(t), find_column(p.lexer.lexdata, p.slice[t])
    line = p.lexer.lexdata.split('\n')[lineno]
    print "%s %s %s" % (
        colorize('%s:%s:%s' % (p.lexer.proto_file, lineno, col), 'white'),
        colorize('error:', 'red'),
        colorize(message, 'white'))
    print line.rstrip()
    print '%s%s' % (' ' * (col - aug), colorize('^', 'green'))
    if missing:
        print '%s%s' % (' ' * (col - aug), colorize(missing, 'green'))
    p.parser.errok()

# Syntax errors
def p_error(p):
    p.lexer.proto_errors += 1
    print colorize(str(ValueError("Syntax error!: %r" % p)), 'blue')
    # print colorize("Somewhere here", 'blue')
    # print colorize("##")
    # print '\n'.join(p.lexer.lexdata.split('\n')[p.lineno - 1:p.lineno + 1])
    # p.parser.errok()
