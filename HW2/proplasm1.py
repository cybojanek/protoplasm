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

import ply.lex as lex
import ply.yacc as yacc
import proto1lexer
import proto1parser
from AbstractSyntaxTree import ASTProgram

def main(file_name):
    lexer = lex.lex(module=proto1lexer)
    lexer.input(open(file_name, 'r').read())
    parser = yacc.yacc(module=proto1parser)
    program = ASTProgram(parser.parse(open(file_name, 'r').read()))
    if not program.wellformed():
        print 'Program not well formed!'
        sys.exit(1)
    program.to_png('%s.ast.png' % file_name)
    tac = program.gencode()
    tac.registerize(ssa=True)
  #  tas = tac.instructions
  #  for i in tas:
  #      print '%s' % (i, )
  #  print "---- ASM ----"
    asm = tac.gencode()
    for i in asm.instructions:
        print "%s" % (i)

    #print "Done with liveliness!"
    #tac.liveliness_to_png('%s.liveliness.png' % file_name)
    # [s.wellformed() for s in stmts]

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
