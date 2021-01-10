__package__ = "syntax-extensions-base"
__author__ = "MegaIng"
__version__ = "1.0.0"
__extra_info__ = {}


from lark import Transformer, Tree
from lark.visitors import Transformer_InPlace
from syntax_extensions.base.python_parsing import PythonCodeTemplate

GRAMMAR = """

%extend compound_stmt: "repeat" test "times" ":" suite -> repeat_stmt

"""
USED_NAMES = ('compound_stmt', 'test', 'suite', '_DEDENT', '_INDENT', '_NEWLINE')




class MatchTransformer(Transformer_InPlace):
    def __init__(self, template: PythonCodeTemplate):
        super(MatchTransformer, self).__init__()
        self.template = template
    def test_base__repeat_stmt(self, children):
        return self.template.format(n=children[0], stmts=children[1].children)


TEMPLATE = """for _ in range($atom:n$):
    $suite:stmts*$"""


def get_extension_impl():
    return GRAMMAR, USED_NAMES, MatchTransformer(PythonCodeTemplate(TEMPLATE))
