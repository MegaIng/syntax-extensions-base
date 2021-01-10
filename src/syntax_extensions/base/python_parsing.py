from typing import List, NamedTuple, Tuple, Dict, Union

from lark import Transformer, Token, Tree, v_args
from lark.indenter import Indenter
from lark.lark import Lark
from lark.load_grammar import GrammarBuilder
from lark.reconstruct import Reconstructor
from lark.visitors import Transformer_InPlace

PYTHON3_GRAMMAR = r"""
// Python 3 grammar for Lark

// NOTE: Work in progress!!! (XXX TODO)
// This grammar should parse all python 3.x code successfully,
// but the resulting parse-tree is still not well-organized.

// Adapted from: https://docs.python.org/3/reference/grammar.html
// Adapted by: Erez Shinan

// Start symbols for the grammar:
//       single_input is a single interactive statement;
//       file_input is a module or sequence of commands read from an input file;
//       eval_input is the input for the eval() functions.
// NB: compound_stmt in single_input is followed by extra NEWLINE!
single_input: _NEWLINE | simple_stmt | compound_stmt _NEWLINE
file_input: (_NEWLINE | stmt)*
eval_input: testlist _NEWLINE*

decorator: "@" dotted_name [ "(" [arguments] ")" ] _NEWLINE
decorators: decorator+
decorated: decorators (classdef | funcdef | async_funcdef)

async_funcdef: "async" funcdef
funcdef: "def" NAME "(" parameters? ")" ["->" test] ":" suite

parameters: paramvalue ("," paramvalue)* ["," SLASH] ["," [starparams | kwparams]]
          | starparams
          | kwparams

SLASH: "/" // Otherwise the it will completely disappear and it will be undisguisable in the result
starparams: "*" typedparam? ("," paramvalue)* ["," kwparams]
kwparams: "**" typedparam

?paramvalue: typedparam ["=" test]
?typedparam: NAME [":" test]

varargslist: (vfpdef ["=" test] ("," vfpdef ["=" test])* ["," [ "*" [vfpdef] ("," vfpdef ["=" test])* ["," ["**" vfpdef [","]]] | "**" vfpdef [","]]]
  | "*" [vfpdef] ("," vfpdef ["=" test])* ["," ["**" vfpdef [","]]]
  | "**" vfpdef [","])

vfpdef: NAME

?stmt: simple_stmt | compound_stmt
?simple_stmt: small_stmt (";" small_stmt)* [";"] _NEWLINE
?small_stmt: (expr_stmt | del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt)
?expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist)
         | ("=" (yield_expr|testlist_star_expr))*)
annassign: ":" test ["=" test]
?testlist_star_expr: (test|star_expr) ("," (test|star_expr))* [","]
!augassign: ("+=" | "-=" | "*=" | "@=" | "/=" | "%=" | "&=" | "|=" | "^=" | "<<=" | ">>=" | "**=" | "//=")
// For normal and annotated assignments, additional restrictions enforced by the interpreter
del_stmt: "del" exprlist
pass_stmt: "pass"
?flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
break_stmt: "break"
continue_stmt: "continue"
return_stmt: "return" [testlist]
yield_stmt: yield_expr
raise_stmt: "raise" [test ["from" test]]
import_stmt: import_name | import_from
import_name: "import" dotted_as_names
// note below: the ("." | "...") is necessary because "..." is tokenized as ELLIPSIS
import_from: "from" (dots? dotted_name | dots) "import" ("*" | "(" import_as_names ")" | import_as_names)
!dots: "."+
import_as_name: NAME ["as" NAME]
dotted_as_name: dotted_name ["as" NAME]
import_as_names: import_as_name ("," import_as_name)* [","]
dotted_as_names: dotted_as_name ("," dotted_as_name)*
dotted_name: NAME ("." NAME)*
global_stmt: "global" NAME ("," NAME)*
nonlocal_stmt: "nonlocal" NAME ("," NAME)*
assert_stmt: "assert" test ["," test]

?compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt
async_stmt: "async" (funcdef | with_stmt | for_stmt)
if_stmt: "if" test ":" suite ("elif" test ":" suite)* ["else" ":" suite]
while_stmt: "while" test ":" suite ["else" ":" suite]
for_stmt: "for" exprlist "in" testlist ":" suite ["else" ":" suite]
try_stmt: ("try" ":" suite ((except_clause ":" suite)+ ["else" ":" suite] ["finally" ":" suite] | "finally" ":" suite))
with_stmt: "with" with_item ("," with_item)*  ":" suite
with_item: test ["as" expr]
// NB compile.c makes sure that the default except clause is last
except_clause: "except" [test ["as" NAME]]
suite: simple_stmt | _NEWLINE _INDENT stmt+ _DEDENT

?test: or_test ("if" or_test "else" test)? | lambdef
?test_nocond: or_test | lambdef_nocond
lambdef: "lambda" [varargslist] ":" test
lambdef_nocond: "lambda" [varargslist] ":" test_nocond
?or_test: and_test ("or" and_test)*
?and_test: not_test ("and" not_test)*
?not_test: "not" not_test -> not
         | comparison
?comparison: expr (_comp_op expr)*
star_expr: "*" expr
?expr: xor_expr ("|" xor_expr)*
?xor_expr: and_expr ("^" and_expr)*
?and_expr: shift_expr ("&" shift_expr)*
?shift_expr: arith_expr (_shift_op arith_expr)*
?arith_expr: term (_add_op term)*
?term: factor (_mul_op factor)*
?factor: _factor_op factor | power

!_factor_op: "+"|"-"|"~"
!_add_op: "+"|"-"
!_shift_op: "<<"|">>"
!_mul_op: "*"|"@"|"/"|"%"|"//"
// <> isn't actually a valid comparison operator in Python. It's here for the
// sake of a __future__ import described in PEP 401 (which really works :-)
!_comp_op: "<"|">"|"=="|">="|"<="|"<>"|"!="|"in"|"not" "in"|"is"|"is" "not"

?power: await_expr ("**" factor)?
?await_expr: AWAIT? atom_expr
AWAIT: "await"

?atom_expr: atom_expr "(" [arguments] ")"      -> funccall
          | atom_expr "[" subscriptlist "]"  -> getitem
          | atom_expr "." NAME               -> getattr
          | atom

?atom: "(" [yield_expr|_tuplelist_comp] ")" -> tuple
     | "[" [test | _tuplelist_comp] "]"  -> list
     | "{" [dict_comp] "}" -> dict
     | "{" set_comp "}" -> set
     | NAME -> var
     | number | string
     | "(" test ")"
     | "..." -> ellipsis
     | "None"    -> const_none
     | "True"    -> const_true
     | "False"   -> const_false

_tuplelist_comp: (test|star_expr) (comp_for | ("," (test|star_expr))+ [","] | ",")
?subscriptlist: subscript
              | subscript (("," subscript)+ [","] | ",") -> subscript_tuple
subscript: test | [test] ":" [test] [sliceop]
sliceop: ":" [test]
exprlist: (expr|star_expr)
        | (expr|star_expr) (("," (expr|star_expr))+ [","]|",") -> exprlist_tuple
testlist: test | testlist_tuple
testlist_tuple: test (("," test)+ [","] | ",")
dict_comp: key_value comp_for 
         | (key_value | "**" expr) ("," (key_value | "**" expr))* [","]

key_value: test ":"  test

set_comp: test comp_for 
        | (test|star_expr) ("," (test | star_expr))* [","]

classdef: "class" NAME ["(" [arguments] ")"] ":" suite

arguments: argvalue ("," argvalue)*  ("," [ starargs | kwargs])?
         | starargs
         | kwargs
         | test comp_for

starargs: "*" test ("," "*" test)* ("," argvalue)* ["," kwargs]
kwargs: "**" test

?argvalue: test ("=" test)?



comp_iter: comp_for | comp_if | async_for
async_for: "async" "for" exprlist "in" or_test [comp_iter]
comp_for: "for" exprlist "in" or_test [comp_iter]
comp_if: "if" test_nocond [comp_iter]

// not used in grammar, but may appear in "node" passed from Parser to Compiler
encoding_decl: NAME

yield_expr: "yield" [yield_arg]
yield_arg: "from" test | testlist


number: DEC_NUMBER | HEX_NUMBER | BIN_NUMBER | OCT_NUMBER | FLOAT_NUMBER | IMAG_NUMBER
string: (STRING | LONG_STRING)+

// Import terminals from standard library (grammars/python.lark)
%import python (NAME, COMMENT, STRING, LONG_STRING)
%import python (DEC_NUMBER, HEX_NUMBER, OCT_NUMBER, BIN_NUMBER, FLOAT_NUMBER, IMAG_NUMBER)

// Other terminals

_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+

%ignore /[\t \f]+/  // WS
%ignore /\\[\t \f]*\r?\n/   // LINE_CONT
%ignore COMMENT
%declare _INDENT _DEDENT

"""

TEMPLATE_PYTHON = """
%extend stmt: "$stmt:" NAME "$" -> template_stmt
%extend suite: _NEWLINE _INDENT "$suite:" NAME "*$" _NEWLINE? _DEDENT  -> template_suite
%extend atom: "$atom:" NAME "$" -> template_atom
"""


def _special(sym):
    return Token('SPECIAL', sym.name)


class PythonIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8


USEFUL_STARTS = ['file_input', 'single_input', 'eval_input', 'stmt']

base_python3_parser = Lark(PYTHON3_GRAMMAR, lexer='standard', start=USEFUL_STARTS, postlex=PythonIndenter())
template_python3_parser = Lark(PYTHON3_GRAMMAR + TEMPLATE_PYTHON, lexer='standard', start=USEFUL_STARTS, postlex=PythonIndenter())
base_python3_recons = Reconstructor(base_python3_parser, {'_NEWLINE': _special, '_DEDENT': _special, '_INDENT': _special})


class Extension(NamedTuple):
    name: str
    grammar: str
    used_names: Tuple[str, ...]
    transformer: Transformer_InPlace


def _indent_postproc(items):
    stack = ['\n']
    actions = []
    for item in items:
        if isinstance(item, Token) and item.type == 'SPECIAL':
            actions.append(item.value)
        else:
            if actions:
                assert actions[0] == '_NEWLINE' and '_NEWLINE' not in actions[1:], actions

                for a in actions[1:]:
                    if a == '_INDENT':
                        stack.append(stack[-1] + ' ' * 4)
                    else:
                        assert a == '_DEDENT'
                        stack.pop()
                actions.clear()
                yield stack[-1]
            yield item


def build_parser(extensions: List[Extension]) -> Tuple[Lark, Transformer_InPlace]:
    builder = GrammarBuilder()

    builder.load_grammar(PYTHON3_GRAMMAR, 'python3')

    transformer = Transformer_InPlace()

    for e in extensions:
        mangle = builder.get_mangle(e.name, dict(zip(e.used_names, e.used_names)))
        builder.load_grammar(e.grammar, e.name, mangle)
        transformer *= e.transformer

    grammar = builder.build()

    parser = Lark(grammar, parser='earley', lexer='standard', start=USEFUL_STARTS, postlex=PythonIndenter())

    return parser, transformer


def recons(tree: Tree):
    return base_python3_recons.reconstruct(tree, _indent_postproc)


@v_args(inline=True)
class TemplateFiller(Transformer):
    def __init__(self, values: Dict[str, Union[Token, Tree, List[Tree]]]):
        super(TemplateFiller, self).__init__()
        self.values = values

    def template_atom(self, name: Token):
        return self.values[name.value]

    def template_stmt(self, name: Token):
        return self.values[name.value]

    def template_suite(self, name: Token):
        assert isinstance(self.values[name.value], list)
        return Tree('suite', self.values[name.value])


class PythonCodeTemplate:
    def __init__(self, code: str, start: str = 'stmt'):
        self.template_tree = template_python3_parser.parse(code, start=start)

    def format(self, values: Dict[str, Union[Token, Tree, List[Tree]]]=None, /, **kwargs: Union[Token, Tree, List[Tree]]) -> Tree:
        values = values | kwargs if values is not None else kwargs
        filler = TemplateFiller(values)
        return filler.transform(self.template_tree)


def tup(*elems):
    return Tree('tuple', list(elems))

def string(*value: str):
    return Tree('string', [Token('STRING', v) for v in value])