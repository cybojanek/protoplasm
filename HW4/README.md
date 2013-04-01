### Homework 4
Implements HW4 proto compiler

Python packages used:

* **ply** for tokenizing and parsing (required)

* **argparse** for command line arguments (argparse is standard on 2.7+) (optional, includes default fallback mode)

* **pygraphviz** for graphing the AST and register allocation

Usage:

```bash
python proplasm1.py [OPTS] ex1.proto
```

Command line arguments (only available with argparse):

* **-h** **--help** print help menu

* **-graphs** output liveliness and AST graphs in png format (requires _pygraphviz_)

### Developer notes
* _protoplasm3.py_ is the glue code for running the compiler. It loads the program code, starts up the lexer and parser, and calls the AST tree to generate the intermediate code, and then converts that to assembly code.

* _proto3lexer.py_ defines the set of tokens to which programs are translated

* _proto3parser.py_ defines the CFG of the language, and generates an Abstract Syntax Tree of ASTNode objects

* _AsbstractSyntaxTree.py_ contains various ASTNode object types, which generate Intermediate Code objects

* _IntermediateCode.py_ contains various IC objects, which generate assembly. The ICContext performs any optimizations and assigns registers.

* _Graph.py_ is a simple graph implementation used in assigning registers to variables (by solving a graph coloring problem)

* _ASMCode.py_ holds the generic AsmInstruction class and writes out the assembled file

* _test.py_ compiles, runs, and checks the output of all tests in _tests/*.proto_

* _tests/*.proto_ are tests to be run by _test.py_. They must be added to _test.py_ to be tested.
