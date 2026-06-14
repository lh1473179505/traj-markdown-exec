"""Tests for the Markdown converter."""

from __future__ import annotations

import re
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from markdown.extensions.toc import TocExtension

from markdown_exec import MarkdownConfig, markdown_config

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
    """Assert that compound hrefs (path#fragment) have only their fragment prefixed.

    Parameters:
        md: A Markdown instance (fixture).
    """
    from xml.etree.ElementTree import Element

    from markdown_exec._internal.processors import IdPrependingTreeprocessor

    prefix = "my-prefix-"
    processor = IdPrependingTreeprocessor(md, prefix)

    root = Element("div")

    # Compound href: path + fragment
    compound_link = Element("a", {"href": "other.md#target"})
    root.append(compound_link)

    # Pure fragment href (regression check)
    pure_link = Element("a", {"href": "#section"})
    root.append(pure_link)

    # Href without fragment (should be untouched)
    no_frag_link = Element("a", {"href": "https://example.com"})
    root.append(no_frag_link)

    processor.run(root)

    # Compound href: path preserved, fragment prefixed
    assert compound_link.get("href") == "other.md#my-prefix-target"
    # Pure fragment href: existing behavior preserved
    assert pure_link.get("href") == "#my-prefix-section"
    # No fragment: untouched
    assert no_frag_link.get("href") == "https://example.com"
