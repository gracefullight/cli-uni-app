"""Admin service for handling all admin-related business logic."""

from typing import Dict, List, Tuple

from constants import Grades
from models.student import Student
from db import Database


class AdminService:
    """Service for admin operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def list_students(self) -> List[Student]:
        """List all students."""
        return self.db.list_students()

    def remove_student(self, student_id: str) -> Tuple[bool, str]:
        """Remove a student by ID."""
        return self.db.remove_student(student_id)

    def group_by_grade(self) -> Dict[str, List[Student]]:
        """Group students by their dominant grade."""
        students = self.db.list_students()
        groups: Dict[str, List[Student]] = {g: [] for g in Grades.ALL}

        for s in students:
            if not s.subjects:
                continue
            best = max(
                (subj.grade for subj in s.subjects), key=lambda g: Grades.ORDER.get(g, -1)
            )
            groups[best].append(s)
        return groups

    def partition_pass_fail(self) -> Tuple[List[Student], List[Student]]:
        """Partition students into pass/fail groups."""
        students = self.db.list_students()
        passed = [s for s in students if s.is_passing()]
        failed = [s for s in students if not s.is_passing()]
        return passed, failed

    def clear_all_students(self) -> None:
        """Clear all student data."""
        self.db.clear_all_students()
