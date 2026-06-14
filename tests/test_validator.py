"""Tests for the `validator` function."""

import pytest
from markdown.core import Markdown

from markdown_exec import validator
from markdown_exec._internal.formatters.base import default_tabs


@pytest.mark.parametrize(
    ("exec_value", "expected"),
    [
        ("yes", True),
        ("YES", True),
        ("on", True),
        ("ON", True),
        ("whynot", True),
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("-1", True),
        ("0", False),
        ("no", False),
        ("NO", False),
        ("off", False),
        ("OFF", False),
        ("false", False),
        ("FALSE", False),
    ],
)
def test_validate(md: Markdown, exec_value: str, expected: bool) -> None:
    """Assert the validator returns True or False given inputs.

    Parameters:
        md: A Markdown instance.
        exec_value: The exec option value, passed from the code block.
        expected: Expected validation result.
    """
    assert validator("whatever", inputs={"exec": exec_value}, options={}, attrs={}, md=md) is expected


@pytest.mark.parametrize(
    ("tabs_input", "expected_tabs"),
    [
        ("OnlySource", ("OnlySource", default_tabs[1])),
        ("A|B", ("A", "B")),
        ("A\\|B|C", ("A\\|B", "C")),
    ],
)
def test_validator_tabs_single_segment_padded(md: Markdown, tabs_input: str, expected_tabs: tuple) -> None:
    """Assert tabs option is always a 2-tuple after validation.

    Parameters:
        md: A Markdown instance.
        tabs_input: The tabs option value, passed from the code block.
        expected_tabs: Expected resulting tabs tuple.
    """
    options: dict = {}
    validator("python", inputs={"exec": "yes", "tabs": tabs_input}, options=options, attrs={}, md=md)
    assert options["tabs"] == expected_tabs
    assert len(options["tabs"]) == 2
