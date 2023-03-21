from typing import Dict

import pytest

import simple_css_selector_transform as css_transform


@pytest.mark.parametrize(
    "input_stylsheet,expected",
    [
        [b"table {width: auto}", b".class table {width: auto}"],
        [b"table.a:not(.table):hower {}", b".class table.a:not(.table):hower {}"],
        [b"table td {}", b".class table td {}"],
    ],
)
def test_basic(input_stylsheet: bytes, expected: bytes) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


@pytest.mark.parametrize(
    "input_stylsheet,expected",
    [
        [b"{}", b"{}"],
        [b"table td, div * {width: auto}", b".class table td, .class div * {width: auto}"],
        [
            b"div, div + div, div > div ~ div {}",
            b".class div, .class div + div, .class div > div ~ div {}",
        ],
    ],
)
def test_multiple(input_stylsheet: bytes, expected: bytes) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


@pytest.mark.parametrize(
    "input_stylsheet,expected",
    [
        [b"/**/ /**//**/ a {}", b"/**/ /**//**/ .class a {}"],
        [b"b/**/a {}", b".class b/**/a {}"],
        [b"a,/**/b {}", b".class a,/**/.class b {}"],
        [b"a,/**/ /**/b {}", b".class a,/**/ /**/.class b {}"],
    ],
)
def test_comments(input_stylsheet: bytes, expected: bytes) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


@pytest.mark.parametrize(
    "input_stylsheet,expected",
    [
        [b"html.a{}", b"html.a{}"],
        [b"/* comment */html{}", b"/* comment */html{}"],
        [b"div html.a{}", b".class div html.a{}"],
        [b"html *{}", b"html .class *{}"],
        [b"html > asd{}", b"html .class > asd{}"],
        [b"html /**/ /**/+ #id{}", b"html /**/ /**/.class + #id{}"],
        [b"html>*{}", b"html .class >*{}"],
    ],
)
def test_root_types(input_stylsheet: bytes, expected: bytes) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


@pytest.mark.parametrize(
    "input_stylsheet,expected",
    [
        [b"body.a{}", b".class.a{}"],
        [b"   /*comment*/   body{}", b"   /*comment*/   .class{}"],
        [b"div body{}", b".class div body{}"],
    ],
)
def test_body_type(input_stylsheet: bytes, expected: bytes) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


def test_nested_rules() -> None:
    input_stylsheet = b"@media print { .div {} }"
    expected = b"@media print { .class .div {} }"
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


def test_ignored_at_rules() -> None:
    input_stylsheet = b'@import url("style.css");'
    expected = b'@import url("style.css");'
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class")
    assert output == expected


@pytest.mark.parametrize(
    "input_stylsheet,expected,kwargs",
    [
        [b"asd,", b"/*<parse-error> at file:1:4*/", {"filename": "file"}],
        [
            b"asd{}\n/*   */bsd,,",
            b".class asd{}\n/*   *//*<parse-error> at <unknown-file>:2:12*/",
            {},
        ],
        [b"{} asd{}", b"{} .class asd{}", {}],
        [b"html +   {}", b"html .class +   {}", {}],
        [
            b",,,{}",
            b",,{}",
            {},
        ],  # The last empty group is removed as it has no semantic meaning (it could be preserved but it is how it is)
    ],
)
def test_invalid(input_stylsheet: bytes, expected: bytes, kwargs: Dict[str, str]) -> None:
    output = css_transform.scope_all_rules_bytes(input_stylsheet, "class", **kwargs)
    assert output == expected
