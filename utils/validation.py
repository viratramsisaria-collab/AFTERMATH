
from __future__ import annotations

from collections.abc import Iterable
from numbers import Real
from typing import TypeVar


T = TypeVar("T")


def clamp(
    value: Real,
    minimum: Real,
    maximum: Real,
) -> Real:
    """Restrict a numeric value to a specified range."""

    if isinstance(value, bool) or isinstance(minimum, bool) or isinstance(maximum, bool):
        raise TypeError("Boolean values are not valid numeric inputs.")

    if minimum > maximum:
        raise ValueError("Minimum cannot be greater than maximum.")

    return max(minimum, min(value, maximum))


def validate_range(
    name: str,
    value: Real,
    minimum: Real,
    maximum: Real,
) -> Real:
    """Validate that a numeric value falls within an inclusive range."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a numeric value.")

    if minimum > maximum:
        raise ValueError("Minimum cannot be greater than maximum.")

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum}; received {value}."
        )

    return value


def validate_non_empty(
    value: str,
    name: str = "Value",
) -> str:
    """Validate and return a non-empty string."""

    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(f"{name} cannot be empty.")

    return cleaned


def validate_choice(
    value: T,
    allowed: Iterable[T],
    name: str = "Value",
) -> T:
    """Validate that a value belongs to an allowed collection."""

    allowed_values = tuple(allowed)

    if value not in allowed_values:
        choices = ", ".join(str(item) for item in allowed_values)
        raise ValueError(
            f"Invalid {name}: {value!r}. Allowed values: {choices}."
        )

    return value
