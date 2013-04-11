from nose.tools import *
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


def compile_and_run(file_prefix, expected_output, input_lines=None):
    expected_output = [str(x) for x in expected_output]
    # Call compiler to compile program
    print 'tests/%s.proto' % file_prefix
    p = Popen(['python2', 'proplasm3.py', 'tests/%s.proto' % file_prefix],
              stdout=PIPE, stdin=PIPE, stderr=PIPE)
    # Wait for compiler to finish compiling
    retcode = p.wait()
    # Check that there were no compile errors
    eq_(retcode, 0,
        'Failed to compile: %s.proto:\nSTDOUT:\n%s\nSTDERR:\n%s' % (
        file_prefix, ''.join(p.stdout.readlines()),
        ''.join(p.stderr.readlines())))
    # Call spim to run it
    p = Popen(['spim', '-file', 'tests/%s.asm' % file_prefix], stdout=PIPE,
              stdin=PIPE, stderr=PIPE)
    # Send input
    if input_lines is not None:
        [p.stdin.write('%s\n' % line) for line in input_lines]
    # Wait for program to finish running
    retcode = p.wait()
    eq_(retcode, 0)
    # Ignore first readline of header and strip any > from input requests
    spim_result = [x.rstrip().lstrip('>') for x in p.stdout.readlines()[1:]]
    eq_(spim_result, expected_output)


def compile_and_fail(file_prefix):
    print 'tests/%s.proto' % file_prefix
    p = Popen(['python2', 'proplasm3.py', 'tests/%s.proto' % file_prefix],
              stdout=PIPE, stdin=PIPE, stderr=PIPE)
    retcode = p.wait()
    eq_(retcode, 1, 'tests/%s.proto: %s != 1\n%s' % (file_prefix, retcode,
        'It compiled, but it should not have!'))


@pre_entry
def test_compile_errors():
    """compile errors"""
    compile_and_fail('fail_declare_block_array')
    compile_and_fail('fail_declare_block_array_partial')
    compile_and_fail('fail_declare_block_var')
    compile_and_fail('fail_declare_block_var_partial')
    compile_and_fail('fail_declare_global')
    compile_and_fail('fail_int_too_big')
    compile_and_fail('fail_int_too_small')
    compile_and_fail('fail_use_before_define')
    compile_and_fail('fail_use_before_define_array')


@pre_entry
def test_liveliness():
    """liveliness"""
    compile_and_run('liveliness', [10])


@pre_entry
def test_input():
    """input"""
    compile_and_run('input', [-15, -27], [5, -3, -9, 3])


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
    compile_and_run('if', [1, 1, 1, 2, 2, 0, 1, 1, 1, 1, 2, 2, 0, 0])


@pre_entry
def test_while():
    """while"""
    compile_and_run('while_do', [10, 10, 11, 3, 6, 9, 12, 15, 18, 21, 1, 2, 3,
                    5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987])
    compile_and_run('do_while', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3,
                    4, 1, 2, 3, 4, 2, 3, 4, 5])


@pre_entry
def test_for():
    """for"""
    compile_and_run('for', [120, 5, 5, 5])


@pre_entry
def test_spilling():
    """spill"""
    compile_and_run('spill_one', [66])
    compile_and_run('spill_five', [120])
    compile_and_run('spill_many', [681])


@pre_entry
def test_cascade():
    """cascade"""
    compile_and_run('cascade', [64, 64, 2])


@pre_entry
def test_scope():
    """variable scope"""
    compile_and_run('scope', [1, 3, 1, 0])


@pre_entry
def test_array():
    """arrays"""
    compile_and_run('arrays', [0, 1, 2, 3, 4, 0, 1, 1, 2, 0, 1, 1, 2, 0, 1, 2,
                    3, 4, 1])


@pre_entry
def test_increment():
    """++ --"""
    compile_and_run('pre_post_increment', [1, 0, 0, 0, 2, 2, 0, 1, 0, 1, 0, 0,
                    1, 0, 1, 0, 0, 1, 1, 1])
    compile_and_run('pre_post_array', [1, 1, 1, 3, 8, 1, 1, 2, 3])
