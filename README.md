## CLIUniApp / GUIUniApp – University Management System

### Project Overview

CLIUniApp and GUIUniApp together implement a small university management system with two interactive subsystems: Students and Admins. The CLI is the primary deliverable; the GUI is an optional companion to mirror the same flows.

- **Students**: Register, login, enroll in up to 4 subjects, remove subjects, change password, and view enrolled subjects with marks and grades.
- **Admins**: List students, group by dominant grade, partition pass/fail by average mark, remove students, and clear all data.
- **Persistence**: All data is stored in a local file `students.data` (JSON), used by both CLI and GUI implementations.

**Technologies**
- **Language**: Python 3.x
- **CLI**: Rich library
- **GUI**: CustomTkinter
- **Architecture**: 3-Tier (Presentation, Service, Data Access)

### Group Member Contributions

Our team divided the work based on architectural layers and features, allowing each member to specialize while collaborating on end-to-end functionality.

#### Member 1 – Student Registration & Login Lead

- **Primary Responsibility**: Core student authentication features.
- **What**:
  - Implemented the main university menu and student menu in the CLI.
  - Built the student registration and login workflows, including all validation logic.
  - Developed the password hashing and checking utilities.
- **How**:
  - Key Files: `cli.py`, `student_controller.py`, `student_service.py`, `utils/password.py`.
  - Core Logic: `student_service.register`, `student_service.login`, `validate_email`, `validate_password`.
  - Rules: Enforced email format (`firstname.lastname@university.com`) and password complexity (e.g., `StartsUpper123`).
- **Why**:
  - This role establishes the foundation of the student subsystem, ensuring secure and reliable access. Centralizing validation in the service layer ensures consistency across different interfaces (CLI/GUI).

#### Member 2 – Subject & Enrollment Lead

- **Primary Responsibility**: Student academic management.
- **What**:
  - Implemented the complete subject enrollment system, including creating, enrolling, and removing subjects.
  - Developed the logic for calculating and assigning random marks and letter grades (HD, D, C, P, F).
  - Created the system for calculating a student's average mark and passing status.
- **How**:
  - Key Files: `student_controller.py`, `student_service.py`, `models/subject.py`, `utils/grade_calculator.py`.
  - Core Logic: `student_service.enroll_subject`, `student_service.remove_subject`, `Subject.create`, `calculate_grade`.
  - Rules: Enforced a maximum of 4 subjects per student.
- **Why**:
  - This role owns the core academic functionality of the application. Encapsulating grade logic in the model and service layers makes the system clean and easy to maintain.

#### Member 3 – Admin System Lead

- **Primary Responsibility**: Administrative oversight and data analysis features.
- **What**:
  - Built all features for the admin subsystem: listing students, removing students, and clearing the database.
  - Implemented the analytical features: grouping students by their dominant grade and partitioning them into pass/fail groups.
- **How**:
  - Key Files: `admin_controller.py`, `admin_service.py`, `cli.py`.
  - Core Logic: `admin_service.list_students`, `admin_service.group_by_grade`, `admin_service.partition_pass_fail`.
- **Why**:
  - This role provides essential tools for system administrators to manage and monitor student data, offering valuable insights into academic performance.

#### Member 4 – GUI Lead

- **Primary Responsibility**: All aspects of the graphical user interface.
- **What**:
  - Developed a complete Tkinter-based GUI that mirrors the student-facing CLI flows.
  - Implemented all GUI windows: Login, Enrollment Dashboard, View Subjects, Remove Subject, and Change Password.
  - Handled UI state management, navigation, and user-friendly error dialogs.
- **How**:
  - Key Files: `gui.py`, `gui_student_controller.py`.
  - Core Logic: Built reusable UI components and screen transition logic (`show_login_window`, `show_enrollment_window`, etc.). The GUI controller delegates all business logic to the `StudentService`.
- **Why**:
  - This role makes the application accessible to non-technical users. By reusing the same service layer as the CLI, we guarantee that business rules and data handling are 100% consistent across both interfaces.

### Collaborative Feature Walkthrough: Student Registration

To illustrate how we collaborated, let's walk through the "Student Registration" feature, which required contributions from multiple members:

1.  **Member 1 (CLI & Service Logic)**:
    - Defined the `register` method in the `StudentService`, which contains the core business logic: validating the email and password, checking for name mismatches, and calling the database to save the new student.
    - Implemented the CLI prompts in `StudentController` to gather the user's first name, last name, email, and password.

2.  **Member 4 (GUI Implementation)**:
    - While no registration form exists in the current GUI, Member 4 built the `login` window, which follows a similar pattern. The `GUIStudentController` calls the same `student_service.login` method that the CLI uses, demonstrating how both interfaces share a common backend.

3.  **Shared Infrastructure (All Members)**:
    - The `Student` model, initially created by Member 1 & 2, provides the data structure.
    - The `Database` class, with its `add_student` method, provides the persistence mechanism used by the service layer. This was a foundational piece of the project that all members relied on.

This collaborative approach ensured that our application was built on a solid, reusable foundation, with a clear separation of concerns between the user interface, business logic, and data layers.

### Architecture

Our application is built using a 3-tier architecture to ensure a clean separation of concerns:

1.  **Presentation Layer (UI)**:
    - `cli.py`, `gui.py`, and the `controllers` package.
    - This layer is responsible for all user interaction. It gathers input and displays results but contains no business logic. It delegates all actions to the service layer.

2.  **Service Layer (Business Logic)**:
    - The `services` package (`student_service.py`, `admin_service.py`).
    - This is the core of the application. It contains all business rules, validation, and logic (e.g., a student can only enroll in 4 subjects). It acts as the single source of truth for all operations.

3.  **Data Access Layer (DAL)**:
    - `db.py`, `models` package, and `students.data` file.
    - This layer is responsible for persisting data. It handles reading from and writing to the JSON data file and defines the data structures (`Student`, `Subject`).

This architecture makes the system highly maintainable and scalable. For example, because the CLI and GUI both use the same service layer, we can be confident that they behave identically.

### Setup and Run Instructions

#### Requirements

- Python 3.8+
- `customtkinter`, `rich`, and `bcrypt` libraries.

#### Installation

1.  Clone the repository.
2.  Install the required packages:
    ```bash
    pip install customtkinter rich bcrypt
    ```

#### Running the CLI

```bash
python3 cli.py
```

#### Running the GUI

```bash
python3 gui.py
```