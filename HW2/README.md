### Homework 2
Implements a compiler for the CFG specified in homework 2.

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

* **-pc** propagate constants at compile time: 'a = 1; b = 2 * a; print(b);' becomes 'print(2);'

* **-pv** propagate variables by parsing through variable assignments: 'a=b; c=b;' becomes 'c=a;' and may be simplified further down also

* **-dc** remove dead code, unused variables, (those which never reach print or input)

* **no-flatten** do _NOT_ flatten temporary assignments. 'a = 1 + 2;' is actually: '@0 = 1 + 2; a = @0;' this flattens these expansions to: 'a = 1 + 2;' (this happens due to the tree expansion)

* **-graphs** output liveliness and AST graphs in png format (requires _pygraphviz_)