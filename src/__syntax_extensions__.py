"""
Similar to __future__, this module exist to facility the `from __syntax_extensions__ import ...` syntax without having to much 
trouble with the normal import facilities.
"""
from typing import NamedTuple, Any


class ExtensionInfo(NamedTuple):
    import_name: str
    package_name: str
    version: str
    author: str
    extra_info: Any


def __getattr__(name):
    try:
        m = __import__('syntax_extensions.extensions.' + name)
    except ImportError as e:
        if e.name == 'syntax_extensions.extensions.' + name:
            raise AttributeError
        else:
            raise 
    else:
        m = getattr(m.extensions, name)
        return ExtensionInfo(
            name,
            getattr(m, '__package__', None),
            getattr(m, '__version__', None),
            getattr(m, '__author__', None),
            getattr(m, '__extra_info__', None),
        )
