### Homework 5
Implements HW4 proto compiler

Python packages used:

* **ply** for tokenizing and parsing (required)

* **argparse** for command line arguments (argparse is standard on 2.7+) (optional, includes default fallback mode)

* **pygraphviz** for graphing the AST and register allocation

Usage:

```bash
python proplasm4.py [OPTS] ex1.proto
```

Command line arguments (only available with argparse):

* **-h** **--help** print help menu

* **-graphs** output liveliness, AST, and basic block graphs in png format (requires _pygraphviz_)

### Developer notes
* **protoplasm4.py** is the glue code for running the compiler. It loads the program code, starts up the lexer and parser, and calls the AST tree to generate the intermediate code, and then converts that to assembly code.

* **proto4lexer.py** defines the set of tokens to which programs are translated

* **proto4parser.py** defines the CFG of the language, and generates an Abstract Syntax Tree of ASTNode objects

* **AsbstractSyntaxTree.py** contains various ASTNode object types, which generate Intermediate Code objects

* **IntermediateCode.py** contains various IC objects, which generate assembly. The ICContext performs any optimizations and assigns registers.

* **Graph.py** is a simple graph implementation used in assigning registers to variables (by solving a graph coloring problem)

* **ASMCode.py** holds the generic AsmInstruction class and writes out the assembled file

* **test.py** compiles, runs, and checks the output of all tests in _tests/*.proto_

* **tests/*.proto** are tests to be run by **test.py**. They must be added to **test.py** to be tested.
