import sys
import types

from importlib.machinery import FileFinder, SourceFileLoader, SOURCE_SUFFIXES, SourcelessFileLoader, ExtensionFileLoader, \
    EXTENSION_SUFFIXES, BYTECODE_SUFFIXES
from typing import Union, Optional, Callable

from syntax_extensions.base.apply import apply

def _get_line(text, n):
    lines = text.splitlines(True)
    if not 0<n<=len(lines):
        return ''
    else:
        return lines[n-1].replace('\r\n', '\n')

class ExtendedSourceFileLoader(SourceFileLoader):
    def source_to_code(self, data: Union[bytes, str], path: str = ...) -> types.CodeType:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        code = apply(data)
        try:
            return super().source_to_code(code, path)
        except SyntaxError as e:
            if _get_line(data, e.lineno) == e.text:
                e.text = _get_line(code, e.lineno)
            raise
    


class ExtendedSourceFileLoaderNoCache(ExtendedSourceFileLoader):
    def path_stats(self, path):
        raise OSError


def exclude_nothing(path: str) -> bool:
    return False


def activate_import(exclude_path: Callable[[str], bool] = exclude_nothing, no_cache: bool = False):
    extensions = ExtensionFileLoader, EXTENSION_SUFFIXES
    if no_cache:
        source = ExtendedSourceFileLoaderNoCache, SOURCE_SUFFIXES
    else:
        source = ExtendedSourceFileLoader, SOURCE_SUFFIXES
    bytecode = SourcelessFileLoader, BYTECODE_SUFFIXES
    new = FileFinder.path_hook(extensions, source, bytecode)

    def path_hook_for_syntax_extensions(path):
        if exclude_path(path):
            return old(path)
        else:
            return new(path)

    for i, h in enumerate(sys.path_hooks):
        if h.__name__ == new.__name__:
            old = sys.path_hooks[i]
            sys.path_hooks[i] = path_hook_for_syntax_extensions
            break
    else:
        assert False
    sys.path_importer_cache.clear()
