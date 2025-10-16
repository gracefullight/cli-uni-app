from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List

from .subject import Subject
from constants import PASSING_AVERAGE


@dataclass
class Student:
    """Represents a student with ID, name, email, password, and enrolled subjects."""

    student_id: str
    first_name: str
    last_name: str
    email: str
    password: str
    subjects: List[Subject] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "subjects": [s.to_dict() for s in self.subjects],
        }

    @staticmethod
    def generate_id(existing_ids: set[str], length: int = 6) -> str:
        """Generate a unique numeric string ID of given length not present in existing_ids."""
        lower = 10 ** (length - 1)
        upper = (10 ** length) - 1
        while True:
            candidate = str(random.randint(lower, upper))
            if candidate not in existing_ids:
                return candidate

    @staticmethod
    def from_dict(data: Dict) -> "Student":
        return Student(
            student_id=str(data["student_id"]),
            first_name=str(data["first_name"]),
            last_name=str(data["last_name"]),
            email=str(data["email"]),
            password=str(data["password"]),
            subjects=[Subject.from_dict(s) for s in data.get("subjects", [])],
        )

    def average_mark(self) -> float:
        if not self.subjects:
            return 0.0
        return sum(s.mark for s in self.subjects) / len(self.subjects)

    def is_passing(self) -> bool:
        return self.average_mark() >= PASSING_AVERAGE