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
import tokenize


def proto_tokenize(file_name):
    statements = []
    statement = []
    g = tokenize.generate_tokens(open(file_name, 'r').readline)
    for toknum, tokval, start, end, line in g:
        # Don't add newlines: we're looking for ;
        if toknum == tokenize.NEWLINE:
            continue
        statement.append([toknum, tokval, start, end, line])
        # If we hit a ; then its an end of statement
        if toknum == tokenize.OP and tokval == ';':
            statements.append(statement)
            statement = []
    for x in statements:
        print '%r' % x[0][4]
        for t in x:
            tokenize.printtoken(*t)
    return statements


def main(file_name):
    statement_tokens = proto_tokenize(file_name)

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
