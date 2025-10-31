"""Student service for handling all student-related business logic."""

from typing import Optional, Tuple

from constants import MAX_SUBJECTS_PER_STUDENT
from utils.password import (
    validate_email,
    validate_password,
    hash_password,
    check_password,
)
from models.student import Student
from models.subject import Subject
from db import Database
from rich.console import Console

console = Console()


class StudentService:
    """Service for student operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # Member 1: Responsible for Student Registration and Login
    def register(
        self, first_name: str, last_name: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[Student]]:
        """Register a new student with email/password validation."""
        if not validate_email(email):
            return False, "Incorrect email or password format", None
        if not validate_password(password):
            return False, "Incorrect email or password format", None

        try:
            fname_part, lname_part = email.split("@")[0].split(".")
        except ValueError:
            return False, "Invalid email components", None

        if fname_part != first_name.lower() or lname_part != last_name.lower():
            return False, "Email and name do not match", None

        return self.db.add_student(first_name, last_name, email, password)

    # Member 1: Responsible for Student Registration and Login
    def login(self, email: str, password: str) -> Optional[Student]:
        """
        Validate and login student.

        Returns:
            Student if successful, None otherwise
        Raises:
            ValueError with error message if validation fails
        """
        if not email or not password:
            raise ValueError("Email and password are required")

        if not validate_email(email) or not validate_password(password):
            raise ValueError("Incorrect email or password format")

        console.print("\tEmail and password formats acceptable.", style="yellow")
    
        student = self.db.get_student_by_email(email.lower())
        if student is None:
            raise ValueError("Student does not exist.")

        if not check_password(password, student.password):
            raise ValueError("Incorrect email or password format")

        return student

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def enroll_subject(
        self, student: Student
    ) -> Tuple[Student, Subject]:
        """
        Enroll student in a new subject.

        Returns:
            Tuple of (updated_student, new_subject)
        Raises:
            ValueError with error message if enrollment fails
        """
        fresh = self.db.get_student_by_id(student.student_id)
        if fresh is None:
            raise ValueError("Student not found in database")

        if len(fresh.subjects) >= MAX_SUBJECTS_PER_STUDENT:
            raise ValueError(
                f"Students can enroll in {MAX_SUBJECTS_PER_STUDENT} subjects only"
            )
        existing_ids = {s.subject_id for s in fresh.subjects}
        new_subject = Subject.create(existing_ids=existing_ids)
        fresh.subjects.append(new_subject)

        self.db.update_student(fresh)
        student.subjects = fresh.subjects

        return (fresh, new_subject)

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def remove_subject(self, student: Student, subject_id: str) -> Student:
        """
        Remove a subject from student's enrollment.

        Returns:
            Updated student
        Raises:
            ValueError with error message if removal fails
        """
        if not subject_id:
            raise ValueError("Please select a subject to remove")

        fresh = self.db.get_student_by_id(student.student_id)
        if fresh is None:
            raise ValueError("Student not found in database")

        removed = False
        for idx, s in enumerate(fresh.subjects):
            if s.subject_id == subject_id:
                del fresh.subjects[idx]
                removed = True

        if not removed:
            raise ValueError("Subject not found")

        self.db.update_student(fresh)
        student.subjects = fresh.subjects

        return fresh

    # Member 1: Responsible for Student Registration and Login
    def change_password(
        self, student: Student, new_password: str, confirm_password: str
    ) -> Student:
        """
        Change student's password.

        Returns:
            Updated student
        Raises:
            ValueError with error message if password change fails
        """
        if new_password != confirm_password:
            raise ValueError("Passwords do not match - try again.")

        if not validate_password(new_password):
            raise ValueError("Incorrect password format")

        fresh = self.db.get_student_by_id(student.student_id)
        if fresh is None:
            raise ValueError("Student not found in database")

        fresh.password = hash_password(new_password)
        self.db.update_student(fresh)
        student.password = fresh.password

        return fresh
