from token import OP, NAME, STRING

from syntax_extensions.base.parser import Module, Statement

__package__ = "syntax-extensions-base"
__author__ = "MegaIng"
__version__ = "1.0.0"
__extra_info__ = {}

def transform(m: Module):
    m.stmts.append(Statement([(NAME, 'print'), (OP, '('), (STRING, "'test_base works'"), (OP, ')')]))