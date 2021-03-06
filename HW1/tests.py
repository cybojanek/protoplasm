from hw1_lists import dup, def_use, ssa
from hw1_classes import PBF, OR, AND, NOT, PROP
from hw1_classes import parse, ParseError, TokenError, PBFToken
from subprocess import Popen, PIPE
from nose.tools import *
import itertools


def test_dup():
    tests = [
        ([1, 2, 3, 4], False),
        ([1, 2, 3, 2, 4], True),
    ]
    for test in tests:
        query, answer = test
        d = dup(query)
        eq_(d, answer, msg="\nQuery: %s\n%r != %r" % (query, d, answer))


def test_def_use():
    tests = [
        ([ ['x', []], ['y', ['x']], ['z', ['x', 'y']], ['x', ['z', 'y']] ], []),
        ([ ['x', []], ['y', ['y', 'x']], ['z', ['x', 'w']], ['x', ['x', 'z']] ], ['y', 'w']),
        ([ ['x', ['x']], ['y', ['x']] ], ['x']),
    ]
    for test in tests:
        query, answer = test
        d = def_use(query)
        eq_(len(d), len(answer), msg="\nQuery: %s\nlen(%r) != len(%r)" % (query, d, answer))
        eq_(set(d), set(answer), msg="\nQuery: %s\n%r != %r" % (query, d, answer))


def test_ssa():
    tests = [
        ([ ['x', []], ['y', ['x']], ['x', ['x', 'y']], ['z', ['x', 'y']], ['y', ['z', 'x']] ],
         [ ['x', []], ['y', ['x']], ['x1', ['x', 'y']], ['z', ['x1', 'y']], ['y1', ['z', 'x1']] ]),
        ([ ['x', []], ['x', ['x']], ['x', ['x']] ],
         [ ['x', []], ['x1', ['x']], ['x2', ['x1']] ]),
        ([ ['x', []], ['x', []], ['x', []] ],
         [ ['x', []], ['x1', []], ['x2', []] ])
    ]
    for test in tests:
        query, answer = test
        d = ssa(query)
        eq_(len(d), len(answer), msg="\nQuery: %s\nlen(%r) != len(%r)" % (query, d, answer))
        for x, y in itertools.izip(d, answer):
            eq_(x, y, msg="\nQuery: %s\n%r != %r" % (query, d, answer))


def test_NNF():
    tests = [
        (PROP('x'), True, 'x'),
        (NOT(PROP('x')), True, "x !"),
        (AND(PROP('x'), NOT(PROP('y'))), True, "x y ! &"),
        (NOT(AND(PROP('x'), NOT(PROP('y')))), False, "x ! y |"),
        (NOT(NOT(PROP('x'))), False, 'x'),
        (NOT(NOT(NOT(PROP('x')))), False, "x !")
    ]
    for test in tests:
        query, answer_a, answer_b = test
        d = query.isNNF()
        eq_(d, answer_a, msg="\nQuery: %s\n%r != %r" % (query, d, answer_a))
        d = str(query.toNNF())
        eq_(str(d), answer_b, msg="\nQuery: %s\n%r != %r" % (query, d, answer_b))


def test_parse():

    @raises(ParseError)
    def parse_with_error(s):
        return str(parse(s))

    @raises(TokenError)
    def token_with_error(s):
        return PBFToken.tokenize(s)

    tests = [
        'x',
        "x y &",
        "x y & z |",
        "x y ! & z ! |",
    ]
    for test in tests:
        d = str(parse(test))
        eq_(d, test, msg="\n %r != %r" % (d, test))

    tests = [
        'x x',
        'x &',
        'x x & z !'
    ]
    for test in tests:
        parse_with_error(test)

    tests = ['#', '7', 'x1']
    for test in tests:
        token_with_error(test)


def test_mips():
    tests = [
        (1, 0),
        (4, 3),
        (10, 8),
        (9876543, 9876529),
        (1073741829, 1073741826),
        (2147483647, 2147483616),
    ]
    for test in tests:
        n, k = test
        p = Popen(['java', '-jar', 'Mars_4_2.jar', 'hw1_mips.asm'],
            stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input='%s\n' % n)
        answer = int(out.split('\n')[-2])
        eq_(p.returncode, 0)
        eq_(len(err), 0)
        eq_(answer, k)

    for test in [0, -1, -2323]:
        p = Popen(['java', '-jar', 'Mars_4_2.jar', 'hw1_mips.asm'],
            stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input='%s\n' % test)
        eq_(p.returncode, 1)
