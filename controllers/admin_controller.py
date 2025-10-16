"""Admin controller for handling all admin operations."""

from rich.console import Console

from messages import (
    Prompts,
    SuccessMessages,
    ErrorMessages,
    InfoMessages,
    FormatTemplates,
    Colors,
)
from utils.cmd import clear_screen
from services.admin_service import AdminService

console = Console()


# Member 3: Responsible for the Admin System
class AdminController:
    """Controller for admin operations: list, remove, group, partition, clear."""

    def __init__(self, admin_service: AdminService) -> None:
        self.admin_service = admin_service

    def list_students(self) -> None:
        """List all students with their statistics."""
        clear_screen()
        console.print(InfoMessages.STUDENT_LIST, style=Colors.WARNING)
        students = self.admin_service.list_students()
        if not students:
            console.print(ErrorMessages.NO_STUDENTS_FOUND, style=Colors.ERROR)
            return

        for s in students:
            avg = s.average_mark()
            status = InfoMessages.STATUS_PASS if s.is_passing() else InfoMessages.STATUS_FAIL
            console.print(
                FormatTemplates.STUDENT_DETAIL.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    email=s.email,
                    subject_count=len(s.subjects),
                    average=avg,
                    status=status,
                )
            )

    def remove_student(self) -> None:
        """Remove a student by ID."""
        clear_screen()
        console.print(InfoMessages.REMOVE_STUDENT, style=Colors.ERROR)
        student_id = console.input(Prompts.STUDENT_ID_TO_REMOVE).strip()
        ok, msg = self.admin_service.remove_student(student_id)
        if not ok:
            console.print(msg, style=Colors.ERROR)
        else:
            console.print(msg)

    def group_by_grade(self) -> None:
        """Group students by their dominant grade."""
        clear_screen()
        console.print(InfoMessages.GRADE_GROUPING, style=Colors.WARNING)
        groups = self.admin_service.group_by_grade()

        if not any(groups.values()):
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
            return

        for grade, members in groups.items():
            console.print(InfoMessages.GRADE_LABEL.format(grade=grade), style=Colors.WARNING)
            if not members:
                console.print(InfoMessages.NOTHING_TO_DISPLAY)
            else:
                for m in members:
                    console.print(
                        FormatTemplates.STUDENT_SUMMARY.format(
                            student_id=m.student_id,
                            first_name=m.first_name,
                            last_name=m.last_name,
                            average=m.average_mark(),
                        )
                    )

    def partition_pass_fail(self) -> None:
        """Partition students into pass/fail groups."""
        clear_screen()
        console.print(InfoMessages.PASS_FAIL_PARTITION, style=Colors.WARNING)
        passed, failed = self.admin_service.partition_pass_fail()

        if not passed and not failed:
            console.print(InfoMessages.NO_STUDENTS_TO_PARTITION, style=Colors.ERROR)
            return

        console.print(InfoMessages.PASS_LABEL, style=Colors.SUCCESS)
        if not passed:
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
        else:
            for s in passed:
                console.print(
                    FormatTemplates.STUDENT_SUMMARY.format(
                        student_id=s.student_id,
                        first_name=s.first_name,
                        last_name=s.last_name,
                        average=s.average_mark(),
                    )
                )

        console.print(InfoMessages.FAIL_LABEL, style=Colors.ERROR)
        if not failed:
            console.print(InfoMessages.NOTHING_TO_DISPLAY)
        else:
            for s in failed:
                console.print(
                    FormatTemplates.STUDENT_SUMMARY.format(
                        student_id=s.student_id,
                        first_name=s.first_name,
                        last_name=s.last_name,
                        average=s.average_mark(),
                    )
                )

    def clear_all(self) -> None:
        """Clear all student data with confirmation."""
        clear_screen()
        console.print(InfoMessages.CLEARING_DATABASE, style=Colors.ERROR)
        confirm = (
            console.input(f"[{Colors.ERROR}]{Prompts.CONFIRM_CLEAR}[/]").strip().upper()
        )
        if confirm == "Y":
            self.admin_service.clear_all_students()
            console.print(SuccessMessages.ALL_CLEARED, style=Colors.WARNING)
        else:
            console.print(SuccessMessages.OPERATION_CANCELLED, style=Colors.ERROR)
