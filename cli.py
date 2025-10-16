"""
CLIUniApp: A complete Python CLI application for university student/admin management.

Features:
- Students: register, login, enroll/remove subjects (max 4), change password, view enrollment with marks/grades
- Admins: remove students, list students, group students by grade, partition pass/fail, clear all data
- Persistence: local file students.data storing all student and subject data (JSON format)

Usage:
  python3 cliuniapp.py

Notes:
- Uses only Python standard libraries.
- All input/output formatting is consistent and robust error handling is implemented.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple

from rich.console import Console

from utils.cmd import clear_screen, pause
from utils.password import validate_email, validate_password, hash_password, check_password

# rich console for colored output
console = Console()


DATA_FILE = "students.data"
MAX_SUBJECTS_PER_STUDENT = 4
PASSING_AVERAGE = 50

def generate_unique_id(existing_ids: set[str], length: int) -> str:
    """Generate a unique numeric string ID of given length not present in existing_ids."""
    lower = 10 ** (length - 1)
    upper = (10 ** length) - 1
    while True:
        candidate = str(random.randint(lower, upper))
        if candidate not in existing_ids:
            return candidate

def calculate_grade(mark: int) -> str:
    """Return grade string based on mark."""
    if mark >= 85:
        return "HD"  # High Distinction
    if mark >= 75:
        return "D"   # Distinction
    if mark >= 65:
        return "C"   # Credit
    if mark >= 50:
        return "P"   # Pass
    return "F"       # Fail

@dataclass
class Subject:
    """Represents a subject enrollment with an ID, name, mark, and grade."""

    subject_id: str
    name: str
    mark: int
    grade: str

    @staticmethod
    def create(name: str, existing_ids: set[str]) -> "Subject":
        """Create a new subject with unique 3-digit ID and random mark."""
        subject_id = generate_unique_id(existing_ids, 3)
        mark = random.randint(0, 100)
        grade = calculate_grade(mark)
        return Subject(subject_id=subject_id, name=name, mark=mark, grade=grade)

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Subject":
        return Subject(
            subject_id=str(data["subject_id"]),
            name=str(data["name"]),
            mark=int(data["mark"]),
            grade=str(data["grade"]),
        )


@dataclass
class Student:
    """Represents a student with ID, name, email, password, and enrolled subjects."""

    student_id: str
    first_name: str
    last_name: str
    email: str
    password: str
    subjects: List[Subject] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "subjects": [s.to_dict() for s in self.subjects],
        }

    @staticmethod
    def from_dict(data: Dict) -> "Student":
        return Student(
            student_id=str(data["student_id"]),
            first_name=str(data["first_name"]),
            last_name=str(data["last_name"]),
            email=str(data["email"]),
            password=str(data["password"]),
            subjects=[Subject.from_dict(s) for s in data.get("subjects", [])],
        )

    def average_mark(self) -> float:
        if not self.subjects:
            return 0.0
        return sum(s.mark for s in self.subjects) / len(self.subjects)

    def is_passing(self) -> bool:
        return self.average_mark() >= PASSING_AVERAGE


class Database:
    """Simple JSON-file backed database for students and subjects."""

    def __init__(self, filepath: str = DATA_FILE) -> None:
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[Student]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
        students = [Student.from_dict(d) for d in data]
        return students

    def _write_all(self, students: List[Student | Dict]) -> None:
        serializable = [s.to_dict() if isinstance(s, Student) else s for s in students]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)

    # CRUD operations
    def list_students(self) -> List[Student]:
        return self._read_all()

    def get_student_by_email(self, email: str) -> Optional[Student]:
        for s in self._read_all():
            if s.email == email:
                return s
        return None

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        for s in self._read_all():
            if s.student_id == student_id:
                return s
        return None

    def add_student(self, first_name: str, last_name: str, email: str, password: str) -> Tuple[bool, str, Optional[Student]]:
        students = self._read_all()
        if any(s.email == email for s in students):
            return False, "Error: Email already registered.", None
        existing_ids = {s.student_id for s in students}
        student_id = generate_unique_id(existing_ids, 6)
        hashed_password = hash_password(password)
        new_student = Student(student_id=student_id, first_name=first_name, last_name=last_name, email=email, password=hashed_password, subjects=[])
        students.append(new_student)
        self._write_all(students)
        return True, f"Success: Student registered with ID {student_id}.", new_student

    def update_student(self, updated: Student) -> None:
        students = self._read_all()
        for idx, s in enumerate(students):
            if s.student_id == updated.student_id:
                students[idx] = updated
                self._write_all(students)
                return
        # If not found, append (should not happen in normal flow)
        students.append(updated)
        self._write_all(students)

    def remove_student(self, student_id: str) -> Tuple[bool, str]:
        students = self._read_all()
        new_students = [s for s in students if s.student_id != student_id]
        if len(new_students) == len(students):
            return False, "Error: Student not found."
        self._write_all(new_students)
        return True, "Success: Student removed."

    def clear_all(self) -> None:
        self._write_all([])

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
            elif choice == "s":
                # Student system prompt (l/r/z/x) - login/register/back/exit
                while True:
                    student_choice = console.input("[cyan]Student System (l/r/z/x): [/]").strip().lower()
                    if student_choice == "l":
                        student = self.student_login()
                        if student:
                            self.menu_subject_enrollment(student)
                    elif student_choice == "r":
                        self.student_register()
                    elif student_choice == "z":
                        # 'z' used as Back in screenshot (maps to returning to main prompt)
                        break
                    elif student_choice == "x":
                        print("Thank You")
                        return
                    else:
                        console.print("Invalid student option. Try again.", style="red")
                        pause()
            elif choice == "x":
                console.print("Thank You", style="yellow")
                return
            else:
                console.print("Invalid option. Try again.", style="red")
                pause()

    def menu_student(self) -> None:
        while True:
            clear_screen()
            print("------ Student Menu ------")
            print("1. Register")
            print("2. Login")
            print("3. Back")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.student_register()
            elif choice == "2":
                student = self.student_login()
                if student:
                    self.menu_subject_enrollment(student)
            elif choice == "3":
                return
            else:
                console.print("Invalid option. Try again.", style="red")
                pause()

    def menu_admin(self) -> None:
        while True:
            clear_screen()
            print("------ Admin Menu ------")
            print("1. List Students")
            print("2. Remove Student")
            print("3. Group Students by Grade")
            print("4. Partition Students by Pass/Fail")
            print("5. Clear All Student Data")
            print("6. Back")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.admin_list_students()
            elif choice == "2":
                self.admin_remove_student()
            elif choice == "3":
                self.admin_group_by_grade()
            elif choice == "4":
                self.admin_partition_pass_fail()
            elif choice == "5":
                self.admin_clear_all()
            elif choice == "6":
                return
            else:
                print("Invalid option. Try again.")
                pause()

    def menu_subject_enrollment(self, student: Student) -> None:
        while True:
            clear_screen()
            print(f"------ Subject Enrollment ({student.first_name} {student.last_name} | ID: {student.student_id}) ------")
            print("1. View Enrollment")
            print("2. Enroll in Subject")
            print("3. Remove Subject")
            print("4. Change Password")
            print("5. Logout")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.student_view_enrollment(student)
            elif choice == "2":
                self.student_enroll_subject(student)
            elif choice == "3":
                self.student_remove_subject(student)
            elif choice == "4":
                self.student_change_password(student)
            elif choice == "5":
                return
            else:
                print("Invalid option. Try again.")
                pause()

    # ------------------------- Student Flows -------------------------
    def student_register(self) -> None:
        clear_screen()
        print("------ Student Registration ------")
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        email = input("Email (firstname.lastname@university.com): ").strip().lower()
        password = input("Password (Start uppercase, 5+ letters, end with 3 digits): ").strip()

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
        print("------ Student Login ------")
        email = input("Email: ").strip().lower()
        password = input("Password: ").strip()
        student = self.db.get_student_by_email(email)
        if not student or not check_password(password, student.password):
            console.print("Error: Invalid email or password.", style="red")
            pause()
            return None
        print(f"Welcome, {student.first_name}!")
        pause("Press Enter to continue to Subject Enrollment...")
        return student

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
        print("------ Change Password ------")
        old = input("Current password: ").strip()
        if not check_password(old, student.password):
            console.print("Error: Current password incorrect.", style="red")
            pause()
            return
        new = input("New password: ").strip()
        if not validate_password(new):
            console.print("Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits", style="red")
            pause()
            return
        student.password = hash_password(new)
        self.db.update_student(student)
        print("Success: Password changed.")
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
    db = Database(os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE))
    cli = CLI(db)
    cli.run()


if __name__ == "__main__":
    main()


