from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from typing import Dict


def calculate_grade(mark: int) -> str:
    """Return grade string based on mark."""
    if mark >= 85:
        return "HD"  # High Distinction
    if mark >= 75:
        return "D"   # Distinction
    if mark >= 65:
        return "C"   # Credit
    if mark >= 50:
        return "P"   # Pass
    return "F"       # Fail


@dataclass
class Subject:
    """Represents a subject enrollment with an ID, name, mark, and grade."""

    subject_id: str
    name: str
    mark: int
    grade: str

    @staticmethod
    def generate_id(existing_ids: set[str], length: int = 3) -> str:
        """Generate a unique numeric string ID of given length not present in existing_ids."""
        lower = 10 ** (length - 1)
        upper = (10 ** length) - 1
        while True:
            candidate = str(random.randint(lower, upper))
            if candidate not in existing_ids:
                return candidate

    @staticmethod
    def create(name: str, existing_ids: set[str]) -> "Subject":
        """Create a new subject with unique 3-digit ID and random mark."""
        subject_id = Subject.generate_id(existing_ids)
        mark = random.randint(0, 100)
        grade = calculate_grade(mark)
        return Subject(subject_id=subject_id, name=name, mark=mark, grade=grade)

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Subject":
        return Subject(
            subject_id=str(data["subject_id"]),
            name=str(data["name"]),
            mark=int(data["mark"]),
            grade=str(data["grade"]),
        )