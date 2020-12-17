from dataclasses import dataclass
from io import StringIO
from textwrap import indent
from token import NEWLINE, INDENT, DEDENT, NL, tok_name, LBRACE, RBRACE, LPAR, RPAR, LSQB, RSQB, OP, COMMENT
from tokenize import generate_tokens, TokenInfo, untokenize
from typing import List, Union, TextIO, Iterable


@dataclass
class Paren:
    open: TokenInfo
    expr: List[Union['Paren', TokenInfo]]
    close: TokenInfo

    def formatted_repr(self) -> str:
        expr = ', '.join(tok_name[e.type] if isinstance(e, TokenInfo) else e.formatted_repr() for e in self.expr)
        return f"<{self.open.string}>{expr}<{self.close.string}>"

    def as_token_stream(self) -> Iterable[TokenInfo]:
        yield self.open
        for e in self.expr:
            if isinstance(e, (TokenInfo, tuple)):
                yield e
            else:
                yield from e.as_token_stream()
        yield self.close

    def unparse(self):
        return untokenize(self.as_token_stream())


@dataclass
class Statement:
    expr: List[Union[Paren, TokenInfo]]
    children: List['Statement'] = None

    def formatted_repr(self) -> str:
        expr = ', '.join(tok_name[e.type] if isinstance(e, TokenInfo) else e.formatted_repr() for e in self.expr)
        if self.children is None:
            return f"{type(self).__name__}([{expr}])"
        else:
            body = indent(',\n'.join(s.formatted_repr() for s in self.children), '  ')
            return f"{type(self).__name__}([{expr}], [\n{body}\n])"

    def as_token_stream(self, indent_stack: List[str]) -> Iterable[TokenInfo]:
        for e in self.expr:
            if isinstance(e, (TokenInfo, tuple)):
                yield e
            else:
                yield from e.as_token_stream()
        yield NEWLINE, '\n'
        if self.children is not None:
            indent_stack.append(indent_stack[-1] + '    ')
            yield INDENT, indent_stack[-1]
            for c in self.children:
                yield from c.as_token_stream(indent_stack)
            yield DEDENT, ''
            indent_stack.pop()

    def unparse(self):
        return untokenize(self.as_token_stream(['']))


@dataclass
class Module:
    stmts: List[Statement]

    def formatted_repr(self) -> str:
        body = indent(',\n'.join(s.formatted_repr() for s in self.stmts), '  ')
        return f"{type(self).__name__}([\n{body}\n])"

    def as_token_stream(self, indent_stack: List[str]) -> Iterable[TokenInfo]:
        for s in self.stmts:
            yield from s.as_token_stream(indent_stack)

    def unparse(self):
        return untokenize(self.as_token_stream(['']))


def parse(inp: Union[str, TextIO]) -> Module:
    if isinstance(inp, str):
        inp = StringIO(inp)
    stmt_stack: List[List[Statement]] = [[]]
    expr_stack: List[List[Union[Paren, TokenInfo]]] = [[]]
    for t in generate_tokens(inp.readline):
        if t.type == NEWLINE:
            assert len(expr_stack) == 1
            assert len(expr_stack[0]) != 0
            stmt_stack[-1].append(Statement(expr_stack[0]))
            expr_stack = [[]]
        elif t.type == INDENT:
            assert len(expr_stack) == 1
            assert len(expr_stack[0]) == 0
            stmt_stack.append([])
        elif t.type == DEDENT:
            assert len(expr_stack) == 1
            assert len(expr_stack[0]) == 0, expr_stack
            c = stmt_stack.pop()
            assert stmt_stack[-1][-1].children is None
            stmt_stack[-1][-1].children = c
        elif t.type in (NL, COMMENT):
            continue
        elif t.type == OP and t.exact_type in (LBRACE, LPAR, LSQB):
            expr_stack.append([t])
        elif t.type == OP and t.exact_type in (RBRACE, RPAR, RSQB):
            o, *e = expr_stack.pop()
            expr_stack[-1].append(Paren(o, list(e), t))
        else:
            expr_stack[-1].append(t)
    return Module(stmt_stack[0])

# print(parse(open(__file__)).formatted_repr())
