"""
Automated GUI tests for GUIUniApp using unittest and Tkinter helpers.

This suite simulates user interactions (typing, clicking, navigation) and
verifies window transitions and validation/error handling.

Assumptions about the target GUI module (guiuniapp):
- The module provides a Tkinter-based application with a main `Tk` root.
- A callable `launch_app()` returns an object with attributes:
  - root: tkinter.Tk
  - show_login(): shows login window
  - show_enrollment(student): shows enrollment window
  - destroy(): closes the app
- The login window contains Entry widgets for email and password, and a Button
  with text 'Login'. Error feedback is via tkinter.messagebox.showerror or
  a Label whose text contains 'Error'.
- After successful login, enrollment window becomes visible with a Button text
  'Enroll' and a list of current subjects (Listbox or similar). An error when
  exceeding max subjects uses messagebox.showerror.

If the module or expected API is not available, tests are skipped gracefully.
"""

import importlib
import sys
import types
import unittest
from contextlib import contextmanager
from typing import Optional, List


try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - environment without Tk
    tk = None
    messagebox = None


def _find_widgets_of_type(parent: "tk.Misc", cls: type) -> List["tk.Misc"]:
    found = []
    for child in parent.winfo_children():
        try:
            if isinstance(child, cls):
                found.append(child)
        except Exception:
            pass
        found.extend(_find_widgets_of_type(child, cls))
    return found


def _find_button_by_text(parent: "tk.Misc", text: str) -> Optional["tk.Button"]:
    for btn in _find_widgets_of_type(parent, tk.Button):
        try:
            if btn.cget("text") == text:
                return btn
        except Exception:
            continue
    return None


def _find_entry_placeholders(parent: "tk.Misc") -> List["tk.Entry"]:
    return _find_widgets_of_type(parent, tk.Entry)


def _flush_events(root: "tk.Tk") -> None:
    root.update_idletasks()
    root.update()


@contextmanager
def patched_messagebox():
    """Patch tkinter.messagebox to record errors and infos during a test."""
    calls = {"showerror": [], "showinfo": [], "showwarning": []}

    def _recorder(name):
        def _f(title, message):
            calls[name].append((title, message))
        return _f

    if messagebox is None:
        yield calls
        return
    orig_err, orig_info, orig_warn = messagebox.showerror, messagebox.showinfo, messagebox.showwarning
    try:
        messagebox.showerror = _recorder("showerror")
        messagebox.showinfo = _recorder("showinfo")
        messagebox.showwarning = _recorder("showwarning")
        yield calls
    finally:
        messagebox.showerror, messagebox.showinfo, messagebox.showwarning = orig_err, orig_info, orig_warn


class TestGUIUniApp(unittest.TestCase):
    app_module: Optional[types.ModuleType] = None
    app = None

    @classmethod
    def setUpClass(cls):
        if tk is None:
            raise unittest.SkipTest("Tkinter not available in this environment")
        # Try to import gui module
        for name in ("guiuniapp", "GUIUniApp", "app_gui", "ui_app"):
            try:
                cls.app_module = importlib.import_module(name)
                break
            except Exception:
                continue
        if cls.app_module is None:
            raise unittest.SkipTest("GUI module not found (expected one of: guiuniapp, GUIUniApp, app_gui, ui_app)")
        if not hasattr(cls.app_module, "launch_app"):
            raise unittest.SkipTest("GUI module lacks launch_app() factory")
        # Launch once for the test class
        cls.app = cls.app_module.launch_app()
        if not hasattr(cls.app, "root") or not isinstance(cls.app.root, tk.Tk):
            raise unittest.SkipTest("launch_app() must return an object with a Tk root")

    @classmethod
    def tearDownClass(cls):
        if cls.app is not None and hasattr(cls.app, "destroy"):
            try:
                cls.app.destroy()
            except Exception:
                pass

    def setUp(self):
        self.assertIsNotNone(self.app)
        # Ensure login window is shown before each test if available
        if hasattr(self.app, "show_login"):
            self.app.show_login()
        _flush_events(self.app.root)

    # ---------------------- Login negative tests ----------------------
    def test_login_empty_shows_error(self):
        if not hasattr(self.app, "root"):
            self.skipTest("App missing root")
        with patched_messagebox() as calls:
            entries = _find_entry_placeholders(self.app.root)
            # Expect at least 2 entries: email and password
            self.assertGreaterEqual(len(entries), 2, "Expected email and password entries")
            for e in entries:
                e.delete(0, tk.END)
            _flush_events(self.app.root)
            # Click Login
            login_btn = _find_button_by_text(self.app.root, "Login")
            self.assertIsNotNone(login_btn, "Login button not found")
            login_btn.invoke()
            _flush_events(self.app.root)
            self.assertTrue(calls["showerror"], "Expected an error message for empty credentials")

    def test_login_invalid_format_shows_error(self):
        with patched_messagebox() as calls:
            entries = _find_entry_placeholders(self.app.root)
            self.assertGreaterEqual(len(entries), 2)
            email_entry, pass_entry = entries[0], entries[1]
            email_entry.delete(0, tk.END)
            email_entry.insert(0, "bademail@wrong")
            pass_entry.delete(0, tk.END)
            pass_entry.insert(0, "weak")
            _flush_events(self.app.root)
            login_btn = _find_button_by_text(self.app.root, "Login")
            self.assertIsNotNone(login_btn)
            login_btn.invoke()
            _flush_events(self.app.root)
            self.assertTrue(calls["showerror"], "Expected validation error for invalid formats")

    # ---------------------- Login positive test -----------------------
    def test_login_success_transitions_enrollment(self):
        if not hasattr(self.app, "test_fixture_register_student"):
            self.skipTest("GUI app does not expose test_fixture_register_student for seeding")
        # Seed a valid student
        student = self.app.test_fixture_register_student(
            first_name="john", last_name="doe",
            email="john.doe@university.com", password="Startt123"
        )
        self.assertIsNotNone(student)
        entries = _find_entry_placeholders(self.app.root)
        self.assertGreaterEqual(len(entries), 2)
        email_entry, pass_entry = entries[0], entries[1]
        email_entry.delete(0, tk.END)
        email_entry.insert(0, student.email)
        pass_entry.delete(0, tk.END)
        pass_entry.insert(0, student.password)
        _flush_events(self.app.root)
        login_btn = _find_button_by_text(self.app.root, "Login")
        self.assertIsNotNone(login_btn)
        login_btn.invoke()
        _flush_events(self.app.root)
        # Verify enrollment window is now present (e.g., an 'Enroll' button exists)
        enroll_btn = _find_button_by_text(self.app.root, "Enroll")
        self.assertIsNotNone(enroll_btn, "Expected to transition to Enrollment window with 'Enroll' button")

    # ---------------------- Enrollment tests -------------------------
    def test_enroll_up_to_four_subjects_and_block_fifth(self):
        if not hasattr(self.app, "ensure_logged_in_for_tests"):
            self.skipTest("GUI app does not expose ensure_logged_in_for_tests helper")
        self.app.ensure_logged_in_for_tests(email="jane.doe@university.com", password="Startt123")
        _flush_events(self.app.root)
        enroll_btn = _find_button_by_text(self.app.root, "Enroll")
        self.assertIsNotNone(enroll_btn)
        with patched_messagebox() as calls:
            for i in range(4):
                enroll_btn.invoke()
                _flush_events(self.app.root)
            # Fifth should trigger error
            enroll_btn.invoke()
            _flush_events(self.app.root)
            self.assertTrue(calls["showerror"], "Expected error when exceeding max subjects")

    def test_subject_window_shows_marks_and_grades(self):
        # Expect a button to open subjects view, often labelled 'Subjects' or 'View Subjects'
        open_subjects = _find_button_by_text(self.app.root, "View Subjects") or _find_button_by_text(self.app.root, "Subjects")
        if open_subjects is None:
            self.skipTest("Subjects view button not found")
        open_subjects.invoke()
        _flush_events(self.app.root)
        # Look for labels with 'Mark' and 'Grade' strings
        labels = _find_widgets_of_type(self.app.root, tk.Label)
        has_mark = any("Mark" in (lbl.cget("text") or "") for lbl in labels if str(lbl.cget("text")))
        has_grade = any("Grade" in (lbl.cget("text") or "") for lbl in labels if str(lbl.cget("text")))
        self.assertTrue(has_mark or has_grade, "Expected subjects view to show marks/grades")


if __name__ == "__main__":
    # Run with more verbose output for clear pass/fail reports
    unittest.main(verbosity=2)


