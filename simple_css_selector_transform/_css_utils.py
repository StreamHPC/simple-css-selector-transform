from typing import Generator, Iterable, Iterator, List, Optional, Tuple

from tinycss2.ast import Comment, LiteralToken, Node, QualifiedRule, WhitespaceToken

_COMMA_TOKEN = ","

# 1. Child combinator
# 2. Next-sibling combinator
# 3. Subsequent-sibling combinator
# Descendant Combinator is any whitespace
_COMBINATORS = [">", "+", "~"]


def selectors(rule: QualifiedRule) -> Generator[Iterable[Node], None, None]:
    class SimpleSelectors:
        def __init__(self, nodes: List[Node]):
            self._nodes: List[Node] = nodes
            self._continue: int = 0

        def values(self) -> Generator[Node, None, None]:
            for index, node in enumerate(self._nodes[self._continue :]):
                if isinstance(node, LiteralToken) and node.value == _COMMA_TOKEN:
                    # Skip over the comma
                    self._continue += index + 1
                    return
                yield node

            self._continue = len(self._nodes)  # No more tokens

        @property
        def has_more_tokens(self) -> bool:
            return self._continue < len(self._nodes)

    selectors = SimpleSelectors(rule.prelude)
    while selectors.has_more_tokens:
        yield selectors.values()


def find_next_combinator(selector: List[Node]) -> Optional[Tuple[int, bool]]:
    leading_whitespace = False
    for index, node in enumerate(selector):
        if isinstance(node, LiteralToken) and node.value in _COMBINATORS:
            return index, leading_whitespace
        elif isinstance(node, WhitespaceToken):
            leading_whitespace = True
        elif isinstance(node, Comment):
            continue
        # Any other token following a whitespace (i.e. not other combinators) is the end of a descendant combinator
        elif leading_whitespace:
            return index, leading_whitespace
    return None


def find_first_semantic_token(selector: Iterable[Node]) -> Optional[int]:
    for index, node in enumerate(selector):
        if not isinstance(node, (Comment, WhitespaceToken)):
            return index
    return None
