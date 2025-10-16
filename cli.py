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
from utils.cmd import clear_screen
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
            choice = console.input("[cyan]University System: (A)dmin, (S)tudent, or [X] : [/]").strip().lower()
            if choice == "a":
                self.menu_admin()
            elif choice == "s":
                self.menu_student()
            elif choice == "x":
                console.print("Thank You", style="yellow")
                return
            else:
                console.print("Invalid option. Try again.", style="red")
                

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
                

    def menu_admin(self) -> None:
        clear_screen()
        # Admin system prompt (c/g/p/r/s/x)
        while True:
            console.print("Admin System:", style="cyan")
            admin_choice = console.input("[cyan][C]lear Database, [G]roup Students, [P]artition Students, [R]emove Student, [S]how Students or [X]: [/]").strip().lower()
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
                

    def menu_subject_enrollment(self, student: Student) -> None:
        while True:
            console.print(f"Student Course Menu ({student.first_name} {student.last_name} | ID: {student.student_id})", style="cyan")
            console.print("[C]hange Password, [E]nroll Subject, [R]emove Subject, [S]how Enrollment, or [X]", style="cyan")
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
            
            return
        if not validate_password(password):
            console.print("Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits", style="red")
            
            return
        # Enforce that email components match provided names
        try:
            fname_part, lname_part = email.split("@")[0].split(".")
        except ValueError:
            console.print("Error: Invalid email format components.", style="red")
            
            return
        if fname_part != first_name.lower() or lname_part != last_name.lower():
            console.print("Error: Email name parts must match first and last name provided.", style="red")
            
            return

        ok, msg, _student = self.db.add_student(first_name, last_name, email, password)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style="red")
        else:
            print(msg)
        

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
                
                return None
            return student
        console.print("Too many failed attempts.", style="red")
        return None

    def student_view_enrollment(self, student: Student) -> None:
        clear_screen()
        console.print(f"Showing {len(student.subjects)} subjects", style="yellow")
        if not student.subjects:
            console.print("No subjects enrolled.")
        else:
            for s in student.subjects:
                console.print(f"[{s.subject_id}] {s.name} - Mark: {s.mark}, Grade: {s.grade}")
            avg = student.average_mark()
            status = "PASS" if student.is_passing() else "FAIL"
            console.print(f"Average: {avg:.2f} ({status})")
        

    def student_enroll_subject(self, student: Student) -> None:
        clear_screen()
        console.print("------ Enroll in Subject ------", style="yellow")
        if len(student.subjects) >= MAX_SUBJECTS_PER_STUDENT:
            console.print(f"Error: Subject limit reached ({MAX_SUBJECTS_PER_STUDENT}).", style="red")
            return
        name = input("Subject name: ").strip()
        if not name:
            console.print("Error: Subject name cannot be empty.", style="red")
            
            return
        # Prevent duplicate subject names for the same student
        if any(s.name.lower() == name.lower() for s in student.subjects):
            console.print("Error: Already enrolled in a subject with this name.", style="red")
            
            return
        existing_ids = {s.subject_id for s in student.subjects}
        subject = Subject.create(name=name, existing_ids=existing_ids)
        student.subjects.append(subject)
        self.db.update_student(student)
        console.print(f"Success: Enrolled in {subject.name} with Subject ID {subject.subject_id}. Mark: {subject.mark}, Grade: {subject.grade}")
        console.print(f"You are now enrolled in {len(student.subjects)} out of {MAX_SUBJECTS_PER_STUDENT} subjects.", style="yellow")
        

    def student_remove_subject(self, student: Student) -> None:
        clear_screen()
        if not student.subjects:
            console.print("No subjects to remove.", style="red")
            return
        for s in student.subjects:
            console.print(f"[{s.subject_id}] {s.name}")
        subject_id = console.input("Enter Subject ID to remove: ").strip()
        for idx, s in enumerate(student.subjects):
            if s.subject_id == subject_id:
                console.print(f"Dropping subject {s.subject_id}", style="yellow")
                del student.subjects[idx]
                self.db.update_student(student)
                console.print(f"You are now enrolled in {len(student.subjects)} out of {MAX_SUBJECTS_PER_STUDENT} subjects.", style="yellow")
                return
        console.print("Error: Subject not found.", style="red")

    def student_change_password(self, student: Student) -> None:
        clear_screen()
        console.print("Updating Password", style="yellow")
        new_password = console.input("New password: ", password=True).strip()
        if not validate_password(new_password):
            console.print("Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits", style="red")
            
            return
        confirm_password = console.input("Confirm password: ", password=True).strip()
        if new_password != confirm_password:
            console.print("Error: Password does not match.", style="red")
            return

        student.password = hash_password(new_password)
        self.db.update_student(student)
        console.print("Success: Password changed.", style="green")
        

    # ------------------------- Admin Flows -------------------------
    def admin_list_students(self) -> None:
        clear_screen()
        console.print("Student List", style="yellow")
        students = self.db.list_students()
        if not students:
            console.print("No students found.", style="red")
            
            return

        for s in students:
            avg = s.average_mark()
            status = "PASS" if s.is_passing() else "FAIL"
            print(f"{s.student_id} | {s.first_name} {s.last_name} | {s.email} | Subjects: {len(s.subjects)} | Avg: {avg:.2f} ({status})")
        

    def admin_remove_student(self) -> None:
        clear_screen()
        console.print("Remove Student", style="red")
        student_id = console.input("Enter Student ID to remove: ").strip()
        ok, msg = self.db.remove_student(student_id)
        if isinstance(msg, str) and msg.startswith("Error"):
            console.print(msg, style="red")
        else:
            print(msg)
        

    def admin_group_by_grade(self) -> None:
        clear_screen()
        console.print("Grade Grouping", style="yellow")
        students = self.db.list_students()
        if not students:
            console.print("<Nothing to Display>")
            
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
            console.print(f"Grade {grade}:", style="yellow")
            if not members:
                console.print("<Nothing to Display>")
            else:
                for m in members:
                    print(f"  {m.student_id} | {m.first_name} {m.last_name} | Avg {m.average_mark():.2f}")
        

    def admin_partition_pass_fail(self) -> None:
        clear_screen()
        console.print("PASS/FAIL Partition", style="yellow")
        students = self.db.list_students()
        if not students:
            console.print("No students to partition.", style="red")
            
            return
        passed = [s for s in students if s.is_passing()]
        failed = [s for s in students if not s.is_passing()]
        console.print("PASS:", style="green")
        if not passed:
            console.print("<Nothing to Display>")
        else:
            for s in passed:
                console.print(f"  {s.student_id} | {s.first_name} {s.last_name} | Avg {s.average_mark():.2f}")
        console.print("FAIL:", style="red")
        if not failed:
            console.print("<Nothing to Display>")
        else:
            for s in failed:
                console.print(f"  {s.student_id} | {s.first_name} {s.last_name} | Avg {s.average_mark():.2f}")
        

    def admin_clear_all(self) -> None:
        clear_screen()
        console.print("Clearing students database", style="red")
        confirm = console.input("[red]Are you sure you want to clear the database (Y)ES/(N)O?: [/]").strip().upper()
        if confirm == "Y":
            self.db.clear_all()
            console.print("Success: All student data cleared.", style="yellow")
        else:
            console.print("Operation cancelled.", style="red")
        


def main() -> None:
    db = Database()
    cli = CLI(db)
    cli.run()


if __name__ == "__main__":
    main()


