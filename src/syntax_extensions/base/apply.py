from token import NAME, COMMENT
from tokenize import TokenInfo
from typing import Iterable, List
import re

from syntax_extensions.base.parser import parse, Module, Statement, Paren

IMPORT_PATTERN = re.compile(r"from __syntax_extensions__ import")


def _get_import_names(s: Statement) -> List[str]: # TODO: something better should be implemented and added as a general utility
    names = s.expr[3:]
    if isinstance(names[0], Paren):
        names = names[0].expr
    i = 0
    actual_names = []
    while i < len(names):
        n = names[i]
        if not isinstance(n, TokenInfo):
            i += 1
        elif n.string == 'as':
            i += 2
        elif n.string == ',':
            i += 1
        elif n.type == NAME:
            actual_names.append(n.string)
            i += 1
    return actual_names


def get_extensions(m: Module) -> List[str]:
    for s in m.stmts:
        if not isinstance(s.expr[0], TokenInfo):  # Lines that start with some kind of Parens aren't allowed
            break
        if s.expr[0].string == 'from':
            if not isinstance(s.expr[1], TokenInfo):  # This isn't valid.
                break
            if s.expr[1].string == '__future__':
                continue  # Ignore `__future__` statements. They have to appear before `__syntax_extensions__`
            elif s.expr[1].string == '__syntax_extensions__' and s.expr[2].string == 'import':
                return _get_import_names(s)
            else:
                break
        elif s.expr[0].type == COMMENT:
            continue
        else:
            break
    else:
        s = "EOF"
    print("Token ", s, "broke import syntax")
    return []


def apply(code: str, additional: Iterable[str] = ()) -> str:
    if not (additional or IMPORT_PATTERN.search(code)):  # Certainly nothing to do here
        return code
    m = parse(code)
    to_apply = list(additional) + get_extensions(m)
    if not to_apply:
        return code
    for n in to_apply:
        try:
            mod = __import__('syntax_extensions.extensions.' + n, fromlist=('transform',))
        except ImportError as e:
            if e.name != 'syntax_extensions.extensions.' + n:
                raise
        else:
            mod.transform(m)
    return m.unparse()
