"""
From PLY documentation:
 - All tokens defined by functions are added in the same order as they
   appear in the lexer file.

 - Tokens defined by strings are added next by sorting them in order of
   decreasing regular expression length (longer expressions are added first).

 - For example, if you wanted to have separate tokens for "=" and "==", you
   need to make sure that "==" is checked first. By sorting regular expressions
   in order of decreasing length, this problem is solved for rules defined
   as strings
"""

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
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

# Parsing rules

