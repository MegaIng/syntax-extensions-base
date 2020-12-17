# syntax-extensions-base
Base package for syntax-extensions to python

Allows one to use/create custom syntax extensions for python as simple as possible.


## How to get started

First, you need to install this package, this can be done via cloning this repo and running `python -m pip install .` inside of the root folder.

Then you need to select a way of preloading `syntax-extensions` before python runs your code with extensions. This can be done a few ways:


- creating a `sitecustomize.py`/`usercustomize.py` file with the following content: `import syntax_extensions.activate; syntax_extensions.activate.activate_encoding()`
  - (This has to be somewhere in your PATH)
- The same line could also be put inside a `.pth` file. Name is irrelevant, but something clear will help (e.g. `syntax_extensions.pth`)
  - Needs to be inside `site-packages`
  - The line can't be split up.
- Creating an extra `main-wrapper.py` file that first executes the line, and the executes the actual main file.
- Other options will come in the future (most notably, a preloader script that acts like `main-wrapper.py` for any python command)

Now you need to actually write code using this. Here an example:

```
# -*- coding: syntax-extensions -*-
from __syntax_extensions__ import test_base

print(test_base)
```

Note that the first line is important, since it is what tells python to actually let `syntax_extensions` work on the file before it is parsed.

The second line tells `syntax_extensions` what to do. These extensions can be installed separately. At the moment, `test_base` is a very simple package to test that the infrastructure is working. It prints `Transforming...` when it is acting on the code and also adds a `print('test_base')` statement at the end of the file.

If you get an `SyntaxError: encoding problem: syntax-extensions` messages, this (probably) means that `syntax_extensions` isn't correctly preloaded.


## How it works

### Basic structure
`syntax-extensions-base` consists of a few parts:

-`__syntax_extensions__` - A simple module serving a similar purpose as `__future__`: Preventing the default import semantics from complaining about a non-existence module. Also allows one to get some basic info about the extensions.
-`syntax_extensions` - A namespace package, containing a variety of packages
  - `.base` The correct implementation: A parser, and a `apply` function (And utils in the future).
  - `.activate` A package containing glue code making sure that the extensions are applied. Will contain at least two methods, currently only `encoding` is implemented (and `import` is planned. This will override the default import mechanics)
  - `.__main__` Will at some point in the future be the wrapper script, to allow one to execute `python -m syntax_extensions main.py` without having to install some additional preloader.
  - `.extensions` Another namespace package. This is where other packages will put their code into.

### How to create your package

Uses this template: (TODO)

In general, you need to create a directory structure of the form `syntax_extensions/extensions/your_extension_name.py` *without* any `__init__.py` files. As long as the parent directory of `syntax_extensions`  is in the path, this should already be it. Now you just need to create a `transform` method inside the file that takes a `syntax_extensions.base.parser.Module` instance and transforms it inplace.
