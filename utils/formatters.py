
from __future__ import annotations


def format_number(value: int | float, decimals: int = 0) -> str:
    """Format a number with thousands separators."""
    return f"{value:,.{decimals}f}"


def format_currency(
    value: int | float,
    symbol: str = "$",
    decimals: int = 0,
) -> str:
    """Format a monetary value."""
    return f"{symbol}{format_number(value, decimals)}"


def format_percentage(value: int | float, decimals: int = 1) -> str:
    """Format a percentage value already expressed on a 0–100 scale."""
    return f"{format_number(value, decimals)}%"


def format_metric(
    value: int | float,
    suffix: str = "",
    decimals: int = 1,
) -> str:
    """Format a metric with an optional suffix."""
    formatted = format_number(value, decimals)
    return f"{formatted}{suffix}"


def format_population(value: int) -> str:
    """Format a population count."""
    return format_number(value)
