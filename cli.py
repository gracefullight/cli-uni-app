"""
CLIUniApp: A complete Python CLI application for university student/admin management.

Features:
- Students: register, login, enroll/remove subjects (max 4), change password, view enrollment with marks/grades
- Admins: remove students, list students, group students by grade, partition pass/fail, clear all data
- Persistence: local file students.data storing all student and subject data (JSON format)
"""
from __future__ import annotations

from typing import Dict, List, Optional
from rich.console import Console

from constants import MAX_SUBJECTS_PER_STUDENT, MAX_LOGIN_ATTEMPTS, Grades
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

class CliApp:
    """Main CLI controller for menus and user interaction."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------- Menu Rendering -------------------------
    def run(self) -> None:
        while True:
            clear_screen()
            console.print(InfoMessages.UNIVERSITY_SYSTEM, style=Colors.HEADER)
            choice = console.input(f"[{Colors.HEADER}]{Prompts.UNIVERSITY}[/]").strip().lower()
            if choice == "a":
                self.menu_admin()
            elif choice == "s":
                self.menu_student()
            elif choice == "x":
                console.print(InfoMessages.THANK_YOU, style=Colors.WARNING)
                return
            else:
                console.print(ErrorMessages.INVALID_OPTION, style=Colors.ERROR)
                

    def menu_student(self) -> None:
        while True:
            student_choice = console.input(f"[{Colors.HEADER}]{Prompts.STUDENT_MENU}[/]").strip().lower()
            if student_choice == "l":
                student = self.student_login()
                if student:
                    clear_screen()
                    console.print(SuccessMessages.LOGIN.format(first_name=student.first_name), style=Colors.SUCCESS)
                    self.menu_subject_enrollment(student)
            elif student_choice == "r":
                self.student_register()
            elif student_choice == "x":
                break
            else:
                console.print(ErrorMessages.INVALID_ADMIN_OPTION, style=Colors.ERROR)
                

    # Person D: Admin System & Database
    def menu_admin(self) -> None:
        clear_screen()
        while True:
            console.print(InfoMessages.ADMIN_SYSTEM, style=Colors.HEADER)
            admin_choice = console.input(f"[{Colors.HEADER}]{Prompts.ADMIN_MENU}[/]").strip().lower()
            if admin_choice == "c":
                self.admin_clear_all()
            elif admin_choice == "g":
                self.admin_group_by_grade()
            elif admin_choice == "p":
                self.admin_partition_pass_fail()
            elif admin_choice == "r":
                self.admin_remove_student()
            elif admin_choice == "s":
                self.admin_list_students()
            elif admin_choice == "x":
                break
            else:
                console.print(ErrorMessages.INVALID_OPTION, style=Colors.ERROR)
                

    # Person C: Student Management & Password
    def menu_subject_enrollment(self, student: Student) -> None:
        while True:
            console.print(InfoMessages.STUDENT_COURSE_MENU.format(
                first_name=student.first_name, 
                last_name=student.last_name, 
                student_id=student.student_id
            ), style=Colors.HEADER)
            console.print(InfoMessages.COURSE_MENU_OPTIONS, style=Colors.HEADER)
            choice = console.input(Prompts.ENROLLMENT_OPTIONS).strip().lower()
            if choice == "c":
                self.student_change_password(student)
            elif choice == "e":
                self.student_enroll_subject(student)
            elif choice == "r":
                self.student_remove_subject(student)
            elif choice == "s":
                self.student_view_enrollment(student)
            elif choice == "x":
                return
            else:
                console.print(ErrorMessages.INVALID_OPTION, style=Colors.ERROR)
                

    # ------------------------- Student Flows -------------------------
    # Person A: Authentication
    def student_register(self) -> None:
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
        

    # Person A: Authentication
    def student_login(self) -> Optional[Student]:
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

    # Person B: Student Enrollment Features
    def student_view_enrollment(self, student: Student) -> None:
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
        

    # Person B: Student Enrollment Features
    def student_enroll_subject(self, student: Student) -> None:
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
        

    # Person B: Student Enrollment Features
    def student_remove_subject(self, student: Student) -> None:
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

    # Person C: Student Management & Password
    def student_change_password(self, student: Student) -> None:
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
        

    # ------------------------- Admin Flows -------------------------
    # Person D: Admin System & Database
    def admin_list_students(self) -> None:
        clear_screen()
        console.print(InfoMessages.STUDENT_LIST, style=Colors.WARNING)
        students = self.db.list_students()
        if not students:
            console.print(ErrorMessages.NO_STUDENTS_FOUND, style=Colors.ERROR)
            return

        for s in students:
            avg = s.average_mark()
            status = InfoMessages.STATUS_PASS if s.is_passing() else InfoMessages.STATUS_FAIL
            console.print(FormatTemplates.STUDENT_DETAIL.format(
                student_id=s.student_id,
                first_name=s.first_name,
                last_name=s.last_name,
                email=s.email,
                subject_count=len(s.subjects),
                average=avg,
                status=status
            ))
        

    # Person D: Admin System & Database
    def admin_remove_student(self) -> None:
        clear_screen()
        console.print(InfoMessages.REMOVE_STUDENT, style=Colors.ERROR)
        student_id = console.input(Prompts.STUDENT_ID_TO_REMOVE).strip()
        ok, msg = self.db.remove_student(student_id)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style=Colors.ERROR)
        else:
            console.print(msg)
        

    # Person D: Admin System & Database
    def admin_group_by_grade(self) -> None:
        clear_screen()
        console.print(InfoMessages.GRADE_GROUPING, style=Colors.WARNING)
        students = self.db.list_students()
        if not students:
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
            return
        
        groups: Dict[str, List[Student]] = {g: [] for g in Grades.ALL}
        
        for s in students:
            if not s.subjects:
                continue
            best = max((subj.grade for subj in s.subjects), key=lambda g: Grades.ORDER.get(g, -1))
            groups[best].append(s)
            
        for grade, members in groups.items():
            console.print(InfoMessages.GRADE_LABEL.format(grade=grade), style=Colors.WARNING)
            if not members:
                console.print(InfoMessages.NOTHING_TO_DISPLAY)
            else:
                for m in members:
                    console.print(FormatTemplates.STUDENT_SUMMARY.format(
                        student_id=m.student_id,
                        first_name=m.first_name,
                        last_name=m.last_name,
                        average=m.average_mark()
                    ))
        

    # Person D: Admin System & Database
    def admin_partition_pass_fail(self) -> None:
        clear_screen()
        console.print(InfoMessages.PASS_FAIL_PARTITION, style=Colors.WARNING)
        students = self.db.list_students()
        if not students:
            console.print(InfoMessages.NO_STUDENTS_TO_PARTITION, style=Colors.ERROR)
            return
        passed = [s for s in students if s.is_passing()]
        failed = [s for s in students if not s.is_passing()]
        
        console.print(InfoMessages.PASS_LABEL, style=Colors.SUCCESS)
        if not passed:
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
        else:
            for s in passed:
                console.print(FormatTemplates.STUDENT_SUMMARY.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    average=s.average_mark()
                ))
        
        console.print(InfoMessages.FAIL_LABEL, style=Colors.ERROR)
        if not failed:
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
        else:
            for s in failed:
                console.print(FormatTemplates.STUDENT_SUMMARY.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    average=s.average_mark()
                ))
        

    # Person D: Admin System & Database
    def admin_clear_all(self) -> None:
        clear_screen()
        console.print(InfoMessages.CLEARING_DATABASE, style=Colors.ERROR)
        confirm = console.input(f"[{Colors.ERROR}]{Prompts.CONFIRM_CLEAR}[/]").strip().upper()
        if confirm == "Y":
            self.db.clear_all_students()
            console.print(SuccessMessages.ALL_CLEARED, style=Colors.WARNING)
        else:
            console.print(SuccessMessages.OPERATION_CANCELLED, style=Colors.ERROR)
        


def main() -> None:
    db = Database()
    cli = CliApp(db)
    cli.run()


if __name__ == "__main__":
    main()


