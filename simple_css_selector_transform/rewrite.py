from typing import Iterable, List, Optional, Union

import functools

import webencodings
from tinycss2 import parse_rule_list, parse_stylesheet_bytes, serialize
from tinycss2.ast import (
    AtRule,
    Comment,
    IdentToken,
    LiteralToken,
    Node,
    ParseError,
    QualifiedRule,
    WhitespaceToken,
)

import simple_css_selector_transform._css_utils as css_utils


def scope_all_rules_bytes(css: bytes, classname: str, *, filename: Optional[str] = None) -> bytes:
    rules: List[TopLevel]
    rules, encoding = parse_stylesheet_bytes(css)
    filename = filename or "<unknown-file>"
    result: bytes = webencodings.encode(
        serialize(_rewrite_all_toplevels(rules, classname, filename)), encoding
    )
    return result


__all__ = ["scope_all_rules_bytes"]

TopLevel = Union[AtRule, Comment, ParseError, QualifiedRule, WhitespaceToken]

_HTML_ELEMENT = "html"
_BODY_ELEMENT = "body"
_CLASS_SELECTOR = "."
_SPACE = LiteralToken(line=None, column=None, value=" ")

"""@ rules that have nested CSS within them and need to be recursed into like @media"""
_NESTING_AT_RULES = ["media", "supports", "layer"]


def _literal(value: str) -> LiteralToken:
    return LiteralToken(line=None, column=None, value=value)


def _ident(value: str) -> IdentToken:
    return IdentToken(line=None, column=None, value=value)


def _comment(value: str) -> Comment:
    return Comment(line=None, column=None, value=value)


def _rewrite_html_selector(selector: List[Node], classname: str) -> List[Node]:
    result = css_utils.find_next_combinator(selector)
    if result is not None:
        combinator_index, leading_whitespace = result
        to_insert = [_literal(_CLASS_SELECTOR), _ident(classname), _SPACE]
        if not leading_whitespace:
            to_insert.insert(0, _SPACE)
        return selector[:combinator_index] + to_insert + selector[combinator_index:]
    return selector


def _rewrite_basic_selector(selector: List[Node], classname: str) -> List[Node]:
    return [_literal(_CLASS_SELECTOR), _ident(classname), _SPACE] + selector


def _rewrite_body_selector(selector: List[Node], classname: str) -> List[Node]:
    # Replace the body tag with a class selector '.<classname>'
    return [_literal(_CLASS_SELECTOR), _ident(classname)] + selector[1:]


def _rewrite_selector(selector: List[Node], classname: str) -> List[Node]:
    tail_index = css_utils.find_first_semantic_token(selector)
    if tail_index is None:
        return selector

    head: List[Node] = selector[:tail_index]
    tail: List[Node] = selector[tail_index:]
    if isinstance(tail[0], IdentToken):
        if tail[0].lower_value == _HTML_ELEMENT:
            return head + _rewrite_html_selector(tail, classname)
        elif tail[0].lower_value == _BODY_ELEMENT:
            return head + _rewrite_body_selector(tail, classname)
    return head + _rewrite_basic_selector(tail, classname)


def _append_to_selector_group(a: Iterable[Node], b: Iterable[Node]) -> List[Node]:
    return list(a) + [_literal(css_utils._COMMA_TOKEN)] + list(b)


def _scope_qualified_rule(rule: QualifiedRule, classname: str) -> QualifiedRule:
    # Convert each item to a real list
    selectors_list: Iterable[List[Node]] = map(list, css_utils.selectors(rule))
    # Rewrite each selector in the selector group
    rewrite_selector = functools.partial(_rewrite_selector, classname=classname)
    rewritten_selectors = list(map(rewrite_selector, selectors_list))
    # Then join it back up into a single selector_group
    if len(rewritten_selectors) > 0:
        rule.prelude = functools.reduce(_append_to_selector_group, rewritten_selectors)
    return rule


def _rewrite_toplevel(rule: TopLevel, classname: str, filename: str) -> TopLevel:
    if isinstance(rule, QualifiedRule):
        return _scope_qualified_rule(rule, classname)
    if isinstance(rule, AtRule):
        if rule.lower_at_keyword in _NESTING_AT_RULES and rule.content is not None:
            rules: List[TopLevel] = parse_rule_list(rule.content)
            rule.content = _rewrite_all_toplevels(rules, classname, filename)
    if isinstance(rule, ParseError):
        return _comment(
            f"<parse-error> at {filename:s}:{rule.source_line:d}:{rule.source_column:d}"
        )
    return rule


def _rewrite_all_toplevels(
    rules: Iterable[TopLevel], classname: str, filename: str
) -> Iterable[TopLevel]:
    return map(functools.partial(_rewrite_toplevel, classname=classname, filename=filename), rules)
