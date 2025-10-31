"""Student controller for handling all student-related operations."""

from typing import Optional
from rich.console import Console

from constants import MAX_SUBJECTS_PER_STUDENT, MAX_LOGIN_ATTEMPTS
from messages import (
    Prompts,
    SuccessMessages,
    ErrorMessages,
    InfoMessages,
    FormatTemplates,
    Colors,
)
from utils.cmd import clear_screen
from models.student import Student
from services.student_service import StudentService
from utils.password import validate_email, validate_password

console = Console()


class StudentController:
    """Controller for student operations: register, login, enrollment, password change."""

    def __init__(self, student_service: StudentService) -> None:
        self.student_service = student_service

    # Member 1: Responsible for Student Registration and Login
    def register(self) -> None:
        """Register a new student: Email/Password → validate → duplicate check → Name → enroll."""
        console.print(f"\t{InfoMessages.STUDENT_SIGN_UP}", style=Colors.SUCCESS)

        while True:
            email = console.input("\tEmail: ").strip().lower()
            password = console.input("\tPassword: ").strip()

            if not validate_email(email) or not validate_password(password):
                console.print("\tIncorrect email or password format", style=Colors.ERROR)
                continue

            console.print("\tEmail and password formats acceptable", style=Colors.WARNING)

            existing = self.student_service.db.get_student_by_email(email)
            if existing is not None:
                console.print(f"\tStudent {existing.first_name} {existing.last_name} already exists.", style=Colors.ERROR)
                return

            break

        full_name = console.input("\tName: ").strip()
        parts = [p for p in full_name.split() if p]
        if len(parts) < 2:
            console.print("\tPlease enter both first and last name (e.g., 'Kevin Anderson').", style=Colors.ERROR)
            return
        first_name, last_name = parts[0], parts[-1]

        console.print(f"\tEnrolling Student {first_name} {last_name}", style=Colors.WARNING)
        
        self.student_service.register(first_name, last_name, email, password)


    # Member 1: Responsible for Student Registration and Login
    def login(self) -> Optional[Student]:
        """Login with email/password, max 3 attempts."""
        console.print(f"\t{InfoMessages.STUDENT_SIGN_IN}", style=Colors.SUCCESS)

        attempts = 0
        while attempts < MAX_LOGIN_ATTEMPTS:
            email = console.input(f"\t{Prompts.LOGIN_EMAIL}").strip().lower()
            password = console.input(f"\t{Prompts.LOGIN_PASSWORD}").strip()
            try:
                student = self.student_service.login(email, password)
                return student
            except ValueError as e:
                console.print(f"\t{str(e)}", style=Colors.ERROR)
                attempts += 1
                continue
        console.print(f"\t{ErrorMessages.TOO_MANY_ATTEMPTS}", style=Colors.ERROR)
        return None

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def view_enrollment(self, student: Student) -> None:
        """Display all enrolled subjects with marks and grades."""
        console.print("\t" +
            InfoMessages.SHOWING_SUBJECTS.format(count=len(student.subjects)),
            style=Colors.WARNING,
        )
        if not student.subjects:
            console.print(f"\t{InfoMessages.NO_SUBJECTS_ENROLLED}", style=Colors.ERROR)
        else:
            for s in student.subjects:
                console.print("\t" +
                    FormatTemplates.SUBJECT_ITEM.format(
                        subject_id=s.subject_id,
                        mark=s.mark,
                        grade=s.grade,
                    )
                )

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def enroll_subject(self, student: Student) -> None:
        """Enroll in a new subject (max 4 limit)."""
        try:
            _student, new_subject = self.student_service.enroll_subject(student)
            console.print("\t" + 
                SuccessMessages.ENROLL.format(
                    subject_id=new_subject.subject_id,
                ),
                style=Colors.WARNING,
            )
            console.print("\t" + 
                SuccessMessages.ENROLL_COUNT.format(
                    count=len(_student.subjects),
                    max_subjects=MAX_SUBJECTS_PER_STUDENT,
                ),
                style=Colors.WARNING,
            )
        except ValueError as e:
            console.print("\t" + str(e), style=Colors.ERROR)

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def remove_subject(self, student: Student) -> None:
        """Remove an enrolled subject."""
        if not student.subjects:
            console.print(f"\t{ErrorMessages.NO_SUBJECTS_TO_REMOVE}", style=Colors.ERROR)
            return

        subject_id = console.input(f"\t{Prompts.SUBJECT_ID_TO_REMOVE}").strip()
        try:
            updated_student = self.student_service.remove_subject(student, subject_id)
            console.print("\t" +
                SuccessMessages.REMOVE_SUBJECT.format(subject_id=subject_id),
                style=Colors.WARNING,
            )
            console.print("\t" +
                SuccessMessages.ENROLL_COUNT.format(
                    count=len(updated_student.subjects),
                    max_subjects=MAX_SUBJECTS_PER_STUDENT,
                ),
                style=Colors.WARNING,
            )
        except ValueError as e:
            console.print(f"\t{str(e)}", style=Colors.ERROR)

    # Member 1: Responsible for Student Registration and Login
    def change_password(self, student: Student) -> None:
        """Change student password with validation."""
        console.print(f"\t{InfoMessages.UPDATING_PASSWORD}", style=Colors.WARNING)
        new_password = console.input(f"\t{Prompts.NEW_PASSWORD}", password=True).strip()
        confirm_password = console.input(f"\t{Prompts.CONFIRM_PASSWORD}", password=True).strip()
        try:
            self.student_service.change_password(student, new_password, confirm_password)
        except ValueError as e:
            console.print(f"\t{str(e)}", style=Colors.ERROR)
