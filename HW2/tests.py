from proplasm1 import proto_tokenize, ProtoSyntaxChecker

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
        psc = ProtoSyntaxChecker(tokens)
        psc.check()

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
        psc = ProtoSyntaxChecker(tokens)
        psc.check()

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
        psc = ProtoSyntaxChecker(tokens)
        psc.check()
