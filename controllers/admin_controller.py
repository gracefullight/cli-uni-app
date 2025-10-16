"""Admin controller for handling all admin operations."""

from typing import Dict, List
from rich.console import Console

from constants import Grades
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
from db import Database

console = Console()


# Person C: CLI Interface
class AdminController:
    """Controller for admin operations: list, remove, group, partition, clear."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def list_students(self) -> None:
        """List all students with their statistics."""
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

    def remove_student(self) -> None:
        """Remove a student by ID."""
        clear_screen()
        console.print(InfoMessages.REMOVE_STUDENT, style=Colors.ERROR)
        student_id = console.input(Prompts.STUDENT_ID_TO_REMOVE).strip()
        ok, msg = self.db.remove_student(student_id)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style=Colors.ERROR)
        else:
            console.print(msg)

    def group_by_grade(self) -> None:
        """Group students by their dominant grade."""
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

    def partition_pass_fail(self) -> None:
        """Partition students into pass/fail groups."""
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

    def clear_all(self) -> None:
        """Clear all student data with confirmation."""
        clear_screen()
        console.print(InfoMessages.CLEARING_DATABASE, style=Colors.ERROR)
        confirm = console.input(f"[{Colors.ERROR}]{Prompts.CONFIRM_CLEAR}[/]").strip().upper()
        if confirm == "Y":
            self.db.clear_all_students()
            console.print(SuccessMessages.ALL_CLEARED, style=Colors.WARNING)
        else:
            console.print(SuccessMessages.OPERATION_CANCELLED, style=Colors.ERROR)
