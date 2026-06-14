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


def test_console_transform_source_prompt_preserved() -> None:
    """Assert the display string uses the last matched prompt, not trailing non-prompt lines.

    When the source contains prompt lines followed by output lines (no $ or %
    prefix), the display text must still be indented with the last successfully
    matched prompt (defaulting to ``$ ``), not with the first two characters of
    the final line.
    """
    from markdown_exec._internal.formatters.console import _transform_source

    # Dollar prompt with a trailing output line whose first two chars are "do".
    code = "$ echo ok\ndone"
    sh_code, display = _transform_source(code)
    assert sh_code == "echo ok"
    assert display == "$ echo ok"

    # Percent prompt with a trailing output line.
    code = "% echo hi\nthere"
    sh_code, display = _transform_source(code)
    assert sh_code == "echo hi"
    assert display == "% echo hi"

    # Multiple prompt lines: last matched prompt wins.
    code = "$ first\n% second\noutput"
    sh_code, display = _transform_source(code)
    assert sh_code == "first\nsecond"
    assert display == "% first\n% second"

    # No prompt lines at all: default "$ " is used.
    code = "plain line"
    sh_code, display = _transform_source(code)
    assert sh_code == ""
    assert display == ""
