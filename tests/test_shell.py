"""Tests for the shell formatters."""

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest
    from markdown import Markdown


def test_output_markdown(md: Markdown) -> None:
    """Assert Markdown is converted to HTML.

    Parameters:
        md: A Markdown instance (fixture).
    """
    html = md.convert(
        dedent(
            """
            ```sh exec="yes"
            echo "**Bold!**"
            ```
            """,
        ),
    )
    assert html == "<p><strong>Bold!</strong></p>"


def test_output_html(md: Markdown) -> None:
    """Assert HTML is injected as is.

    Parameters:
        md: A Markdown instance (fixture).
    """
    html = md.convert(
        dedent(
            """
            ```sh exec="yes" html="yes"
            echo "**Bold!**"
            ```
            """,
        ),
    )
    assert html == "<p>**Bold!**\n</p>"


def test_error_raised(md: Markdown, caplog: pytest.LogCaptureFixture) -> None:
    """Assert errors properly log a warning and return a formatted traceback.

    Parameters:
        md: A Markdown instance (fixture).
        caplog: Pytest fixture to capture logs.
    """
    html = md.convert(
        dedent(
            """
            ```sh exec="yes"
            echo("wrong syntax")
            ```
            """,
        ),
    )
    assert "error" in html
    assert "Execution of sh code block exited with unexpected code 2" in caplog.text


def test_console_transform_source_prompt_preserved() -> None:
    """Assert the display string uses the last matched prompt, not the last line's prefix."""
    from markdown_exec._internal.formatters.console import _transform_source

    # Dollar prompt followed by a non-prompt output line.
    code_dollar = "$ echo ok\ndone"
    _, display_dollar = _transform_source(code_dollar)
    assert display_dollar == "$ echo ok"

    # Percent prompt followed by a non-prompt output line.
    code_percent = "% echo ok\ndone"
    _, display_percent = _transform_source(code_percent)
    assert display_percent == "% echo ok"

    # Multiple prompt lines followed by a non-prompt line.
    code_multi = "$ echo hello\n$ echo world\nsome output"
    _, display_multi = _transform_source(code_multi)
    for line in display_multi.split("\n"):
        assert line.startswith("$ ")


def test_return_code(md: Markdown, caplog: pytest.LogCaptureFixture) -> None:
    """Assert return code is used correctly.

    Parameters:
        md: A Markdown instance (fixture).
        caplog: Pytest fixture to capture logs.
    """
    html = md.convert(
        dedent(
            """
            ```sh exec="yes" returncode="1"
            echo Not in the mood
            exit 1
            ```
            """,
        ),
    )
    assert "Not in the mood" in html
    assert "exited with" not in caplog.text
