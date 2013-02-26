import argparse
import os
import sys

import ply.lex as lex
import ply.yacc as yacc
import proto1lexer
import proto1parser

from AbstractSyntaxTree import ASTProgram


def main(args):
    # Remove file extension from name
    program_name = os.path.splitext(args.file)[0]
    # Load lexer
    lexer = lex.lex(module=proto1lexer)
    # Tokenize file
    lexer.input(open(args.file, 'r').read())
    # Load parser
    parser = yacc.yacc(module=proto1parser)
    # Parse program
    program = ASTProgram(parser.parse(open(args.file, 'r').read()))
    if not program.wellformed():
        print 'Program not well formed!'
        sys.exit(1)
    # Generate three address code
    tac = program.gencode()
    # Optimize and assign registers
    tac.registerize(flatten_temp=not(args.noflatten), ssa=not(args.nossa),
        propagate_variables=args.pv, propagate_constants=args.pc,
        eliminate_dead_code=args.dc)
    # Generate assembly
    asm = tac.gencode()
    if args.graphs:
        # Output program abstract syntax tree as png
        program.to_png(program_name)
        # Output liveliness coloring of
        tac.liveliness_graph.to_png(program_name)
    asm.write_to_file(program_name)
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Proto1 Compiler')
    parser.add_argument('-pc', action='store_true', default=False,
        help='Propagate constants')
    parser.add_argument('-pv', action='store_true', default=False,
        help='Propagate variables')
    parser.add_argument('-dc', action='store_true', default=False,
        help='Eliminate dead code')
    parser.add_argument('-nossa', action='store_false', default=True,
        help='Do NOT use SSA')
    parser.add_argument('-noflatten', action='store_false', default=True,
        help='Do NOT flatten temporary variables')
    parser.add_argument('-graphs', action='store_true', default=False,
        help='Generate png graphs for AST and liveliness')
    parser.add_argument('file', type=str, help='File to compile')
    args = parser.parse_args()
    if not os.path.exists(args.file):
        print '%r does not exist' % args.file
        sys.exit(1)
    main(args)
    sys.exit(0)
