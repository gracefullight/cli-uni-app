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
from utils.cmd import clear_screen, pause
from utils.password import validate_email, validate_password, hash_password, check_password
from models.student import Student
from models.subject import Subject
from db import Database

# rich console for colored output
console = Console()

MAX_SUBJECTS_PER_STUDENT = 4

class CLI:
    """Main CLI controller for menus and user interaction."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------- Menu Rendering -------------------------
    def run(self) -> None:
        while True:
            clear_screen()
            # Print header in cyan using rich
            console.print("The University System", style="cyan")
            # Prompt format: University System: (A)dmin, (S)tudent, or X : 
            choice = console.input("[cyan]University System: (A)dmin, (S)tudent, or X : [/]").strip().lower()
            if choice == "a":
                self.menu_admin()
            elif choice == "s":
                self.menu_student()
            elif choice == "x":
                console.print("Thank You", style="yellow")
                return
            else:
                console.print("Invalid option. Try again.", style="red")
                pause()

    def menu_student(self) -> None:
        # Student system prompt (l/r/x) - login/register/back
        while True:
            student_choice = console.input("[cyan]Student System: [L]ogin, [R]egister, or X): [/]").strip().lower()
            if student_choice == "l":
                student = self.student_login()
                if student:
                    clear_screen()
                    console.print(f"Welcome, {student.first_name}!", style="green")
                    self.menu_subject_enrollment(student)
            elif student_choice == "r":
                self.student_register()
            elif student_choice == "x":
                break
            else:
                console.print("Invalid student option. Try again.", style="red")
                pause()

    def menu_admin(self) -> None:
        clear_screen()
        # Admin system prompt (c/g/p/r/s/x)
        while True:
            admin_choice = console.input("[cyan]Admin System (c/g/p/r/s/x): [/]").strip().lower()
            if admin_choice == "c":
                # Clear all student data
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
                console.print("Invalid admin option. Try again.", style="red")
                pause()

    def menu_subject_enrollment(self, student: Student) -> None:
        while True:
            console.print(f"Student Course Menu ({student.first_name} {student.last_name} | ID: {student.student_id})", style="cyan")
            console.print("[C]hange Password, [E]nroll Subject, [R]emove Subject, [S]how Enrollment, or X", style="cyan")
            choice = console.input("Select an option: ").strip().lower()
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
                console.print("Invalid option. Try again.", style="red")
                pause()

    # ------------------------- Student Flows -------------------------
    def student_register(self) -> None:
        clear_screen()
        console.print("Student Sign Up", style="green")
        first_name = console.input("First name: ").strip()
        last_name = console.input("Last name: ").strip()
        email = console.input("Email (firstname.lastname@university.com): ").strip().lower()
        password = console.input("Password (Start uppercase, 5+ letters, end with 3 digits): ", password=True).strip()

        # Validations
        if not validate_email(email):
            console.print("Error: Invalid email format. Expected firstname.lastname@university.com", style="red")
            pause()
            return
        if not validate_password(password):
            console.print("Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits", style="red")
            pause()
            return
        # Enforce that email components match provided names
        try:
            fname_part, lname_part = email.split("@")[0].split(".")
        except ValueError:
            console.print("Error: Invalid email format components.", style="red")
            pause()
            return
        if fname_part != first_name.lower() or lname_part != last_name.lower():
            console.print("Error: Email name parts must match first and last name provided.", style="red")
            pause()
            return

        ok, msg, _student = self.db.add_student(first_name, last_name, email, password)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style="red")
        else:
            print(msg)
        pause()

    def student_login(self) -> Optional[Student]:
        clear_screen()
        console.print("Student Sign In", style="green")

        attempts = 0
        while attempts < 3:
            email = console.input("Email: ").strip().lower()
            password = console.input("Password: ", password=True).strip()
            if not validate_email(email) or not validate_password(password):
                console.print("Incorrect email or password format", style="red")
                attempts += 1
                continue
            student = self.db.get_student_by_email(email)
            if not student or not check_password(password, student.password):
                console.print("Error: Invalid email or password.", style="red")
                pause()
                return None
            return student
        console.print("Too many failed attempts.", style="red")
        return None

    def student_view_enrollment(self, student: Student) -> None:
        clear_screen()
        print("------ Your Enrollment ------")
        if not student.subjects:
            print("No subjects enrolled.")
        else:
            for s in student.subjects:
                print(f"[{s.subject_id}] {s.name} - Mark: {s.mark}, Grade: {s.grade}")
            avg = student.average_mark()
            status = "PASS" if student.is_passing() else "FAIL"
            print(f"Average: {avg:.2f} ({status})")
        pause()

    def student_enroll_subject(self, student: Student) -> None:
        clear_screen()
        print("------ Enroll in Subject ------")
        if len(student.subjects) >= MAX_SUBJECTS_PER_STUDENT:
            console.print(f"Error: Subject limit reached ({MAX_SUBJECTS_PER_STUDENT}).", style="red")
            pause()
            return
        name = input("Subject name: ").strip()
        if not name:
            console.print("Error: Subject name cannot be empty.", style="red")
            pause()
            return
        # Prevent duplicate subject names for the same student
        if any(s.name.lower() == name.lower() for s in student.subjects):
            console.print("Error: Already enrolled in a subject with this name.", style="red")
            pause()
            return
        existing_ids = {s.subject_id for s in student.subjects}
        subject = Subject.create(name=name, existing_ids=existing_ids)
        student.subjects.append(subject)
        self.db.update_student(student)
        print(f"Success: Enrolled in {subject.name} with Subject ID {subject.subject_id}. Mark: {subject.mark}, Grade: {subject.grade}")
        pause()

    def student_remove_subject(self, student: Student) -> None:
        clear_screen()
        print("------ Remove Subject ------")
        if not student.subjects:
            print("No subjects to remove.")
            pause()
            return
        for s in student.subjects:
            print(f"[{s.subject_id}] {s.name}")
        subject_id = input("Enter Subject ID to remove: ").strip()
        for idx, s in enumerate(student.subjects):
            if s.subject_id == subject_id:
                del student.subjects[idx]
                self.db.update_student(student)
                print("Success: Subject removed.")
                pause()
                return
        console.print("Error: Subject not found.", style="red")
        pause()

    def student_change_password(self, student: Student) -> None:
        clear_screen()
        console.print("Updating Password", style="yellow")
        new_password = console.input("New password: ", password=True).strip()
        if not validate_password(new_password):
            console.print("Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits", style="red")
            pause()
            return
        confirm_password = console.input("Confirm password: ", password=True).strip()
        if new_password != confirm_password:
            console.print("Error: Passwords do not match.", style="red")
            return

        student.password = hash_password(new_password)
        self.db.update_student(student)
        console.print("Success: Password changed.", style="green")
        pause()

    # ------------------------- Admin Flows -------------------------
    def admin_list_students(self) -> None:
        clear_screen()
        print("------ All Students ------")
        students = self.db.list_students()
        if not students:
            print("No students found.")
            pause()
            return
        for s in students:
            avg = s.average_mark()
            status = "PASS" if s.is_passing() else "FAIL"
            print(f"{s.student_id} | {s.first_name} {s.last_name} | {s.email} | Subjects: {len(s.subjects)} | Avg: {avg:.2f} ({status})")
        pause()

    def admin_remove_student(self) -> None:
        clear_screen()
        print("------ Remove Student ------")
        student_id = input("Enter Student ID to remove: ").strip()
        ok, msg = self.db.remove_student(student_id)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style="red")
        else:
            print(msg)
        pause()

    def admin_group_by_grade(self) -> None:
        clear_screen()
        print("------ Group Students by Grade ------")
        students = self.db.list_students()
        if not students:
            print("No students to group.")
            pause()
            return
        # Determine dominant grade per student as the highest grade across subjects; if no subjects, 'N/A'
        grade_order = {"HD": 4, "D": 3, "C": 2, "P": 1, "F": 0}
        groups: Dict[str, List[Student]] = {"HD": [], "D": [], "C": [], "P": [], "F": [], "N/A": []}
        for s in students:
            if not s.subjects:
                groups["N/A"].append(s)
                continue
            best = max((subj.grade for subj in s.subjects), key=lambda g: grade_order.get(g, -1))
            groups[best].append(s)
        for grade, members in groups.items():
            print(f"Grade {grade}:")
            if not members:
                print("  (none)")
            else:
                for m in members:
                    print(f"  {m.student_id} | {m.first_name} {m.last_name} | Avg {m.average_mark():.2f}")
        pause()

    def admin_partition_pass_fail(self) -> None:
        clear_screen()
        print("------ Partition Students by Pass/Fail ------")
        students = self.db.list_students()
        if not students:
            print("No students to partition.")
            pause()
            return
        passed = [s for s in students if s.is_passing()]
        failed = [s for s in students if not s.is_passing()]
        print("PASS:")
        if not passed:
            print("  (none)")
        else:
            for s in passed:
                print(f"  {s.student_id} | {s.first_name} {s.last_name} | Avg {s.average_mark():.2f}")
        print("FAIL:")
        if not failed:
            print("  (none)")
        else:
            for s in failed:
                print(f"  {s.student_id} | {s.first_name} {s.last_name} | Avg {s.average_mark():.2f}")
        pause()

    def admin_clear_all(self) -> None:
        clear_screen()
        print("------ Clear All Student Data ------")
        confirm = input("Type 'CONFIRM' to permanently delete all student data: ").strip()
        if confirm == "CONFIRM":
            self.db.clear_all()
            print("Success: All student data cleared.")
        else:
            console.print("Operation cancelled.", style="red")
        pause()


def main() -> None:
    db = Database()
    cli = CLI(db)
    cli.run()


if __name__ == "__main__":
    main()


