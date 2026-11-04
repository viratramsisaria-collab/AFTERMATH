
from __future__ import annotations

import re
import uuid


def create_id(prefix: str | None = None) -> str:
    """Generate a unique hexadecimal identifier, optionally prefixed."""
    identifier = uuid.uuid4().hex

    if prefix:
        clean_prefix = slugify(prefix)
        return f"{clean_prefix}-{identifier}"

    return identifier


def slugify(value: str) -> str:
    """Convert text into a lowercase, URL-friendly identifier."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    return value or "item"
