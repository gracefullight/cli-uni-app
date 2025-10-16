"""Password and email validation and hashing utilities."""

import re
import bcrypt


# Person A: Authentication
def validate_email(email: str) -> bool:
    """Validate email format: firstname.lastname@university.com"""
    pattern = r"^[a-z]+\.[a-z]+@university\.com$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password: starts with uppercase, 5+ letters total, ending with 3 digits."""
    pattern = r"^[A-Z][A-Za-z]{4,}\d{3}$"
    return re.match(pattern, password) is not None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Check a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
