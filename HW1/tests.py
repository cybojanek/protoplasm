from hw1_lists import dup, def_use, ssa
import itertools


def test_dup():
    tests = [
        ([1, 2, 3, 4], False),
        ([1, 2, 3, 2, 4], True),
        ]
    for test in tests:
        query, answer = test
        d = dup(query)
        print 'Query: %s\nReply :%s\nAnswer:%s' % (query, d, answer)
        assert dup(query) == answer


def test_def_use():
    tests = [
        ([ ['x', []], ['y', ['x']], ['z', ['x', 'y']], ['x', ['z', 'y']] ], []),
        ([ ['x', []], ['y', ['y', 'x']], ['z', ['x', 'w']], ['x', ['x', 'z']] ], ['y', 'w']),
        ]
    for test in tests:
        query, answer = test
        d = def_use(query)
        print 'Query: %s\nReply :%s\nAnswer:%s' % (query, d, answer)
        assert set(def_use(query)) == set(answer)


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
        print 'Query: %s\nReply :%s\nAnswer:%s' % (query, d, answer)
        assert len(d) == len(answer)
        for x, y in itertools.izip(d, answer):
            assert x == y
