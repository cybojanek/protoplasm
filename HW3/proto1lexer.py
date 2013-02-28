import ply.lex as lex

# Reserved words
reserved = {
    'print': 'PRINT',
    'input': 'INPUT'
}

# List of token names
tokens = ['EQUALS', 'SEMICOLON', 'LPAREN', 'RPAREN',
    'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'MODULUS',
    'ID', 'NUMBER'] + list(reserved.values())

# Tokens without actions
t_EQUALS = r'='
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_MINUS = r'-'
t_PLUS = r'\+'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULUS = r'%'


# Tokens with actions
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
    raise ValueError("Illegal character %r at line: %s" % (t.value[0], t.lexer.lineno))
    # t.lexer.skip(1)

# Parsing rules

