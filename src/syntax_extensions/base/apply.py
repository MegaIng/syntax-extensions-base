from io import StringIO
from token import NAME, COMMENT, NEWLINE, NL, STRING
from tokenize import TokenInfo, generate_tokens
from typing import Iterable, List
import re

from syntax_extensions.base.python_parsing import Extension, build_parser, recons

IMPORT_PATTERN = re.compile(r"from __syntax_extensions__ import")


def _get_import_names(s: List[TokenInfo]) -> List[str]:
    assert (s[0].string, s[1].string, s[2].string) == ('from', '__syntax_extensions__', 'import')
    if s[3].string == '(':
        assert s[-1] == ')'
        s = s[4:-1]
    else:
        s = s[3:]
    names = []
    i = 0
    while i < len(s):
        if s[i].string == 'as':
            i += 1
        elif s[i].string == ',':
            pass
        else:
            names.append(s[i].string)
        i += 1
    return names


def _get_imported_extensions(m: str) -> List[str]:
    names = []
    from_line = []
    for t in generate_tokens(StringIO(m).readline):
        if from_line:
            if len(from_line) == 1:
                if t.string in ('__syntax_extensions__', '__future__'):
                    from_line.append(t)
                else:
                    break  # Some other import line. Stop searching
            else:
                if t.type == NEWLINE:
                    if from_line[1].string == '__syntax_extensions__':
                        names.extend(_get_import_names(from_line))
                    from_line = []
                elif t.type in (COMMENT, NL):
                    continue
                else:
                    from_line.append(t)
        elif from_line is not None:
            if t.string == 'from':
                from_line = [t]
            elif t.type in (NEWLINE, NL):
                continue
            else:
                from_line = None
        else:
            if t.type in (NEWLINE, NL):
                from_line = []
            elif t.type in (STRING, COMMENT):  # Only things allowed before a magic import
                continue
            else:
                break
    return names



def find_extensions(code: str, additional: Iterable[str] = ()) -> List[Extension]:
    if not (additional or IMPORT_PATTERN.search(code)):  # Certainly nothing to do here
        return []
    to_apply = list(additional) + _get_imported_extensions(code)
    extensions = []
    for n in to_apply:
        try:
            mod = __import__('syntax_extensions.extensions.' + n, fromlist=('transform',))
        except ImportError as e:
            if e.name != 'syntax_extensions.extensions.' + n:
                raise
            else:
                raise ImportError("Could not import syntax-extension: " + repr(n))
        else:
            extensions.append(Extension(n, *mod.get_extension_impl()))
    return extensions


def apply_extensions(code: str, extensions: List[Extension]):
    if not extensions:
        return code
    parser, trans = build_parser(extensions)
    tree = parser.parse(code + "\n", start='file_input')
    tree = trans.transform(tree)

    result = recons(tree)
    return result


def apply(code, additional: Iterable[str] = ()):
    return apply_extensions(code, find_extensions(code, additional))
