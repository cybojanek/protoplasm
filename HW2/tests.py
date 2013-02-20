from proplasm1 import proto_tokenize, ProtoParser

from nose.tools import *
from tokenize import TokenError


def add_newlines(array):
    return ['%s\n' % x for x in array]


def test_proto_token_errors():
    """proto1 token errors"""

    @raises(TokenError)
    def tokenize_with_error(lines):
        proto_tokenize(lines=lines)

    tests = [
        # Expects continuation of multi-line statement
        ['x = 2 * (2 -1'],
    ]
    for test in tests:
        tokenize_with_error(add_newlines(test))


def test_proto_syntax_errors():
    """proto1 syntax errors"""

    @raises(SyntaxError)
    def parse_with_error(lines):
        tokens = proto_tokenize(lines=lines)
        pp = ProtoParser(tokens)
        pp.check()

    tests = [
        # Missing semicolon
        ['x = 1'],
        # Trying to assign to reserved word print
        ['x = 1;', 'print = x;'],
        # Missing operand
        ['x = 1;', 'y = x + 2 *;'],
    ]
    for test in tests:
        parse_with_error(add_newlines(test))


def test_undefined_variables():
    """proto1 undefined variable errors"""

    @raises(NameError)
    def parse_with_error(lines):
        tokens = proto_tokenize(lines=lines)
        pp = ProtoParser(tokens)
        pp.check()

    tests = [
        # Base case
        ['x = x;'],
        ['x = x + 1;'],
        ['x = 1;', 'y = x + 1;', 'z = y + w;'],
    ]
    for test in tests:
        parse_with_error(add_newlines(test))


def test_proto_syntax():
    """proto1 syntax"""

    tests = [
        # Base case
        ['x = 1; print(x);'],
        # Multi line paranthesis should work
        ['x = 2 * (2 -', '1 + 2);'],
    ]
    for test in tests:
        tokens = proto_tokenize(lines=add_newlines(test))
        pp = ProtoParser(tokens)
        pp.check()


def test_proto_syntax_tree():
    """proto1 syntax tree"""

    tests = [
        (['x = 1;'], 'None -> [= -> [x,1]]'),
        (['x = 1;', 'z = x + 2 - 3;'],
            'None -> [= -> [x,1],= -> [z,+ -> [x,- -> [2,3]]]]'),
        (['x = 1;', 'print(x + 2);', 'z = input();'],
            'None -> [= -> [x,1],print -> [+ -> [x,2]],= -> [z,input]]')
    ]
    for test in tests:
        tokens = proto_tokenize(lines=add_newlines(test[0]))
        pp = ProtoParser(tokens)
        pp.check()
        eq_(str(pp.parse_tree), test[1])
