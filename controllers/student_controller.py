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

console = Console()


class StudentController:
    """Controller for student operations: register, login, enrollment, password change."""

    def __init__(self, student_service: StudentService) -> None:
        self.student_service = student_service

    # Member 1: Responsible for Student Registration and Login
    def register(self) -> None:
        """Register a new student with email/password validation."""
        clear_screen()
        console.print(InfoMessages.STUDENT_SIGN_UP, style=Colors.SUCCESS)
        first_name = console.input(Prompts.FIRST_NAME).strip()
        last_name = console.input(Prompts.LAST_NAME).strip()
        email = console.input(Prompts.EMAIL).strip().lower()
        password = console.input(Prompts.PASSWORD, password=True).strip()

        try:
            ok, msg, _student = self.student_service.register(
                first_name, last_name, email, password
            )
            if not ok:
                console.print(msg, style=Colors.ERROR)
            else:
                console.print(msg)
        except ValueError as e:
            console.print(str(e), style=Colors.ERROR)

    # Member 1: Responsible for Student Registration and Login
    def login(self) -> Optional[Student]:
        """Login with email/password, max 3 attempts."""
        clear_screen()
        console.print(InfoMessages.STUDENT_SIGN_IN, style=Colors.SUCCESS)

        attempts = 0
        while attempts < MAX_LOGIN_ATTEMPTS:
            email = console.input(Prompts.LOGIN_EMAIL).strip().lower()
            password = console.input(Prompts.LOGIN_PASSWORD, password=True).strip()
            try:
                student = self.student_service.login(email, password)
                return student
            except ValueError as e:
                console.print(str(e), style=Colors.ERROR)
                attempts += 1
                continue
        console.print(ErrorMessages.TOO_MANY_ATTEMPTS, style=Colors.ERROR)
        return None

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def view_enrollment(self, student: Student) -> None:
        """Display all enrolled subjects with marks and grades."""
        clear_screen()
        console.print(
            InfoMessages.SHOWING_SUBJECTS.format(count=len(student.subjects)),
            style=Colors.WARNING,
        )
        if not student.subjects:
            console.print(InfoMessages.NO_SUBJECTS_ENROLLED)
        else:
            for s in student.subjects:
                console.print(
                    FormatTemplates.SUBJECT_ITEM.format(
                        subject_id=s.subject_id,
                        name=s.name,
                        mark=s.mark,
                        grade=s.grade,
                    )
                )
            avg = student.average_mark()
            status = (
                InfoMessages.STATUS_PASS if student.is_passing() else InfoMessages.STATUS_FAIL
            )
            console.print(InfoMessages.AVERAGE_STATUS.format(average=avg, status=status))

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def enroll_subject(self, student: Student) -> None:
        """Enroll in a new subject (max 4 limit)."""
        clear_screen()
        console.print(InfoMessages.ENROLL_IN_SUBJECT, style=Colors.WARNING)
        name = console.input(Prompts.SUBJECT_NAME).strip()
        if not name:
            console.print(ErrorMessages.SUBJECT_NAME_EMPTY, style=Colors.ERROR)
            return

        try:
            _student, new_subject = self.student_service.enroll_subject(student, name)
            console.print(
                SuccessMessages.ENROLL.format(
                    subject_name=new_subject.name,
                    subject_id=new_subject.subject_id,
                    mark=new_subject.mark,
                    grade=new_subject.grade,
                )
            )
            console.print(
                SuccessMessages.ENROLL_COUNT.format(
                    count=len(_student.subjects),
                    max_subjects=MAX_SUBJECTS_PER_STUDENT,
                ),
                style=Colors.WARNING,
            )
        except ValueError as e:
            console.print(str(e), style=Colors.ERROR)

    # Member 2: Responsible for Subject Enrollment and Grade Calculation
    def remove_subject(self, student: Student) -> None:
        """Remove an enrolled subject."""
        clear_screen()
        if not student.subjects:
            console.print(ErrorMessages.NO_SUBJECTS_TO_REMOVE, style=Colors.ERROR)
            return
        for s in student.subjects:
            console.print(
                FormatTemplates.SUBJECT_LIST_ITEM.format(
                    subject_id=s.subject_id, name=s.name
                )
            )
        subject_id = console.input(Prompts.SUBJECT_ID_TO_REMOVE).strip()
        try:
            updated_student = self.student_service.remove_subject(student, subject_id)
            console.print(
                SuccessMessages.REMOVE_SUBJECT.format(subject_id=subject_id),
                style=Colors.WARNING,
            )
            console.print(
                SuccessMessages.ENROLL_COUNT.format(
                    count=len(updated_student.subjects),
                    max_subjects=MAX_SUBJECTS_PER_STUDENT,
                ),
                style=Colors.WARNING,
            )
        except ValueError as e:
            console.print(str(e), style=Colors.ERROR)

    # Member 1: Responsible for Student Registration and Login
    def change_password(self, student: Student) -> None:
        """Change student password with validation."""
        clear_screen()
        console.print(InfoMessages.UPDATING_PASSWORD, style=Colors.WARNING)
        new_password = console.input(Prompts.NEW_PASSWORD, password=True).strip()
        confirm_password = console.input(Prompts.CONFIRM_PASSWORD, password=True).strip()
        try:
            self.student_service.change_password(student, new_password, confirm_password)
            console.print(SuccessMessages.PASSWORD_CHANGED, style=Colors.SUCCESS)
        except ValueError as e:
            console.print(str(e), style=Colors.ERROR)
