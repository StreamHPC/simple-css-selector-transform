"""Simple transformations for CSS Selectors"""

import sys
from importlib import metadata as importlib_metadata

from simple_css_selector_transform.app import app
from simple_css_selector_transform.rewrite import scope_all_rules_bytes


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

__all__ = ["app", "get_version", "scope_all_rules_bytes", "version"]

if __name__ == "main":
    app()  # pragma: no cover
