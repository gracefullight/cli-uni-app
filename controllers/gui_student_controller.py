"""GUI Student controller for handling student operations without Console I/O."""

from typing import Optional, Tuple

from models.student import Student
from models.subject import Subject
from services.student_service import StudentService


# Member 4: Responsible for GUI Development
class GUIStudentController:
    """Controller for GUI student operations."""

    def __init__(self, student_service: StudentService) -> None:
        self.student_service = student_service

    def login(self, email: str, password: str) -> Optional[Student]:
        """
        Validate and login student.

        Returns:
            Student if successful, None otherwise
        Raises:
            ValueError with error message if validation fails
        """
        return self.student_service.login(email, password)

    def register(
        self, first_name: str, last_name: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[Student]]:
        """
        Register a new student.

        Returns:
            Tuple of (success, message, student)
        """
        return self.student_service.register(first_name, last_name, email, password)

    def enroll_subject(self, student: Student) -> Tuple[Student, Subject]:
        """
        Enroll student in a new subject.

        Returns:
            Tuple of (updated_student, new_subject)
        Raises:
            ValueError with error message if enrollment fails
        """
        # For the GUI, we use a simplified enroll_subject without a name
        # The service creates a default name.
        return self.student_service.enroll_subject(student)

    def remove_subject(self, student: Student, subject_id: str) -> Student:
        """
        Remove a subject from student's enrollment.

        Returns:
            Updated student
        Raises:
            ValueError with error message if removal fails
        """
        return self.student_service.remove_subject(student, subject_id)

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
        return self.student_service.change_password(
            student, new_password, confirm_password
        )
