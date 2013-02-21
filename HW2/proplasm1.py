"""
TODO
Read program and convert to statements
Tokenize with python's tokenize
Abstract classes for intermediate code representation
Liveliness
MIPS

* Static semantics - valid grammar and all variables defined
* Dynamic semantics - how ops are run
"""

import os
import sys

from ProtoParse import proto_tokenize, ProtoParser


def main(file_name):
    statement_tokens = proto_tokenize(file_name)
    pp = ProtoParser(statement_tokens)
    pp.check()
    print pp.parse_tree
    pp.parse_tree.graphvizify()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: %s FILE" % (sys.argv[0])
        sys.exit(1)
    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print "%s does not exist" % (file_name)
        sys.exit(1)
    main(file_name)
    sys.exit(0)
