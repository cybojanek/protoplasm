from nose.tools import *
import subprocess
from subprocess import Popen, PIPE


def compile_and_run(file_prefix, expected_output):
    expected_output = [str(x) for x in expected_output]
    # Call compiler to compile program
    subprocess.call(['python', 'proplasm1.py', 'tests/%s.proto' % file_prefix])
    # Call spim to run it
    p = Popen(['spim', '-file', 'tests/%s.asm' % file_prefix], stdout=PIPE,
            stdin=PIPE, stderr=PIPE)
    header, spim_result = p.stdout.readline(), [x.rstrip() for x in p.stdout.readlines()]
    eq_(spim_result, expected_output)

def test_math():
    """+ * / % operator"""
    compile_and_run('add', [12345678, 12345678, 7654322, 0, 12345678, 7654322,
        12345678, 7654322, 12345678, 7654322, 12345678, 7654322, -2345678,
        -2345678, -4691356, -4691356, -4691356])
    compile_and_run('mult', [838102050, 838102050, -838102050, -838102050,
        838102050, -838102050, 838102050, -838102050, 838102050, -838102050,
        152399025, -838102050, 152399025, 152399025, -152399025, -152399025])
    compile_and_run('div', [123456, -123456, 0, 0, 123456, -123456, 0, 0,
        123456, -123456, 0, 0, -1, 1, -1, 1, -1])
    compile_and_run('rem', [4, 4, 7890, -7890, 4, 4, 7890, -7890, 0, 0, 7890,
        -7890, 0, 0, 0, 0, 0])

def test_comparison():
    """== != < <= >= > operators"""
    compile_and_run('equals', [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1])
    compile_and_run('comparison', [0, 0, 1, 1, 0, 1, 0, 1])

def test_boolean_logic():
    """&& || ! operators"""
    compile_and_run('negation', [0, 0, 0, 1])
    compile_and_run('and_or', [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1])

def test_spilling():
    """Spill registers"""
    compile_and_run('spill_one', [66])
    compile_and_run('spill_five', [120])
    compile_and_run('spill_many', [681])

def test_if():
    """if/then/else statements"""
    compile_and_run('if', [1,1,1,2,2,0,1,1,1,1,2,2])

def test_while():
    """while do statements"""
    compile_and_run('while', [10, 10, 11, 3,6,9,12,15,18,21,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987])

