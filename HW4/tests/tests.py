from nose.tools import *
import subprocess
from subprocess import Popen, PIPE


def pre_entry(f):
    """Decorator for adding any pre test entry stuff.
    For now it just adds a newline so when you capture output,
    its on the next line after the test name

    """
    def new_f():
        print ""
        f()
    # Fix name and restore docstring
    new_f.__name__ = f.__name__
    new_f.__doc__ = f.__doc__
    return new_f


def compile_and_run(file_prefix, expected_output):
    expected_output = [str(x) for x in expected_output]
    # Call compiler to compile program
    print 'tests/%s.proto' % file_prefix
    subprocess.call(['python', 'proplasm3.py', 'tests/%s.proto' % file_prefix])
    # Call spim to run it
    p = Popen(['spim', '-file', 'tests/%s.asm' % file_prefix], stdout=PIPE,
              stdin=PIPE, stderr=PIPE)
    # Ignore first readline of header
    spim_result = [x.rstrip() for x in p.stdout.readlines()[1:]]
    eq_(spim_result, expected_output)


@pre_entry
def test_math():
    """+ - * / %"""
    compile_and_run('add', [12345678, 12345678, 7654322, 0, 12345678, 7654322,
                    12345678, 7654322, 12345678, 7654322, 12345678, 7654322,
                    -2345678, -2345678, -4691356, -4691356, -4691356])
    compile_and_run('sub', [7654322, -7654322, 12345678, 4691356, 7654322,
                    12345678, -7654322, -12345678, 7654322, 12345678, -7654322,
                    -12345678, 2345678, -2345678, 0, 0, 0])
    compile_and_run('mult', [838102050, 838102050, -838102050, -838102050,
                    838102050, -838102050, 838102050, -838102050, 838102050,
                    -838102050, 152399025, -838102050, 152399025, 152399025,
                    -152399025, -152399025])
    compile_and_run('div', [123456, -123456, 0, 0, 123456, -123456, 0, 0,
                    123456, -123456, 0, 0, -1, 1, -1, 1, -1])
    compile_and_run('rem', [4, 4, 7890, -7890, 4, 4, 7890, -7890, 0, 0, 7890,
                    -7890, 0, 0, 0, 0, 0])


@pre_entry
def test_comparison():
    """== != < <= >= >"""
    compile_and_run('equals', [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1])
    compile_and_run('comparison', [0, 0, 1, 1, 0, 1, 0, 1])


@pre_entry
def test_boolean_logic():
    """&& || !"""
    compile_and_run('bool', [1, 0, 2])
    compile_and_run('not', [0, 0, 0, 1])
    compile_and_run('and_or', [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1,
                    1])


@pre_entry
def test_if():
    """if/then/else"""
    compile_and_run('if', [1, 1, 1, 2, 2, 0, 1, 1, 1, 1, 2, 2])


@pre_entry
def test_while():
    """while"""
    compile_and_run('while_do', [10, 10, 11, 3, 6, 9, 12, 15, 18, 21, 1, 2, 3, 5,
                    8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987])
    compile_and_run('do_while', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3, 4,
                    1, 2, 3, 4, 2, 3, 4, 5])

@pre_entry
def test_spilling():
    """spill"""
    compile_and_run('spill_one', [66])
    compile_and_run('spill_five', [120])
    compile_and_run('spill_many', [681])
