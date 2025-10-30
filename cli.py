"""
CLIUniApp: A complete Python CLI application for university student/admin management.

Features:
- Students: register, login, enroll/remove subjects (max 4), change password, view enrollment with marks/grades
- Admins: remove students, list students, group students by grade, partition pass/fail, clear all data
- Persistence: local file students.data storing all student and subject data (JSON format)
"""
from __future__ import annotations

from rich.console import Console

from messages import (
    Prompts,
    SuccessMessages,
    ErrorMessages,
    InfoMessages,
    Colors,
)
from utils.cmd import clear_screen
from controllers.student_controller import StudentController
from controllers.admin_controller import AdminController
from db import Database
from services.student_service import StudentService
from services.admin_service import AdminService

console = Console()


class CliApp:
    """Main CLI application with menu navigation."""

    def __init__(self, student_controller: StudentController, admin_controller: AdminController) -> None:
        self.student_controller = student_controller
        self.admin_controller = admin_controller

    # ------------------------- Menu Rendering -------------------------
    # Member 1: Responsible for the main application flow
    def run(self) -> None:
        while True:
            clear_screen()
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

    # Member 1: Responsible for Student Registration and Login
    def menu_student(self) -> None:
        while True:
            student_choice = console.input(f"[{Colors.HEADER}]{Prompts.STUDENT_MENU}[/]").strip().lower()
            if student_choice == "l":
                student = self.student_controller.login()
                if student:
                    clear_screen()
                    console.print(SuccessMessages.LOGIN.format(first_name=student.first_name), style=Colors.SUCCESS)
                    self.menu_subject_enrollment(student)
            elif student_choice == "r":
                self.student_controller.register()
            elif student_choice == "x":
                break
            else:
                console.print(ErrorMessages.INVALID_ADMIN_OPTION, style=Colors.ERROR)

    # Member 3: Responsible for the Admin System
    def menu_admin(self) -> None:
        while True:
            admin_choice = console.input(f"[{Colors.HEADER}]\t{InfoMessages.ADMIN_SYSTEM}[/]").strip().lower()
            if admin_choice == "c":
                self.admin_controller.clear_all()
            elif admin_choice == "g":
                self.admin_controller.group_by_grade()
            elif admin_choice == "p":
                self.admin_controller.partition_pass_fail()
            elif admin_choice == "r":
                self.admin_controller.remove_student()
            elif admin_choice == "s":
                self.admin_controller.list_students()
            elif admin_choice == "x":
                break
            else:
                console.print(ErrorMessages.INVALID_OPTION, style=Colors.ERROR)

    # Member 2: Responsible for Subject Enrollment
    def menu_subject_enrollment(self, student) -> None:
        while True:
            console.print(InfoMessages.STUDENT_COURSE_MENU.format(
                first_name=student.first_name, 
                last_name=student.last_name, 
                student_id=student.student_id
            ), style=Colors.HEADER)
            console.print(InfoMessages.COURSE_MENU_OPTIONS, style=Colors.HEADER)
            choice = console.input(Prompts.ENROLLMENT_OPTIONS).strip().lower()
            if choice == "c":
                self.student_controller.change_password(student)
            elif choice == "e":
                self.student_controller.enroll_subject(student)
            elif choice == "r":
                self.student_controller.remove_subject(student)
            elif choice == "s":
                self.student_controller.view_enrollment(student)
            elif choice == "x":
                return
            else:
                console.print(ErrorMessages.INVALID_OPTION, style=Colors.ERROR)

# Shared responsibility: Application entry point
def main() -> None:
    db = Database()
    student_service = StudentService(db)
    admin_service = AdminService(db)
    student_controller = StudentController(student_service)
    admin_controller = AdminController(admin_service)
    cli = CliApp(student_controller, admin_controller)
    cli.run()


if __name__ == "__main__":
    main()