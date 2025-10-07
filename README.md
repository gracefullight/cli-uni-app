## CLIUniApp / GUIUniApp – University Management System

### Project Overview

CLIUniApp and GUIUniApp together implement a small university management system with two interactive subsystems: Students and Admins. The CLI is the primary deliverable; the GUI is an optional companion to mirror the same flows.

- **Students**: Register, login, enroll in up to 4 subjects, remove subjects, change password, and view enrolled subjects with marks and grades.
- **Admins**: List students, group by dominant grade, partition pass/fail by average mark, remove students, and clear all data.
- **Persistence**: All data is stored in a local file `students.data` (JSON), used by both CLI and GUI implementations.

**Technologies**
- **Language**: Python 3.x (standard library only)
- **CLI**: Plain Python I/O
- **GUI**: Tkinter
- **Testing**: `unittest` with Tkinter helpers for basic GUI automation


### Group Member Contributions

#### Member 1 – University Main Menu, Student System, Registration/Login

- **What**
  - Implemented the University main menu (CLI) with navigation to Student/Admin flows.
  - Built student registration and login workflows with validation and persistence.

- **How**
  - Key files: `cliuniapp.py`
  - Classes/Functions: `CLI.menu_student`, `CLI.student_register`, `CLI.student_login`, `validate_email`, `validate_password`, `Database.add_student`, `Database.get_student_by_email`.
  - Email rule: `firstname.lastname@university.com`.
  - Password rule: starts uppercase, 5+ letters total, ends with exactly 3 digits.
  - Student IDs: unique 6‑digit random numbers.

- **Why**
  - Centralized validators ensure consistent rules across CLI/GUI.
  - Simple, readable menus match assignment expectations and keep I/O predictable for grading.
  - File‑backed database makes the app portable and easy to evaluate.

- **Challenges & Solutions**
  - Ensuring email name parts match typed first/last names: parsed and verified during registration.
  - Avoiding duplicate accounts: `Database.add_student` checks for existing emails before insert.


#### Member 2 – Subject Enrollment System (Enroll/Remove, Marks & Grades)

- **What**
  - Implemented subject CRUD with a strict limit of 4 subjects per student.
  - Random marks (0–100) and derived grades (HD/D/C/P/F).

- **How**
  - Key code: `Subject.create`, `CLI.student_enroll_subject`, `CLI.student_remove_subject`.
  - Subject IDs: unique 3‑digit numbers (per student context).
  - Grade calculation: HD ≥85, D ≥75, C ≥65, P ≥50, else F.

- **Why**
  - Encapsulating mark/grade generation in `Subject.create` keeps the enrollment flow clean.
  - Preventing duplicate subject names per student improves usability and data clarity.

- **Challenges & Solutions**
  - Enforcing the max‑4 rule with informative errors: checked before creation, user gets clear messages.
  - Keeping averages accurate: recomputed from the student’s subject list when needed.


#### Member 3 – Admin System (List/Group/Partition/Remove, Data Management)

- **What**
  - Admin features to manage and analyze student data.
  - Group by dominant grade across enrolled subjects; partition by pass/fail using average.

- **How**
  - Key code: `CLI.menu_admin`, `CLI.admin_list_students`, `CLI.admin_group_by_grade`, `CLI.admin_partition_pass_fail`, `CLI.admin_remove_student`, `Database.clear_all`.
  - Dominant grade: highest grade attained among a student’s subjects; students with no subjects are shown as N/A.

- **Why**
  - Provides instructors with a quick overview of student performance.
  - Functions separated for clarity; `Database` abstracts file I/O for safety.

- **Challenges & Solutions**
  - Handling students with no subjects: added an explicit N/A group.
  - Avoiding accidental data loss: destructive actions require confirmation prompts (in CLI) and explicit calls.


#### Member 4 – GUI Development (Login, Student Menu, Enrollment UI, Navigation, Errors)

- **What**
  - Tkinter GUI mirroring the CLI flows: Login/Registration, Student Main Menu, Enroll (quick and form input), View Subjects, Remove Subject, Change Password, Logout.
  - Error handling with `tkinter.messagebox` dialogs.

- **How**
  - Key file: `guiuniapp.py`
  - Structure: `App` class with distinct builder methods per screen and navigation helpers (e.g., `show_login`, `show_enrollment`, `show_enroll_form`).
  - Uses the same `Database`, `Student`, `Subject`, and validators from the CLI to ensure consistent behavior.
  - Buttons enable/disable based on business rules (e.g., disable Enroll at 4 subjects).

- **Why**
  - Separating screens into small builder methods improves maintainability and readability.
  - Reusing CLI logic guarantees identical validations and persistence across interfaces.

- **Challenges & Solutions**
  - Keeping UI state in sync with storage: after each action, refresh UI labels and button states.
  - Making tests robust: headers and labels added so automated tests can reliably detect UI states.


### Integration & Testing

- **Integration**
  - Shared persistence through `students.data` and shared model/validation code.
  - CLI and GUI both interact via the same `Database` class and dataclasses (`Student`, `Subject`).

- **Testing Strategy**
  - CLI: manual scenario testing for menu flows and validations.
  - GUI: `unittest` suite (`test_guiuniapp.py`) with Tkinter widget introspection and patched `messagebox` to capture dialogs.
  - Positive and negative tests: login validation, enrollment limits, navigation.

- **Outcomes**
  - The app satisfies the assignment’s functional requirements and formatting.
  - Tests provide confidence in validation, transitions, and error handling.


### Setup and Run Instructions

#### Requirements

- Python 3.8+ (standard library only)
- Tkinter (usually included with Python on macOS and Windows; on some Linux distros install via package manager)

#### Installation

1. Clone or download this repository into a folder.
2. Ensure you are in the project directory:
   ```bash
   cd /Users/pranavsingh/Desktop/CLIUniApp
   ```

#### Running the CLI

```bash
python3 cliuniapp.py
```

#### Running the GUI (optional)

```bash
python3 guiuniapp.py
```

#### Running Tests

```bash
python3 -m unittest -v test_guiuniapp.py
```

Notes:
- The app will create/update `students.data` in the project directory.
- If Tkinter is not available, the GUI and GUI tests will be skipped or fail to launch.
- Install Tkinter to see the GUI


