import json
import os
from typing import Dict, List, Optional, Tuple

from models.student import Student
from utils.password import hash_password

DATA_FILE = "students.data"


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
        student_id = Student.generate_id(existing_ids)
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