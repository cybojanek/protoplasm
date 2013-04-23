try:
    import argparse
except ImportError:
    argparse = None
import os
import sys

import ply.lex as lex
import ply.yacc as yacc
import proto4lexer
import proto4parser

from proto4lexer import colorize

from AbstractSyntaxTree import ASTProgram
from ASMCode import write_asm_to_file


def main(args):
    # Remove file extension from name
    program_name = os.path.splitext(args.file)[0]
    # Load lexer
    lexer = lex.lex(module=proto4lexer)
    lexer.proto_file = args.file
    lexer.proto_errors = 0
    # Tokenize file
    lexer.input(open(args.file, 'r').read())
    lexer.lineno = 0
    # Load parser
    parser = yacc.yacc(module=proto4parser)
    parser.proto_errors = 0
    # Parse program
    try:
        program = parser.parse(open(args.file, 'r').read())
    except:
        # Exception probably because of errors
        if parser.proto_errors > 0 or lexer.proto_errors > 0:
            print colorize('Could not continue parsing due to previous errors', 'red')
            sys.exit(1)
        else:  # Idk
            raise
    if parser.proto_errors > 0 or lexer.proto_errors > 0:
        print colorize('Could not continue parsing due to previous errors', 'red')
        sys.exit(1)
    # print program
    # print 'FIX WELLFORMED'
    if not program.wellformed():
        print 'Program not well formed!'
        sys.exit(1)
    # Generate three address code
    tac = program.gencode()
    # print tac
    #print tac
    # for block in tac.blocks:
    #     print '----------\n'
    #     print 'MASTER:\n%s' % block
    #     for follow in block.follow:
    #         print 'FOLLOW:\n%s' % follow
    # sys.exit(0)
    # Optimize and assign registers
    tac.registerize(ssa=not(args.nossa))
    # for block in tac.blocks:
    #     print '----------\n'
    #     print 'MASTER:\n%s' % block
    #     for follow in block.follow:
    #         print 'FOLLOW:\n%s' % follow
    # sys.exit(0)
    # Generate assembly
    asm = tac.gencode()
    # for a in asm:
    #     print a
    if args.graphs:
        # Output program abstract syntax tree as png
        program.to_png(program_name)
        # Output liveliness coloring of
        for i, g in tac.all_graphs:
            g.to_png("%s_%s" % (program_name, i))
        tac.basic_blocks_to_png(program_name)
    write_asm_to_file(program_name, asm)
    sys.exit(0)

if __name__ == '__main__':
    if argparse is not None:
        parser = argparse.ArgumentParser(description='Proto4 Compiler')
        parser.add_argument('-nossa', action='store_true', default=False,
            help='Do NOT use SSA')
        parser.add_argument('-graphs', action='store_true', default=False,
            help='Generate png graphs for AST and liveliness')
        parser.add_argument('file', type=str, help='File to compile')
        args = parser.parse_args()
    else:
        class CArgs(object):
            def __init__(self):
                self.pc = False
                self.pv = False
                self.dc = False
                self.nossa = False
                self.noflatten = False
                self.graphs = False
                self.file = sys.argv[1]
        args = CArgs()
    if not os.path.exists(args.file):
        print '%r does not exist' % args.file
        sys.exit(1)
    main(args)
    sys.exit(0)
