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
