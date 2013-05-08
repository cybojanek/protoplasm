from nose.tools import *
from subprocess import Popen, PIPE


RUNTIME_OOB = "Proto Runtime Error: Attempt to access array out of bounds."


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
    p = Popen(['python2', 'proplasm5.py', 'tests/%s.proto' % file_prefix],
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
    p = Popen(['python2', 'proplasm5.py', 'tests/%s.proto' % file_prefix],
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
    compile_and_fail('fail_function_num_args')
    compile_and_fail('fail_function_type_args')
    compile_and_fail('fail_int_too_big')
    compile_and_fail('fail_int_too_small')
    compile_and_fail('fail_return_flow_if_then_else')
    compile_and_fail('fail_return_flow_main')
    compile_and_fail('fail_return_type_function')
    compile_and_fail('fail_return_type_variable')
    compile_and_fail('fail_use_before_define')
    compile_and_fail('fail_use_before_define_array')


@pre_entry
def test_classes():
    """classes"""
    compile_and_run('class', [1, 2, 3, 4, 5, 6, 5, 7, 9])
    compile_and_run('class_arrays', [435, 4, 0, 1, 1])


@pre_entry
def test_functions():
    """functions"""
    compile_and_run('arguments', [21, 81])


@pre_entry
def test_recursion():
    """recursion"""
    compile_and_run('factorial', [120, 479001600])
    compile_and_run('fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144,
                                  233, 377, 610, 987, 1597, 2584, 4181])


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
    compile_and_run('not', [0, 1])
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
    compile_and_run('spill_array', [86, 0, 1, 2, 3, 4])
    compile_and_run('spill_across_functions', [1056, 253])


@pre_entry
def test_return():
    """return"""
    compile_and_run('return', [10, 0, 13, 26, 39, 52, 65, 78, 91, 104, 117])


@pre_entry
def test_cascade():
    """cascade"""
    compile_and_run('cascade', [64, 64, 2])
    compile_and_run('cascade_array', [1, 1, 1])


@pre_entry
def test_scope():
    """variable scope"""
    compile_and_run('scope', [1, 3, 1, 0, 1, 1, 4])


@pre_entry
def test_global():
    """global variables"""
    compile_and_run('scope_functions_global', [5, 6, 6, 3, 6, 12, 6, 0, 1, 2,
                    3, 4, 7, 8, 9, 10, 11])


@pre_entry
def test_array():
    """arrays"""
    compile_and_run('arrays', [0, 1, 2, 3, 4, 0, 1, 1, 2, 0, 1, 1, 2, 0, 1, 2,
                    3, 4, 1])


@pre_entry
def test_increment():
    """++ --"""
    compile_and_run('pre_post_increment', [1, 0, 0, 2, 2, 0, 1, 0, 2, 1, 0, 3,
                    3, 1, 0, 0, 1, 1, 1])
    compile_and_run('pre_post_array',  [1, 1, 2, 3, 4, 0, 0, 5, 0, 1, 2, 3, 4, 1,
                    2, 3, 4, 5, 2, 3, 4, 5, 6, 3, 4, 5, 6, 7, 4, 5, 6, 7, 8])


@pre_entry
def test_runtime_error():
    """array bounds"""
    compile_and_run('fail_array_bounds', [0, RUNTIME_OOB])


@pre_entry
def test_comments():
    """comments"""
    compile_and_run('comments', [1])

@pre_entry
def test_inheritance():
    """class functions & inheritance"""
    compile_and_run('class_inherited_properties', [20, 30, 40])
    compile_and_run('class_functions', [20,30,40,90,20,62,62])

@pre_entry
def test_empty():
    """empty"""
    compile_and_run('empty', [])


@pre_entry
def test_hw4():
    """Homework 5"""
    compile_and_run('HW5/t1', [52])
    compile_and_fail('HW5/t2')
    compile_and_run('HW5/t3', [52, 42], [10])
    compile_and_fail('HW5/t4')
    compile_and_run('HW5/t5', [0, -420])
    compile_and_run('HW5/t6', [5, 0])
    compile_and_run('HW5/t7', [-18, -330])
    compile_and_run('HW5/t8', [70])
    compile_and_fail('HW5/t9')
    compile_and_fail('HW5/t10')
    compile_and_run('HW5/t11', [528])
    compile_and_run('HW5/t12', [1])
    compile_and_run('HW5/t13', [11])
    compile_and_fail('HW5/t14')
    compile_and_fail('HW5/t15')
    compile_and_run('HW5/t16', [0])
    compile_and_run('HW5/t17', [42, 0])
    compile_and_fail('HW5/t18')
    compile_and_run('HW5/t19', [-30])
    # compile_and_run('HW5/t20', [0])  # Not used
    compile_and_fail('HW5/t21')
    compile_and_run('HW5/t22', [42, 10, 42])
    compile_and_run('HW5/t23', [42])
    compile_and_run('HW5/t24', [0, 1, 2])
    compile_and_run('HW5/t25', [0, 1, 2])
    compile_and_run('HW5/t26', [1, 2, 3, 4])
    compile_and_run('HW5/t27', [RUNTIME_OOB])
    compile_and_run('HW5/t28', [42, 42])
    compile_and_run('HW5/t29', [42, 41])
    compile_and_run('HW5/t30', [42, 41])
    compile_and_run('HW5/t31', [24, 42, 42])
    # compile_and_run('HW5/t32', [24, 42, 42])  # Not used
    compile_and_run('HW5/t33', [1, 1, 1])  # WRONG-ish
    compile_and_run('HW5/t34', [RUNTIME_OOB], [5])
    compile_and_fail('HW5/t35')
    compile_and_fail('HW5/t36')
    compile_and_fail('HW5/t37')
    compile_and_fail('HW5/t38')
    compile_and_fail('HW5/t39')
    compile_and_fail('HW5/t40')
    compile_and_fail('HW5/t41')
    compile_and_fail('HW5/t42')
    compile_and_fail('HW5/t43')
    compile_and_fail('HW5/t44')
    compile_and_fail('HW5/t45')
    compile_and_fail('HW5/t46')
    compile_and_fail('HW5/t47')
    compile_and_fail('HW5/t48')
    compile_and_fail('HW5/t49')
    compile_and_fail('HW5/t50')
    compile_and_fail('HW5/t51')
    compile_and_fail('HW5/t52')
    compile_and_fail('HW5/t53')
    compile_and_fail('HW5/t54')
    compile_and_fail('HW5/t55')
    compile_and_fail('HW5/t56')
    compile_and_fail('HW5/t57')
    compile_and_fail('HW5/t58')
    compile_and_fail('HW5/t59')
    compile_and_run('HW5/t60', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    compile_and_run('HW5/t61', [42, 43])
    compile_and_run('HW5/t62', [41, 42])
    compile_and_run('HW5/t63', [38, 40, 42])
    compile_and_run('HW5/t64', [1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
    compile_and_run('HW5/t65', [42], [4])
    compile_and_run('HW5/t66', [42])
    compile_and_run('HW5/t67', [42])
    compile_and_fail('HW5/t68')
    compile_and_run('HW5/t69', [42])
