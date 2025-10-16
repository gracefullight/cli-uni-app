"""GUI Student controller for handling student operations without Console I/O."""

from typing import Optional, Tuple

from constants import MAX_SUBJECTS_PER_STUDENT
from utils.password import validate_email, validate_password, hash_password, check_password
from models.student import Student
from models.subject import Subject
from db import Database


# Person D: GUI Interface
class GUIStudentController:
    """Controller for GUI student operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

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
            raise ValueError("Invalid email or password format")
        
        student = self.db.get_student_by_email(email.lower())
        if student is None or not check_password(password, student.password):
            raise ValueError("Invalid email or password")
        
        return student

    def enroll_subject(self, student: Student) -> Tuple[Student, Subject]:
        """
        Enroll student in a new subject.
        
        Returns:
            Tuple of (updated_student, new_subject)
        Raises:
            ValueError with error message if enrollment fails
        """
        # Refresh student data from database
        fresh = self.db.get_student_by_id(student.student_id)
        if fresh is None:
            raise ValueError("Student not found in database")
        
        if len(fresh.subjects) >= MAX_SUBJECTS_PER_STUDENT:
            raise ValueError(f"Students are allowed to enroll in {MAX_SUBJECTS_PER_STUDENT} subjects only")
        
        existing_ids = {s.subject_id for s in fresh.subjects}
        subject_name = f"Subject-{len(fresh.subjects) + 1}"
        new_subject = Subject.create(name=subject_name, existing_ids=existing_ids)
        fresh.subjects.append(new_subject)
        
        self.db.update_student(fresh)
        return (fresh, new_subject)

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
                break
        
        if not removed:
            raise ValueError("Subject not found")
        
        self.db.update_student(fresh)
        return fresh

    def change_password(self, student: Student, new_password: str, confirm_password: str) -> Student:
        """
        Change student's password.
        
        Returns:
            Updated student
        Raises:
            ValueError with error message if password change fails
        """
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if not validate_password(new_password):
            raise ValueError("Incorrect password format")
        
        fresh = self.db.get_student_by_id(student.student_id)
        if fresh is None:
            raise ValueError("Student not found in database")
        
        fresh.password = hash_password(new_password)
        self.db.update_student(fresh)
        
        return fresh
