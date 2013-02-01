from hw1_lists import dup, def_use, ssa
from hw1_classes import PBF, OR, AND, NOT, PROP
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
