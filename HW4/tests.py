from nose.tools import *
import subprocess
from subprocess import Popen, PIPE


def test_proto_files():
    """Test tests/*.proto"""
    tests = [
        ['add', [12345678, 12345678, 7654322, 0, 12345678,
                  7654322, 12345678, 7654322, 12345678, 7654322,
                   12345678, 7654322, -2345678, -2345678,
                   -4691356, -4691356, -4691356]],
        ['div', [123456, -123456, 0, 0, 123456, -123456,
                 0, 0, 123456, -123456, 0, 0, -1, 1,
                  -1, 1, -1]],
        ['mult', [838102050, 838102050, -838102050, -838102050,
                  838102050, -838102050, 838102050, -838102050,
                  838102050, -838102050, 152399025, -838102050,
                  152399025, 152399025, -152399025, -152399025]],
        ['rem', [4, 4, 7890, -7890, 4, 4,
                 7890, -7890, 0, 0, 7890, -7890,
                 0, 0, 0, 0, 0]],
        ['equals', [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1]],
        ['comparison', [0, 0, 1, 1, 0, 1, 0, 1]],
        ['negation', [0, 0, 0, 1]],
        ['and_or', [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1]],
        ['spill_one', [66]],
        ['spill_five', [120]],
        ['spill_many', [681]],
        ['if', [1,1,1,2,2,0,1,1,1,1,2,2]],
        ['while', [10, 10, 11, 3,6,9,12,15,18,21,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987]]
    ]
    for test, results in tests:
        results = [str(x) for x in results]
        # Call compiler to compile program
        subprocess.call(['python', 'proplasm1.py', 'tests/%s.proto' % test])
        # Call spim to run it
        p = Popen(['spim', '-file',
            'tests/%s.asm' % test],
            stdout=PIPE, stdin=PIPE, stderr=PIPE)
        header, spim_result = p.stdout.readline(), [x.rstrip() for x in p.stdout.readlines()]
        eq_(spim_result, results)
        # eq_(p.returncode, 0)
