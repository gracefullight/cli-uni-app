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
from utils.password import validate_email, validate_password, hash_password, check_password
from models.student import Student
from models.subject import Subject
from db import Database

console = Console()


# Person C: CLI Interface
class StudentController:
    """Controller for student operations: register, login, enrollment, password change."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def register(self) -> None:
        """Register a new student with email/password validation."""
        clear_screen()
        console.print(InfoMessages.STUDENT_SIGN_UP, style=Colors.SUCCESS)
        first_name = console.input(Prompts.FIRST_NAME).strip()
        last_name = console.input(Prompts.LAST_NAME).strip()
        email = console.input(Prompts.EMAIL).strip().lower()
        password = console.input(Prompts.PASSWORD, password=True).strip()

        if not validate_email(email):
            console.print(ErrorMessages.INVALID_EMAIL_FORMAT, style=Colors.ERROR)
            return
        if not validate_password(password):
            console.print(ErrorMessages.INVALID_PASSWORD_FORMAT, style=Colors.ERROR)
            return
        try:
            fname_part, lname_part = email.split("@")[0].split(".")
        except ValueError:
            console.print(ErrorMessages.INVALID_EMAIL_COMPONENTS, style=Colors.ERROR)
            return
        if fname_part != first_name.lower() or lname_part != last_name.lower():
            console.print(ErrorMessages.EMAIL_NAME_MISMATCH, style=Colors.ERROR)
            return

        ok, msg, _student = self.db.add_student(first_name, last_name, email, password)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style=Colors.ERROR)
        else:
            console.print(msg)

    def login(self) -> Optional[Student]:
        """Login with email/password, max 3 attempts."""
        clear_screen()
        console.print(InfoMessages.STUDENT_SIGN_IN, style=Colors.SUCCESS)

        attempts = 0
        while attempts < MAX_LOGIN_ATTEMPTS:
            email = console.input(Prompts.LOGIN_EMAIL).strip().lower()
            password = console.input(Prompts.LOGIN_PASSWORD, password=True).strip()
            if not validate_email(email) or not validate_password(password):
                console.print(ErrorMessages.INCORRECT_FORMAT, style=Colors.ERROR)
                attempts += 1
                continue
            student = self.db.get_student_by_email(email)
            if not student or not check_password(password, student.password):
                console.print(ErrorMessages.INVALID_CREDENTIALS, style=Colors.ERROR)
                return None
            return student
        console.print(ErrorMessages.TOO_MANY_ATTEMPTS, style=Colors.ERROR)
        return None

    def view_enrollment(self, student: Student) -> None:
        """Display all enrolled subjects with marks and grades."""
        clear_screen()
        console.print(InfoMessages.SHOWING_SUBJECTS.format(count=len(student.subjects)), style=Colors.WARNING)
        if not student.subjects:
            console.print(InfoMessages.NO_SUBJECTS_ENROLLED)
        else:
            for s in student.subjects:
                console.print(FormatTemplates.SUBJECT_ITEM.format(
                    subject_id=s.subject_id,
                    name=s.name,
                    mark=s.mark,
                    grade=s.grade
                ))
            avg = student.average_mark()
            status = InfoMessages.STATUS_PASS if student.is_passing() else InfoMessages.STATUS_FAIL
            console.print(InfoMessages.AVERAGE_STATUS.format(average=avg, status=status))

    def enroll_subject(self, student: Student) -> None:
        """Enroll in a new subject (max 4 limit)."""
        clear_screen()
        console.print(InfoMessages.ENROLL_IN_SUBJECT, style=Colors.WARNING)
        if len(student.subjects) >= MAX_SUBJECTS_PER_STUDENT:
            console.print(ErrorMessages.SUBJECT_LIMIT_REACHED.format(max_subjects=MAX_SUBJECTS_PER_STUDENT), style=Colors.ERROR)
            return
        name = console.input(Prompts.SUBJECT_NAME).strip()
        if not name:
            console.print(ErrorMessages.SUBJECT_NAME_EMPTY, style=Colors.ERROR)
            return
        if any(s.name.lower() == name.lower() for s in student.subjects):
            console.print(ErrorMessages.SUBJECT_ALREADY_ENROLLED, style=Colors.ERROR)
            return
        existing_ids = {s.subject_id for s in student.subjects}
        subject = Subject.create(name=name, existing_ids=existing_ids)
        student.subjects.append(subject)
        self.db.update_student(student)
        console.print(SuccessMessages.ENROLL.format(
            subject_name=subject.name,
            subject_id=subject.subject_id,
            mark=subject.mark,
            grade=subject.grade
        ))
        console.print(SuccessMessages.ENROLL_COUNT.format(
            count=len(student.subjects),
            max_subjects=MAX_SUBJECTS_PER_STUDENT
        ), style=Colors.WARNING)

    def remove_subject(self, student: Student) -> None:
        """Remove an enrolled subject."""
        clear_screen()
        if not student.subjects:
            console.print(ErrorMessages.NO_SUBJECTS_TO_REMOVE, style=Colors.ERROR)
            return
        for s in student.subjects:
            console.print(FormatTemplates.SUBJECT_LIST_ITEM.format(subject_id=s.subject_id, name=s.name))
        subject_id = console.input(Prompts.SUBJECT_ID_TO_REMOVE).strip()
        for idx, s in enumerate(student.subjects):
            if s.subject_id == subject_id:
                console.print(SuccessMessages.REMOVE_SUBJECT.format(subject_id=s.subject_id), style=Colors.WARNING)
                del student.subjects[idx]
                self.db.update_student(student)
                console.print(SuccessMessages.ENROLL_COUNT.format(
                    count=len(student.subjects),
                    max_subjects=MAX_SUBJECTS_PER_STUDENT
                ), style=Colors.WARNING)
                return
        console.print(ErrorMessages.SUBJECT_NOT_FOUND, style=Colors.ERROR)

    def change_password(self, student: Student) -> None:
        """Change student password with validation."""
        clear_screen()
        console.print(InfoMessages.UPDATING_PASSWORD, style=Colors.WARNING)
        new_password = console.input(Prompts.NEW_PASSWORD, password=True).strip()
        if not validate_password(new_password):
            console.print(ErrorMessages.INVALID_PASSWORD_FORMAT, style=Colors.ERROR)
            return
        confirm_password = console.input(Prompts.CONFIRM_PASSWORD, password=True).strip()
        if new_password != confirm_password:
            console.print(ErrorMessages.PASSWORD_MISMATCH, style=Colors.ERROR)
            return

        student.password = hash_password(new_password)
        self.db.update_student(student)
        console.print(SuccessMessages.PASSWORD_CHANGED, style=Colors.SUCCESS)
