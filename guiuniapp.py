"""
GUIUniApp: Minimal Tkinter GUI to pair with CLIUniApp for automated testing.

Provides:
- Login window: email/password entries, Login button, error handling
- Enrollment window: 'Enroll' button to add subjects (max 4), 'View Subjects' to show marks/grades
- Error dialogs via tkinter.messagebox
- Test hooks required by test_guiuniapp.py: launch_app(), ensure_logged_in_for_tests(), test_fixture_register_student()

This GUI uses the same persistence and validations from cliuniapp.py.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox

from cliuniapp import (
    Database,
    Subject,
    validate_email,
    validate_password,
    DATA_FILE,
)


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GUIUniApp")
        self.db = Database(os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE))
        self.current_student = None
        self._container = tk.Frame(self.root)
        self._container.pack(fill=tk.BOTH, expand=True)
        self._frames = {}
        self._build_login()
        self._build_register()
        self._build_enrollment()
        self._build_subjects_view()
        self._build_enroll_form()
        self._build_remove_subject()
        self._build_change_password()
        self.show_login()

    # ---------------- UI construction ----------------
    def _clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.pack_forget()

    def _build_login(self) -> None:
        frame = tk.Frame(self._container)
        lbl_title = tk.Label(frame, text="Login", font=("Arial", 14, "bold"))
        lbl_email = tk.Label(frame, text="Email:")
        self.entry_email = tk.Entry(frame)
        lbl_pass = tk.Label(frame, text="Password:")
        self.entry_password = tk.Entry(frame, show="*")
        btn_login = tk.Button(frame, text="Login", command=self._on_login)
        btn_register = tk.Button(frame, text="Register", command=self.show_register)
        btn_exit = tk.Button(frame, text="Exit", command=self.destroy)

        lbl_title.pack(pady=8)
        lbl_email.pack(anchor="w")
        self.entry_email.pack(fill=tk.X, padx=4)
        lbl_pass.pack(anchor="w", pady=(8, 0))
        self.entry_password.pack(fill=tk.X, padx=4)
        btn_login.pack(pady=(12, 4))
        btn_register.pack(pady=2)
        btn_exit.pack(pady=(8, 0))

        self._frames["login"] = frame

    def _build_register(self) -> None:
        frame = tk.Frame(self._container)
        tk.Label(frame, text="Register", font=("Arial", 14, "bold")).pack(pady=8)
        tk.Label(frame, text="First name:").pack(anchor="w")
        self.reg_first = tk.Entry(frame)
        self.reg_first.pack(fill=tk.X, padx=4)
        tk.Label(frame, text="Last name:").pack(anchor="w", pady=(6, 0))
        self.reg_last = tk.Entry(frame)
        self.reg_last.pack(fill=tk.X, padx=4)
        tk.Label(frame, text="Email (firstname.lastname@university.com):").pack(anchor="w", pady=(6, 0))
        self.reg_email = tk.Entry(frame)
        self.reg_email.pack(fill=tk.X, padx=4)
        tk.Label(frame, text="Password (Start uppercase, 5+ letters, end with 3 digits):").pack(anchor="w", pady=(6, 0))
        self.reg_password = tk.Entry(frame, show="*")
        self.reg_password.pack(fill=tk.X, padx=4)
        btn_create = tk.Button(frame, text="Create Account", command=self._on_register)
        btn_back = tk.Button(frame, text="Back", command=self.show_login)
        btn_create.pack(pady=(12, 4))
        btn_back.pack()
        self._frames["register"] = frame

    def _build_enrollment(self) -> None:
        frame = tk.Frame(self._container)
        self.lbl_enroll_title = tk.Label(frame, text="Enrollment", font=("Arial", 14, "bold"))
        self.lbl_enroll_title.pack(pady=8)

        # Student info / status line
        self.lbl_student_info = tk.Label(frame, text="", font=("Arial", 10))
        self.lbl_student_info.pack(pady=(0, 8))

        self.btn_enroll = tk.Button(frame, text="Enroll", command=self._on_enroll)
        self.btn_enroll.pack(pady=6)

        self.btn_view_subjects = tk.Button(frame, text="View Subjects", command=self._show_subjects_window)
        self.btn_view_subjects.pack(pady=6)

        # Extra actions per full GUI spec
        self.btn_enroll_form = tk.Button(frame, text="Enroll (Form)", command=self.show_enroll_form)
        self.btn_enroll_form.pack(pady=6)

        self.btn_remove_subject = tk.Button(frame, text="Remove Subject", command=self.show_remove_subject)
        self.btn_remove_subject.pack(pady=6)

        self.btn_change_password = tk.Button(frame, text="Change Password", command=self.show_change_password)
        self.btn_change_password.pack(pady=6)

        self.btn_logout = tk.Button(frame, text="Logout", command=self._logout)
        self.btn_logout.pack(pady=(12, 0))

        self._frames["enrollment"] = frame

    def _build_subjects_view(self) -> None:
        frame = tk.Frame(self._container)
        lbl = tk.Label(frame, text="Subjects", font=("Arial", 14, "bold"))
        lbl.pack(pady=8)
        # Static headers so tests can detect 'Mark' and 'Grade' labels even with no subjects
        header = tk.Frame(frame)
        tk.Label(header, text="Subject", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Mark", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=12)
        tk.Label(header, text="Grade", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=12)
        header.pack(anchor="w", padx=2)
        self.subjects_holder = tk.Frame(frame)
        self.subjects_holder.pack(fill=tk.BOTH, expand=True)
        btn_back = tk.Button(frame, text="Back", command=self.show_enrollment)
        btn_back.pack(pady=8)
        self._frames["subjects"] = frame

    def _build_enroll_form(self) -> None:
        frame = tk.Frame(self._container)
        tk.Label(frame, text="Enroll in Subject", font=("Arial", 14, "bold")).pack(pady=8)
        tk.Label(frame, text="Subject name:").pack(anchor="w")
        self.entry_subject_name = tk.Entry(frame)
        self.entry_subject_name.pack(fill=tk.X, padx=4)
        btn_enroll = tk.Button(frame, text="Enroll", command=self._on_enroll_form)
        btn_back = tk.Button(frame, text="Back", command=self.show_enrollment)
        btn_enroll.pack(pady=(12, 4))
        btn_back.pack()
        self._frames["enroll_form"] = frame

    def _build_remove_subject(self) -> None:
        frame = tk.Frame(self._container)
        tk.Label(frame, text="Remove Subject", font=("Arial", 14, "bold")).pack(pady=8)
        self.remove_list_holder = tk.Frame(frame)
        self.remove_list_holder.pack(fill=tk.BOTH, expand=True)
        controls = tk.Frame(frame)
        btn_remove = tk.Button(controls, text="Remove", command=self._on_remove_subject)
        btn_back = tk.Button(controls, text="Back", command=self.show_enrollment)
        btn_remove.pack(side=tk.LEFT, padx=4)
        btn_back.pack(side=tk.LEFT, padx=4)
        controls.pack(pady=8)
        self._frames["remove_subject"] = frame

    def _build_change_password(self) -> None:
        frame = tk.Frame(self._container)
        tk.Label(frame, text="Change Password", font=("Arial", 14, "bold")).pack(pady=8)
        tk.Label(frame, text="Current password:").pack(anchor="w")
        self.entry_pw_current = tk.Entry(frame, show="*")
        self.entry_pw_current.pack(fill=tk.X, padx=4)
        tk.Label(frame, text="New password (Start uppercase, 5+ letters, end with 3 digits):").pack(anchor="w", pady=(6, 0))
        self.entry_pw_new = tk.Entry(frame, show="*")
        self.entry_pw_new.pack(fill=tk.X, padx=4)
        btn_save = tk.Button(frame, text="Save", command=self._on_change_password)
        btn_back = tk.Button(frame, text="Back", command=self.show_enrollment)
        btn_save.pack(pady=(12, 4))
        btn_back.pack()
        self._frames["change_password"] = frame

    # ---------------- Public navigation ----------------
    def show_login(self) -> None:
        self._clear_container()
        self._frames["login"].pack(fill=tk.BOTH, expand=True)

    def show_register(self) -> None:
        self._clear_container()
        # Clear registration fields
        for e in (self.reg_first, self.reg_last, self.reg_email, self.reg_password):
            e.delete(0, tk.END)
        self._frames["register"].pack(fill=tk.BOTH, expand=True)

    def show_enrollment(self, student=None) -> None:
        if student is not None:
            self.current_student = student
        self._clear_container()
        self._frames["enrollment"].pack(fill=tk.BOTH, expand=True)
        if self.current_student is not None:
            self.lbl_enroll_title.config(text=f"Enrollment - {self.current_student.first_name} {self.current_student.last_name} ({self.current_student.student_id})")
        else:
            self.lbl_enroll_title.config(text="Enrollment")
        self._refresh_enrollment_buttons()
        self._refresh_student_info()

    def _show_subjects_window(self) -> None:
        self._clear_container()
        # Rebuild list each time
        for child in self.subjects_holder.winfo_children():
            child.destroy()
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                row = tk.Frame(self.subjects_holder)
                tk.Label(row, text=f"{subj.subject_id} - {subj.name}").pack(side=tk.LEFT)
                tk.Label(row, text=f"Mark: {subj.mark}").pack(side=tk.LEFT, padx=12)
                tk.Label(row, text=f"Grade: {subj.grade}").pack(side=tk.LEFT, padx=12)
                row.pack(anchor="w", pady=2)
        else:
            tk.Label(self.subjects_holder, text="No subjects enrolled.").pack(anchor="w")
        self._frames["subjects"].pack(fill=tk.BOTH, expand=True)

    def show_enroll_form(self) -> None:
        self._clear_container()
        self.entry_subject_name.delete(0, tk.END)
        self._frames["enroll_form"].pack(fill=tk.BOTH, expand=True)

    def show_remove_subject(self) -> None:
        self._clear_container()
        for child in self.remove_list_holder.winfo_children():
            child.destroy()
        self.remove_choice = tk.StringVar(value="")
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                tk.Radiobutton(self.remove_list_holder, text=f"{subj.subject_id} - {subj.name}", value=subj.subject_id, variable=self.remove_choice).pack(anchor="w")
        else:
            tk.Label(self.remove_list_holder, text="No subjects to remove.").pack(anchor="w")
        self._frames["remove_subject"].pack(fill=tk.BOTH, expand=True)

    def show_change_password(self) -> None:
        self._clear_container()
        self.entry_pw_current.delete(0, tk.END)
        self.entry_pw_new.delete(0, tk.END)
        self._frames["change_password"].pack(fill=tk.BOTH, expand=True)

    # ---------------- Event handlers ----------------
    def _on_login(self) -> None:
        email = self.entry_email.get().strip().lower()
        password = self.entry_password.get().strip()
        if not email or not password:
            messagebox.showerror("Login Error", "Email and password are required.")
            return
        if not validate_email(email) or not validate_password(password):
            messagebox.showerror("Login Error", "Invalid email or password format.")
            return
        student = self.db.get_student_by_email(email)
        if student is None or student.password != password:
            messagebox.showerror("Login Error", "Invalid credentials or unregistered user.")
            return
        self.current_student = student
        self.show_enrollment(student)

    def _on_register(self) -> None:
        first = self.reg_first.get().strip()
        last = self.reg_last.get().strip()
        email = self.reg_email.get().strip().lower()
        password = self.reg_password.get().strip()
        if not first or not last or not email or not password:
            messagebox.showerror("Registration Error", "All fields are required.")
            return
        if not validate_email(email):
            messagebox.showerror("Registration Error", "Invalid email format (firstname.lastname@university.com).")
            return
        try:
            fname_part, lname_part = email.split("@")[0].split(".")
        except ValueError:
            messagebox.showerror("Registration Error", "Invalid email components.")
            return
        if fname_part != first.lower() or lname_part != last.lower():
            messagebox.showerror("Registration Error", "Email name parts must match first and last name.")
            return
        if not validate_password(password):
            messagebox.showerror("Registration Error", "Password must start uppercase, have 5+ letters, and end with 3 digits.")
            return
        ok, msg, student = self.db.add_student(first, last, email, password)
        if not ok:
            messagebox.showerror("Registration Error", msg)
            return
        messagebox.showinfo("Registration", msg)
        self.show_login()

    def _on_enroll(self) -> None:
        if self.current_student is None:
            messagebox.showerror("Enroll Error", "No student logged in.")
            return
        # Reload from DB to ensure latest state
        fresh = self.db.get_student_by_id(self.current_student.student_id)
        if fresh is None:
            messagebox.showerror("Enroll Error", "Student not found.")
            return
        self.current_student = fresh
        if len(self.current_student.subjects) >= 4:
            messagebox.showerror("Enroll Error", "Maximum of 4 subjects exceeded.")
            return
        existing_ids = {s.subject_id for s in self.current_student.subjects}
        new_subject = Subject.create(name=f"Subject {len(self.current_student.subjects)+1}", existing_ids=existing_ids)
        self.current_student.subjects.append(new_subject)
        self.db.update_student(self.current_student)
        messagebox.showinfo("Enroll", f"Enrolled in {new_subject.name} (ID {new_subject.subject_id}) with mark {new_subject.mark} and grade {new_subject.grade}.")
        # Refresh UI state
        self._refresh_enrollment_buttons()
        self._refresh_student_info()
        self._refresh_enrollment_buttons()

    def _on_enroll_form(self) -> None:
        if self.current_student is None:
            messagebox.showerror("Enroll Error", "No student logged in.")
            return
        name = self.entry_subject_name.get().strip()
        if not name:
            messagebox.showerror("Enroll Error", "Subject name cannot be empty.")
            return
        fresh = self.db.get_student_by_id(self.current_student.student_id)
        if fresh is None:
            messagebox.showerror("Enroll Error", "Student not found.")
            return
        self.current_student = fresh
        if len(self.current_student.subjects) >= 4:
            messagebox.showerror("Enroll Error", "Maximum of 4 subjects exceeded.")
            return
        if any(s.name.lower() == name.lower() for s in self.current_student.subjects):
            messagebox.showerror("Enroll Error", "Already enrolled in a subject with this name.")
            return
        existing_ids = {s.subject_id for s in self.current_student.subjects}
        new_subject = Subject.create(name=name, existing_ids=existing_ids)
        self.current_student.subjects.append(new_subject)
        self.db.update_student(self.current_student)
        messagebox.showinfo("Enroll", f"Enrolled in {name} with mark {new_subject.mark} and grade {new_subject.grade}.")
        # After success, return to main menu and refresh
        self.show_enrollment()
        self._refresh_enrollment_buttons()
        self._refresh_student_info()

    def _on_remove_subject(self) -> None:
        if self.current_student is None:
            messagebox.showerror("Remove Error", "No student logged in.")
            return
        subject_id = getattr(self, "remove_choice", None).get() if hasattr(self, "remove_choice") else ""
        if not subject_id:
            messagebox.showerror("Remove Error", "Please select a subject to remove.")
            return
        fresh = self.db.get_student_by_id(self.current_student.student_id)
        if fresh is None:
            messagebox.showerror("Remove Error", "Student not found.")
            return
        removed = False
        for idx, s in enumerate(fresh.subjects):
            if s.subject_id == subject_id:
                del fresh.subjects[idx]
                removed = True
                break
        if not removed:
            messagebox.showerror("Remove Error", "Subject not found.")
            return
        self.db.update_student(fresh)
        self.current_student = fresh
        messagebox.showinfo("Remove", "Subject removed.")
        self.show_enrollment()

    def _on_change_password(self) -> None:
        if self.current_student is None:
            messagebox.showerror("Password Error", "No student logged in.")
            return
        current = self.entry_pw_current.get().strip()
        new = self.entry_pw_new.get().strip()
        fresh = self.db.get_student_by_id(self.current_student.student_id)
        if fresh is None:
            messagebox.showerror("Password Error", "Student not found.")
            return
        if current != fresh.password:
            messagebox.showerror("Password Error", "Current password incorrect.")
            return
        if not validate_password(new):
            messagebox.showerror("Password Error", "Invalid password format.")
            return
        fresh.password = new
        self.db.update_student(fresh)
        self.current_student = fresh
        messagebox.showinfo("Password", "Password changed successfully.")
        self.show_enrollment()

    def _logout(self) -> None:
        self.current_student = None
        self.show_login()

    def _refresh_enrollment_buttons(self) -> None:
        if self.current_student is None:
            self.btn_enroll.config(state=tk.DISABLED)
            self.btn_enroll_form.config(state=tk.DISABLED)
            return
        count = len(self.current_student.subjects)
        if count >= 4:
            self.btn_enroll.config(state=tk.DISABLED)
            self.btn_enroll_form.config(state=tk.DISABLED)
        else:
            self.btn_enroll.config(state=tk.NORMAL)
            self.btn_enroll_form.config(state=tk.NORMAL)

    def _refresh_student_info(self) -> None:
        if self.current_student is None:
            self.lbl_student_info.config(text="")
            return
        count = len(self.current_student.subjects)
        avg = (sum(s.mark for s in self.current_student.subjects) / count) if count else 0.0
        status = "PASS" if (avg >= 50 and count > 0) else ("N/A" if count == 0 else "FAIL")
        self.lbl_student_info.config(text=f"Subjects: {count} | Average: {avg:.2f} | Status: {status}")

    # ---------------- Test helpers ----------------
    def test_fixture_register_student(self, first_name: str, last_name: str, email: str, password: str):
        ok, _msg, student = self.db.add_student(first_name, last_name, email, password)
        if not ok:
            # Try to fetch existing
            student = self.db.get_student_by_email(email)
        return student

    def ensure_logged_in_for_tests(self, email: str, password: str) -> None:
        # If student does not exist, create a default one
        names = email.split("@")[0].split(".") if "@" in email and "." in email else ["test", "user"]
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else "user"
        student = self.test_fixture_register_student(first_name, last_name, email, password)
        self.current_student = student
        self.show_enrollment(student)

    def destroy(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass


def launch_app() -> App:
    return App()


if __name__ == "__main__":
    app = launch_app()
    app.root.mainloop()


