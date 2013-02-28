from nose.tools import *
import subprocess
from subprocess import Popen, PIPE


def test_proto_files():
    """Test tests/*.proto"""
    tests = [
        ['add', ['12345678', '12345678', '7654322', '0', '12345678',
                  '7654322', '12345678', '7654322', '12345678', '7654322',
                   '12345678', '7654322', '-2345678', '-2345678',
                   '-4691356', '-4691356', '-4691356']],
        ['div', ['123456', '-123456', '0', '0', '123456', '-123456',
                 '0', '0', '123456', '-123456', '0', '0', '-1', '1',
                  '-1', '1', '-1']],
        ['mult', ['838102050', '838102050', '-838102050', '-838102050',
                  '838102050', '-838102050', '838102050', '-838102050',
                  '838102050', '-838102050', '152399025', '-838102050',
                  '152399025', '152399025', '-152399025', '-152399025']],
        ['rem', ['4', '4', '7890', '-7890', '4', '4',
                 '7890', '-7890', '0', '0', '7890', '-7890',
                 '0', '0', '0', '0', '0']],
        ['spill_one', ['66']],
        ['spill_five', ['120']],
        ['spill_many', ['681']],
    ]
    for test, results in tests:
        test_result = ''.join(results)
        # Call compiler to compile program
        subprocess.call(['/usr/local/bin/python', 'proplasm1.py',
            'tests/%s.proto' % test])
        # Call spim to run it
        p = Popen(['/Users/cybojanek/sources/spimsimulator/spim/spim', '-file',
            'tests/%s.asm' % test],
            stdout=PIPE, stdin=PIPE, stderr=PIPE)
        header, result = p.stdout.readline(), p.stdout.readline()
        eq_(result, test_result)
        # eq_(p.returncode, 0)
