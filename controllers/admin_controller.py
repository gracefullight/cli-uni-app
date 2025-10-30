"""Admin controller for handling all admin operations."""

from rich.console import Console

from messages import (
    Prompts,
    SuccessMessages,
    InfoMessages,
    FormatTemplates,
    Colors,
)
from services.admin_service import AdminService
from utils.grade_calculator import calculate_grade

console = Console()

# Member 3: Responsible for the Admin System
class AdminController:
    """Controller for admin operations: list, remove, group, partition, clear."""

    def __init__(self, admin_service: AdminService) -> None:
        self.admin_service = admin_service

    def list_students(self) -> None:
        """List all students with their statistics."""
        console.print(f"\t{InfoMessages.STUDENT_LIST}", style=Colors.WARNING)
        students = self.admin_service.list_students()
        if not students:
            console.print(f"\t\t{InfoMessages.NOTHING_TO_DISPLAY}")
            return

        for s in students:
            formatted_student = FormatTemplates.STUDENT_DETAIL.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    email=s.email,
                )
            console.print(f"\t{formatted_student}")

    def remove_student(self) -> None:
        """Remove a student by ID."""
        student_id = console.input(Prompts.STUDENT_ID_TO_REMOVE).strip()
        ok, msg = self.admin_service.remove_student(student_id)
        if not ok:
            console.print(f"\tStudent {student_id} does not exist", style=Colors.ERROR)
        else:
            console.print(f"\tRemoving Student {student_id} Account", style=Colors.WARNING)

    def group_by_grade(self) -> None:
        """Group students by their dominant grade."""
        console.print(f"\t{InfoMessages.GRADE_GROUPING}", style=Colors.WARNING)
        groups = self.admin_service.group_by_grade()

        if not any(groups.values()):
            console.print(f"\t\t{InfoMessages.NOTHING_TO_DISPLAY}", style=Colors.WARNING)
            return

        for grade, members in groups.items():
            if members:
                summaries = []
                for m in members:
                    summaries.append(
                        FormatTemplates.STUDENT_SUMMARY.format(
                            student_id=m.student_id,
                            first_name=m.first_name,
                            last_name=m.last_name,
                            average=m.average_mark(),
                            grade=m.get_grade(),
                        )
                    )

                joined = ", ".join(summaries)
                console.print(f"\t{grade} --> [{joined}]")

    def partition_pass_fail(self) -> None:
        """Partition students into pass/fail groups."""
        console.print(f"\t{InfoMessages.PASS_FAIL_PARTITION}", style=Colors.WARNING)
        passed, failed = self.admin_service.partition_pass_fail()

        failed_summaries: list[str] = []
        for s in failed:
            failed_summaries.append(
                FormatTemplates.STUDENT_SUMMARY.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    average=s.average_mark(),
                    grade=s.get_grade(),
                )
            )

        joined_failed = ", ".join(failed_summaries)
        console.print(f"\t{InfoMessages.STATUS_FAIL} --> [{joined_failed}]")

        passed_summaries: list[str] = []
        for s in passed:
            passed_summaries.append(
                FormatTemplates.STUDENT_SUMMARY.format(
                    student_id=s.student_id,
                    first_name=s.first_name,
                    last_name=s.last_name,
                    average=s.average_mark(),
                    grade=s.get_grade(),
                )
            )

        joined_passed = ", ".join(passed_summaries)
        console.print(f"\t{InfoMessages.STATUS_PASS} --> [{joined_passed}]")

    def clear_all(self) -> None:
        """Clear all student data with confirmation."""
        console.print(f"\t{InfoMessages.CLEARING_DATABASE}", style=Colors.WARNING)
        confirm = (
            console.input(f"[{Colors.ERROR}]\t{Prompts.CONFIRM_CLEAR}[/]").strip().upper()
        )

        if confirm == "Y":
            self.admin_service.clear_all_students()
            console.print(f"\t{SuccessMessages.ALL_CLEARED}", style=Colors.WARNING)
