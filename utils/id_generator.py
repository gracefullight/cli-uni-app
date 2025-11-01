"""ID generation utility for Student and Subject models."""

import random


def generate_unique_id(existing_ids: set[str], length: int) -> str:
    """Generate a unique numeric string ID of given length not present in existing_ids."""
    lower = 10 ** (length - 1)
    upper = (10 ** length) - 1
    while True:
        candidate = str(random.randint(lower, upper))
        if candidate not in existing_ids:
            return candidate