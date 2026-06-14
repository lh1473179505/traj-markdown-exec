"""Tests for the Markdown converter."""

from __future__ import annotations

import re
from textwrap import dedent
from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element

import pytest
from markdown.extensions.toc import TocExtension

from markdown_exec import MarkdownConfig, markdown_config
from markdown_exec._internal.processors import IdPrependingTreeprocessor

if TYPE_CHECKING:
    from markdown import Markdown


def test_rendering_nested_blocks(md: Markdown) -> None:
    """Assert nested blocks are properly handled.

    Parameters:
        md: A Markdown instance (fixture).
    """
    html = md.convert(
        dedent(
            """
            ````md exec="1"
            ```python exec="1"
            print("**Bold!**")
            ```
            ````
            """,
        ),
    )
    assert html == "<p><strong>Bold!</strong></p>"


def test_instantiating_config_singleton() -> None:
    """Assert that the Markdown config instances act as a singleton."""
    assert MarkdownConfig() is markdown_config
    markdown_config.save([], {})
    markdown_config.reset()


@pytest.mark.parametrize(
    ("id", "id_prefix", "expected"),
    [
        ("", None, 'id="exec-\\d+--heading"'),
        ("", "", 'id="heading"'),
        ("", "some-prefix-", 'id="some-prefix-heading"'),
        ("some-id", None, 'id="some-id-heading"'),
        ("some-id", "", 'id="heading"'),
        ("some-id", "some-prefix-", 'id="some-prefix-heading"'),
    ],
)
def test_prefixing_headings(md: Markdown, id: str, id_prefix: str | None, expected: str) -> None:  # noqa: A002
    """Assert that we prefix headings as specified.

    Parameters:
        md: A Markdown instance (fixture).
        id: The code block id.
        id_prefix: The code block id prefix.
        expected: The id we expect to find in the HTML.
    """
    TocExtension().extendMarkdown(md)
    prefix = f'idprefix="{id_prefix}"' if id_prefix is not None else ""
    html = md.convert(
        dedent(
            f"""
            ```python exec="1" id="{id}" {prefix}
            print("# HEADING")
            ```
            """,
        ),
    )
    assert re.search(expected, html)


def test_id_prepending_compound_href(md: Markdown) -> None:
    """Assert compound hrefs get the prefix only on the fragment part.

    Parameters:
        md: A Markdown instance (fixture).
    """
    root = Element("div")
    # Compound href: path + fragment
    a_compound = Element("a", {"href": "other.md#target"})
    root.append(a_compound)
    # Pure fragment href
    a_fragment = Element("a", {"href": "#section"})
    root.append(a_fragment)
    # Absolute path with fragment
    a_abs = Element("a", {"href": "/docs/foo#heading"})
    root.append(a_abs)
    # No fragment — should be left untouched
    a_plain = Element("a", {"href": "other.md"})
    root.append(a_plain)

    tp = IdPrependingTreeprocessor(md, id_prefix="pfx-")
    tp.run(root)

    assert a_compound.get("href") == "other.md#pfx-target"
    assert a_fragment.get("href") == "#pfx-section"
    assert a_abs.get("href") == "/docs/foo#pfx-heading"
    assert a_plain.get("href") == "other.md"
