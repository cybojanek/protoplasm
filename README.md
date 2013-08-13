# Compiler Written For CSE 504 Spring 2013

The compiler works on C-like code and transforms it to MIPS assembly. I don't have the homework assignments anymore, so take a look at the **tests** directory for a lot of examples.

## Requirements

If you want to try it out, you're going to need the python **ply** package as a minimum. If you want to look at the extra goodies I coded up for fun, beyond the homework requirements, then install the **pygraphviz** package. If you pass in the **-graphs** flag, then you will get three pngs for every file: an Abstract Syntax Tree, register assignment and variable liveliness (coloring problem), and basic blocks.

## Sublime Text

If you're like me and you **LOVE** Sublime Text, then I added a syntax highlighter, preference file for comments, and some snippets for autocompletion. I could have just used the **C** syntax highlighter, but I wanted to learn how Sublime Text does it, which was kinda fun.

## Screenshots

![Sublime Text](https://github.com/cybojanek/protoplasm/raw/master/Sublime.png)
![AST](https://github.com/cybojanek/protoplasm/raw/master/fibonacci.ast.png)
![Basic Blocks](https://github.com/cybojanek/protoplasm/raw/master/fibonacci_basic_blocks.png)
![Coloring 1](https://github.com/cybojanek/protoplasm/raw/master/fibonacci_1_coloring.png)
![Coloring 7](https://github.com/cybojanek/protoplasm/raw/master/fibonacci_7_coloring.png)
