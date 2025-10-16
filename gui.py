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

import customtkinter as ctk  # type: ignore
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from messages import GUIMessages, FormatTemplates
from db import Database
from models.student import Student
from controllers.gui_student_controller import GUIStudentController


class GuiApp:
    def __init__(self, db: Database) -> None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("GUIUniApp")
        self.root.geometry("500x400")
        self.db = db
        self.controller = GUIStudentController(db)
        self.current_student: Optional[Student] = None
        self._container = ctk.CTkFrame(self.root)
        self._container.pack(fill="both", expand=True)
        self._frames: dict[str, ctk.CTkFrame] = {}
        self._build_enrollment_window()
        self._build_subject_window()
        self._build_remove_subject_window()
        self._build_change_password_window()
        self._build_login_window()
        self.show_login_window()

    def _clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.pack_forget()

    # Person D: GUI Interface - Login Window
    def _build_login_window(self) -> None:
        frame = ctk.CTkFrame(self._container)
        
        title = ctk.CTkLabel(frame, text=GUIMessages.LOGIN_TITLE, font=("Arial", 24, "bold"))
        title.pack(pady=20)

        lbl_email = ctk.CTkLabel(frame, text=GUIMessages.EMAIL_LABEL, font=("Arial", 12))
        lbl_email.pack(anchor="w", padx=50, pady=(10, 0))
        
        self.entry_email = ctk.CTkEntry(frame, placeholder_text=GUIMessages.EMAIL_PLACEHOLDER, width=300)
        self.entry_email.pack(pady=(0, 10), padx=50)

        lbl_password = ctk.CTkLabel(frame, text=GUIMessages.PASSWORD_LABEL, font=("Arial", 12))
        lbl_password.pack(anchor="w", padx=50, pady=(10, 0))
        
        self.entry_password = ctk.CTkEntry(frame, placeholder_text="Enter password", width=300, show="*")
        self.entry_password.pack(pady=(0, 10), padx=50)
        self.entry_password.bind("<Return>", lambda event: self._on_login())

        btn_login = ctk.CTkButton(frame, text=GUIMessages.LOGIN_BUTTON, command=self._on_login)
        btn_login.pack(pady=10)
        
        self._frames["login"] = frame

    # Person D: GUI Interface - Enrollment Window
    def _build_enrollment_window(self) -> None:
        frame = ctk.CTkFrame(self._container)
        self.lbl_enroll_title = ctk.CTkLabel(frame, text=GUIMessages.ENROLLMENT_TITLE, font=("Arial", 14, "bold"))
        self.lbl_enroll_title.pack(pady=8)

        self.lbl_student_info = ctk.CTkLabel(frame, text="", font=("Arial", 10))
        self.lbl_student_info.pack(pady=(0, 8))

        self.btn_enroll = ctk.CTkButton(frame, text=GUIMessages.ENROLL_BUTTON, command=self._on_enroll)
        self.btn_enroll.pack(pady=6)

        self.btn_view_subjects = ctk.CTkButton(frame, text=GUIMessages.VIEW_SUBJECTS_BUTTON, command=self.show_subject_window)
        self.btn_view_subjects.pack(pady=6)

        self.btn_remove_subject = ctk.CTkButton(frame, text=GUIMessages.REMOVE_SUBJECT_BUTTON, command=self.show_remove_subject_window)
        self.btn_remove_subject.pack(pady=6)

        self.btn_change_password = ctk.CTkButton(frame, text=GUIMessages.CHANGE_PASSWORD_BUTTON, command=self.show_change_password_window)
        self.btn_change_password.pack(pady=6)

        self.btn_logout = ctk.CTkButton(frame, text=GUIMessages.LOGOUT_BUTTON, command=self._logout)
        self.btn_logout.pack(pady=(12, 0))

        self._frames["enrollment"] = frame

    # Person D: GUI Interface - Subject Window
    def _build_subject_window(self) -> None:
        frame = ctk.CTkFrame(self._container)
        ctk.CTkLabel(frame, text=GUIMessages.SUBJECTS_TITLE, font=("Arial", 14, "bold")).pack(pady=8)
        self.subjects_holder = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.subjects_holder.pack(fill="both", expand=True, padx=10, pady=10)
        btn_back = ctk.CTkButton(frame, text=GUIMessages.BACK_BUTTON, command=self.show_enrollment_window)
        btn_back.pack(pady=8)
        self._frames["subjects"] = frame

    # Person D: GUI Interface - Remove Subject Window
    def _build_remove_subject_window(self) -> None:
        frame = ctk.CTkFrame(self._container)
        ctk.CTkLabel(frame, text=GUIMessages.REMOVE_SUBJECT_TITLE, font=("Arial", 14, "bold")).pack(pady=8)
        self.remove_list_holder = ctk.CTkFrame(frame)
        self.remove_list_holder.pack(fill="both", expand=True)
        controls = ctk.CTkFrame(frame)
        btn_remove = ctk.CTkButton(controls, text=GUIMessages.REMOVE_BUTTON, command=self._on_remove_subject)
        btn_back = ctk.CTkButton(controls, text=GUIMessages.BACK_BUTTON, command=self.show_enrollment_window)
        btn_remove.pack(side="left", padx=4)
        btn_back.pack(side="left", padx=4)
        controls.pack(pady=8)
        self._frames["remove_subject"] = frame

    # Person D: GUI Interface - Change Password Window
    def _build_change_password_window(self) -> None:
        frame = ctk.CTkFrame(self._container)
        ctk.CTkLabel(frame, text=GUIMessages.CHANGE_PASSWORD_TITLE, font=("Arial", 14, "bold")).pack(pady=8)
        ctk.CTkLabel(frame, text=GUIMessages.NEW_PASSWORD_LABEL).pack(anchor="w")
        self.entry_pw_new = ctk.CTkEntry(frame, show="*")
        self.entry_pw_new.pack(fill="x", padx=4)
        ctk.CTkLabel(frame, text=GUIMessages.CONFIRM_PASSWORD_LABEL).pack(anchor="w", pady=(6, 0))
        self.entry_pw_confirm = ctk.CTkEntry(frame, show="*")
        self.entry_pw_confirm.pack(fill="x", padx=4)
        btn_save = ctk.CTkButton(frame, text=GUIMessages.SAVE_BUTTON, command=self._on_change_password)
        btn_back = ctk.CTkButton(frame, text=GUIMessages.BACK_BUTTON, command=self.show_enrollment_window)
        btn_save.pack(pady=(12, 4))
        btn_back.pack()
        self._frames["change_password"] = frame

    # Person D: GUI Interface - Login Window
    def show_login_window(self) -> None:
        self._clear_container()
        self._frames["login"].pack(fill="both", expand=True)
        self.entry_email.focus()

    # Person D: GUI Interface - Enrollment Window (Main Window after login)
    def show_enrollment_window(self, student=None) -> None:
        if student is not None:
            self.current_student = student

        self._clear_container()
        self._frames["enrollment"].pack(fill="both", expand=True)
        if self.current_student is not None:
            title_text = FormatTemplates.GUI_ENROLLMENT_TITLE.format(
                first_name=self.current_student.first_name,
                last_name=self.current_student.last_name,
                student_id=self.current_student.student_id
            )
            self.lbl_enroll_title.configure(text=title_text)
            
            # Update student info: subject count, average, pass/fail
            num_subjects = len(self.current_student.subjects)
            avg = self.current_student.average_mark()
            pass_fail = self.current_student.is_passing()
            info_text = FormatTemplates.GUI_STUDENT_INFO.format(
                num_subjects=num_subjects,
                avg=avg,
                pass_fail=pass_fail
            )
            self.lbl_student_info.configure(text=info_text)
        else:
            self.lbl_enroll_title.configure(text=GUIMessages.ENROLLMENT_DEFAULT_TITLE)
            self.lbl_student_info.configure(text="")

    # Person D: GUI Interface - Subject Window
    def show_subject_window(self) -> None:
        for child in self.subjects_holder.winfo_children():
            child.destroy()
        
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                row = ctk.CTkFrame(self.subjects_holder, fg_color="transparent")
                subject_text = FormatTemplates.GUI_SUBJECT_ROW.format(
                    subject_id=subj.subject_id,
                    name=subj.name
                )
                ctk.CTkLabel(row, text=subject_text, width=200, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(subj.mark), width=80, anchor="center").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=subj.grade, width=80, anchor="center").pack(side="left", padx=5)
                row.pack(fill="x", pady=2)
        else:
            ctk.CTkLabel(self.subjects_holder, text=GUIMessages.NO_SUBJECTS_GUI).pack(anchor="w")
        
        self._clear_container()
        self._frames["subjects"].pack(fill="both", expand=True)

    # Person D: GUI Interface - Remove Subject Window
    def show_remove_subject_window(self) -> None:
        self._clear_container()
        for child in self.remove_list_holder.winfo_children():
            child.destroy()
        self.remove_choice = tk.StringVar(value="")
        if self.current_student and self.current_student.subjects:
            for subj in self.current_student.subjects:
                button_text = FormatTemplates.GUI_SUBJECT_ROW.format(
                    subject_id=subj.subject_id,
                    name=subj.name
                )
                ctk.CTkRadioButton(self.remove_list_holder, text=button_text, value=subj.subject_id, variable=self.remove_choice).pack(anchor="w")
        else:
            ctk.CTkLabel(self.remove_list_holder, text=GUIMessages.NO_SUBJECTS_TO_REMOVE_GUI).pack(anchor="w")
        self._frames["remove_subject"].pack(fill="both", expand=True)

    # Person D: GUI Interface - Change Password Window
    def show_change_password_window(self) -> None:
        self._clear_container()
        self.entry_pw_new.delete(0, "end")
        self.entry_pw_confirm.delete(0, "end")
        self._frames["change_password"].pack(fill="both", expand=True)

    # Person D: GUI Interface
    def _on_login(self) -> None:
        email = self.entry_email.get().strip().lower()
        password = self.entry_password.get().strip()
        
        try:
            student = self.controller.login(email, password)
            self.current_student = student
            self.show_enrollment_window(student)
        except ValueError as e:
            messagebox.showerror(GUIMessages.LOGIN_ERROR, str(e))

    # Person D: GUI Interface - Enrollment Window
    def _on_enroll(self) -> None:
        if self.current_student is None:
            messagebox.showerror(GUIMessages.ENROLL_ERROR, GUIMessages.NO_STUDENT_LOGGED_IN)
            return
        
        try:
            self.current_student, new_subject = self.controller.enroll_subject(self.current_student)
            success_msg = GUIMessages.ENROLL_SUCCESS.format(
                name=new_subject.name,
                subject_id=new_subject.subject_id,
                mark=new_subject.mark,
                grade=new_subject.grade
            )
            messagebox.showinfo(GUIMessages.ENROLL_BUTTON, success_msg)
            self.show_enrollment_window()  # Refresh UI automatically
        except ValueError as e:
            messagebox.showerror(GUIMessages.ENROLL_ERROR, str(e))

    # Person D: GUI Interface - Remove Subject
    def _on_remove_subject(self) -> None:
        if self.current_student is None:
            messagebox.showerror(GUIMessages.REMOVE_ERROR, GUIMessages.NO_STUDENT_LOGGED_IN)
            return
        
        remove_choice = getattr(self, "remove_choice", None)
        subject_id = remove_choice.get() if remove_choice is not None else ""
        
        try:
            self.current_student = self.controller.remove_subject(self.current_student, subject_id)
            messagebox.showinfo(GUIMessages.REMOVE_SUBJECT_BUTTON, GUIMessages.SUBJECT_REMOVED)
            self.show_enrollment_window()
        except ValueError as e:
            messagebox.showerror(GUIMessages.REMOVE_ERROR, str(e))

    # Person D: GUI Interface - Change Password
    def _on_change_password(self) -> None:
        if self.current_student is None:
            messagebox.showerror(GUIMessages.PASSWORD_ERROR, GUIMessages.NO_STUDENT_LOGGED_IN)
            return
        
        new_password = self.entry_pw_new.get().strip()
        confirm_password = self.entry_pw_confirm.get().strip()
        
        try:
            self.current_student = self.controller.change_password(self.current_student, new_password, confirm_password)
            messagebox.showinfo(GUIMessages.CHANGE_PASSWORD_BUTTON, GUIMessages.PASSWORD_CHANGED)
            self.show_enrollment_window()
        except ValueError as e:
            messagebox.showerror(GUIMessages.PASSWORD_ERROR, str(e))

    def _logout(self) -> None:
        self.current_student = None
        # Clear login fields
        self.entry_email.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.show_login_window()

    def destroy(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

def main() -> None:
    db = Database()
    app = GuiApp(db)
    app.root.mainloop()


if __name__ == "__main__":
    main()


