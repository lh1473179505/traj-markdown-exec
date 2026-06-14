"""Tests for the `validator` function."""

import logging

import pytest
from markdown.core import Markdown

from markdown_exec import validator


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


def test_validator_invalid_int_options(md: Markdown, caplog: pytest.LogCaptureFixture) -> None:
    """Assert invalid int options fall back to 0 with a warning instead of raising."""
    # returncode=abc should fall back to 0 and log a warning
    options: dict = {}
    with caplog.at_level(logging.WARNING):
        result = validator("python", inputs={"exec": "yes", "returncode": "abc"}, options=options, attrs={}, md=md)
    assert result is True
    assert options["returncode"] == 0
    assert any("invalid returncode" in record.message for record in caplog.records)

    # width=bad should fall back to 0 and log a warning
    caplog.clear()
    options = {}
    with caplog.at_level(logging.WARNING):
        result = validator("python", inputs={"exec": "yes", "width": "bad"}, options=options, attrs={}, md=md)
    assert result is True
    assert options["width"] == 0
    assert any("invalid width" in record.message for record in caplog.records)

    # valid returncode=2 should still parse correctly
    options = {}
    result = validator("python", inputs={"exec": "yes", "returncode": "2"}, options=options, attrs={}, md=md)
    assert result is True
    assert options["returncode"] == 2
