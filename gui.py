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

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from db import Database
from models.subject import Subject
from models.student import Student
from utils.password import validate_email, validate_password, hash_password, check_password


class App:
    def __init__(self) -> None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("GUIUniApp")
        self.root.geometry("500x400")
        self.db = Database()
        self.current_student: Optional[Student] = None
        self._container = ctk.CTkFrame(self.root)
        self._container.pack(fill="both", expand=True)
        self._frames: dict[str, ctk.CTkFrame] = {}
        self._build_login()
        self._build_enrollment()
        self._build_subjects_view()
        self._build_remove_subject()
        self._build_change_password()
        self.show_login()

    # ---------------- UI construction ----------------
    def _clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.pack_forget()

    def _build_login(self) -> None:
        frame = ctk.CTkFrame(self._container)
        lbl_title = ctk.CTkLabel(frame, text="Student Login", font=("Arial", 14, "bold"))
        lbl_email = ctk.CTkLabel(frame, text="Email:")
        self.entry_email = ctk.CTkEntry(frame, placeholder_text="Firstname.Lastname@university.com")
        lbl_pass = ctk.CTkLabel(frame, text="Password:")
        self.entry_password = ctk.CTkEntry(frame, show="*")
        self.entry_password.bind("<Return>", lambda e: self._on_login())
        
        btn_login = ctk.CTkButton(frame, text="Login", command=self._on_login)
        btn_exit = ctk.CTkButton(frame, text="Exit", command=self.destroy)

        lbl_title.pack(pady=8)
        lbl_email.pack(anchor="w")
        self.entry_email.pack(fill="x", padx=4)
        lbl_pass.pack(anchor="w", pady=(8, 0))
        self.entry_password.pack(fill="x", padx=4)
        btn_login.pack(pady=(12, 4))
        btn_exit.pack(pady=(8, 0))

        self._frames["login"] = frame

    def _build_enrollment(self) -> None:
        frame = ctk.CTkFrame(self._container)
        self.lbl_enroll_title = ctk.CTkLabel(frame, text="Enrollment", font=("Arial", 14, "bold"))
        self.lbl_enroll_title.pack(pady=8)

        # Student info / status line
        self.lbl_student_info = ctk.CTkLabel(frame, text="", font=("Arial", 10))
        self.lbl_student_info.pack(pady=(0, 8))

        self.btn_enroll = ctk.CTkButton(frame, text="Enroll", command=self._on_enroll)
        self.btn_enroll.pack(pady=6)

        self.btn_view_subjects = ctk.CTkButton(frame, text="View Subjects", command=self._show_subjects_window)
        self.btn_view_subjects.pack(pady=6)

        self.btn_remove_subject = ctk.CTkButton(frame, text="Remove Subject", command=self.show_remove_subject)
        self.btn_remove_subject.pack(pady=6)

        self.btn_change_password = ctk.CTkButton(frame, text="Change Password", command=self.show_change_password)
        self.btn_change_password.pack(pady=6)

        self.btn_logout = ctk.CTkButton(frame, text="Logout", command=self._logout)
        self.btn_logout.pack(pady=(12, 0))

        self._frames["enrollment"] = frame

    def _build_subjects_view(self) -> None:
        frame = ctk.CTkFrame(self._container)
        lbl = ctk.CTkLabel(frame, text="Subjects", font=("Arial", 14, "bold"))
        lbl.pack(pady=8)
        # Static headers - table style with fixed widths
        header = ctk.CTkFrame(frame, fg_color="transparent")
        ctk.CTkLabel(header, text="Subject", font=("Arial", 10, "bold"), width=200, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Mark", font=("Arial", 10, "bold"), width=80, anchor="center").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Grade", font=("Arial", 10, "bold"), width=80, anchor="center").pack(side="left", padx=5)
        header.pack(fill="x", padx=2, pady=(0, 5))
        # Pack Back button FIRST with side="bottom"
        btn_back = ctk.CTkButton(frame, text="Back", command=self.show_enrollment)
        btn_back.pack(side="bottom", pady=8)
        # Then pack subjects_holder - it will fill remaining space
        self.subjects_holder = ctk.CTkFrame(frame)
        self.subjects_holder.pack(fill="both", expand=True)
        self._frames["subjects"] = frame

    def _build_remove_subject(self) -> None:
        frame = ctk.CTkFrame(self._container)
        ctk.CTkLabel(frame, text="Remove Subject", font=("Arial", 14, "bold")).pack(pady=8)
        self.remove_list_holder = ctk.CTkFrame(frame)
        self.remove_list_holder.pack(fill="both", expand=True)
        controls = ctk.CTkFrame(frame)
        btn_remove = ctk.CTkButton(controls, text="Remove", command=self._on_remove_subject)
        btn_back = ctk.CTkButton(controls, text="Back", command=self.show_enrollment)
        btn_remove.pack(side="left", padx=4)
        btn_back.pack(side="left", padx=4)
        controls.pack(pady=8)
        self._frames["remove_subject"] = frame

    def _build_change_password(self) -> None:
        frame = ctk.CTkFrame(self._container)
        ctk.CTkLabel(frame, text="Change Password", font=("Arial", 14, "bold")).pack(pady=8)
        ctk.CTkLabel(frame, text="New password (Start uppercase, 5+ letters, end with 3 digits):").pack(anchor="w")
        self.entry_pw_new = ctk.CTkEntry(frame, show="*")
        self.entry_pw_new.pack(fill="x", padx=4)
        ctk.CTkLabel(frame, text="Confirm password:").pack(anchor="w", pady=(6, 0))
        self.entry_pw_confirm = ctk.CTkEntry(frame, show="*")
        self.entry_pw_confirm.pack(fill="x", padx=4)
        btn_save = ctk.CTkButton(frame, text="Save", command=self._on_change_password)
        btn_back = ctk.CTkButton(frame, text="Back", command=self.show_enrollment)
        btn_save.pack(pady=(12, 4))
        btn_back.pack()
        self._frames["change_password"] = frame

    # ---------------- Public navigation ----------------
    def show_login(self) -> None:
        self._clear_container()
        self._frames["login"].pack(fill="both", expand=True)
        self.entry_email.focus()

    def show_enrollment(self, student=None) -> None:
        if student is not None:
            self.current_student = student

        self._clear_container()
        self._frames["enrollment"].pack(fill="both", expand=True)
        if self.current_student is not None:
            self.lbl_enroll_title.configure(text=f"Enrollment - {self.current_student.first_name} {self.current_student.last_name} ({self.current_student.student_id})")
        else:
            self.lbl_enroll_title.configure(text="Enrollment")
        self._refresh_enrollment_buttons()
        self._refresh_student_info()

    def _show_subjects_window(self) -> None:
        # Update content FIRST (while frame is hidden)
        for child in self.subjects_holder.winfo_children():
            child.destroy()
        
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                row = ctk.CTkFrame(self.subjects_holder, fg_color="transparent")
                # Fixed width columns for table-like appearance
                ctk.CTkLabel(row, text=f"{subj.subject_id} - {subj.name}", width=200, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(subj.mark), width=80, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=subj.grade, width=80, anchor="center").pack(side="left", padx=5)
                row.pack(fill="x", pady=2)
        else:
            ctk.CTkLabel(self.subjects_holder, text="No subjects enrolled.").pack(anchor="w")
        
        # THEN switch to this frame
        self._clear_container()
        self._frames["subjects"].pack(fill="both", expand=True)

    def show_remove_subject(self) -> None:
        self._clear_container()
        for child in self.remove_list_holder.winfo_children():
            child.destroy()
        self.remove_choice = tk.StringVar(value="")
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                ctk.CTkRadioButton(self.remove_list_holder, text=f"{subj.subject_id} - {subj.name}", value=subj.subject_id, variable=self.remove_choice).pack(anchor="w")
        else:
            ctk.CTkLabel(self.remove_list_holder, text="No subjects to remove.").pack(anchor="w")
        self._frames["remove_subject"].pack(fill="both", expand=True)

    def show_change_password(self) -> None:
        self._clear_container()
        self.entry_pw_new.delete(0, "end")
        self.entry_pw_confirm.delete(0, "end")
        self._frames["change_password"].pack(fill="both", expand=True)

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
        if student is None or not check_password(password, student.password):
            messagebox.showerror("Login Error", "Invalid credentials or unregistered user.")
            return
        self.current_student = student
        self.show_enrollment(student)

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

    def _on_remove_subject(self) -> None:
        if self.current_student is None:
            messagebox.showerror("Remove Error", "No student logged in.")
            return
        remove_choice = getattr(self, "remove_choice", None)
        subject_id = remove_choice.get() if remove_choice is not None else ""
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
        new_password = self.entry_pw_new.get().strip()
        confirm_password = self.entry_pw_confirm.get().strip()
        if new_password != confirm_password:
            messagebox.showerror("Password Error", "New passwords do not match.")
            return
        if not validate_password(new_password):
            messagebox.showerror("Password Error", "Invalid password format.")
            return
        fresh = self.db.get_student_by_id(self.current_student.student_id)
        if fresh is None:
            messagebox.showerror("Password Error", "Student not found.")
            return
        fresh.password = hash_password(new_password)
        self.db.update_student(fresh)
        self.current_student = fresh
        messagebox.showinfo("Password", "Password changed successfully.")
        self.show_enrollment()

    def _logout(self) -> None:
        self.current_student = None
        # Clear login fields
        self.entry_email.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.show_login()

    def _refresh_enrollment_buttons(self) -> None:
        if self.current_student is None:
            self.btn_enroll.configure(state="disabled")
            return
        self.btn_enroll.configure(state="normal")

    def _refresh_student_info(self) -> None:
        if self.current_student is None:
            self.lbl_student_info.configure(text="")
            return
        count = len(self.current_student.subjects)
        avg = (sum(s.mark for s in self.current_student.subjects) / count) if count else 0.0
        status = "PASS" if (avg >= 50 and count > 0) else ("N/A" if count == 0 else "FAIL")
        self.lbl_student_info.configure(text=f"Subjects: {count} | Average: {avg:.2f} | Status: {status}")

    def destroy(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

def main() -> None:
    app = App()
    app.root.mainloop()


if __name__ == "__main__":
    main()


