import ply.lex as lex

# Reserved words
reserved = {
    'input': 'INPUT',
    'print': 'PRINT',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'new': 'NEW',
    'int': 'INT',
    'bool': 'BOOL',
    'true': 'TRUE',
    'false': 'FALSE'
}

# List of token names
tokens = ['EQUALS', 'PLUSPLUS', 'PLUS', 'MINUSMINUS', 'MINUS',
          'TIMES', 'DIVIDE', 'MODULUS',
          'AND', 'OR', 'EQUALEQUAL', 'NOTEQUAL', 'NOT',
          'LESSTHAN', 'LESSTHANEQUAL', 'GREATERTHAN', 'GREATERTHANEQUAL',
          'LPAREN', 'RPAREN', 'LCURLY', 'RCURLY', 'SEMICOLON',
          'LBRACE', 'RBRACE', 'COMMA',
          'ID', 'NUMBER'] + list(reserved.values())

# Tokens without actions
t_EQUALS = r'='
t_PLUSPLUS = r'\+\+'
t_PLUS = r'\+'
t_MINUSMINUS = r'--'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULUS = r'%'
t_AND = r'&&'
t_OR = r'\|\|'
t_EQUALEQUAL = r'=='
t_NOTEQUAL = r'!='
t_NOT = r'!'
t_LESSTHAN = r'<'
t_LESSTHANEQUAL = r'<='
t_GREATERTHAN = r'>'
t_GREATERTHANEQUAL = r'>='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURLY = r'{'
t_RCURLY = r'}'
t_SEMICOLON = r';'
t_LBRACE = r'\['
t_RBRACE = r'\]'
t_COMMA = r','


# Tokens with actions

# Comments
def t_COMMENT(t):
    r'//.*[\n]?'
    # Increment line number and don't return these tokens
    t.lexer.lineno += t.value.count('\n')


# Variables and reserved words
def t_ID(t):
    r'[_a-zA-Z]\w*'
    # If its in reserved, get the type
    # otherwise, its just an ID
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Bad integer: %r" % t.value
        t.value = 0
    return t

# Ignores characters
t_ignore = " \t"


# Increment line count
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# On character error
def t_error(t):
    raise ValueError("Illegal character %r at line: %s" % (
        t.value[0], t.lexer.lineno))
    # t.lexer.skip(1)
