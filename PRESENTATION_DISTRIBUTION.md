# Presentation Distribution Guide (Layer-Based)

## Person A: Models & Utils (Data Layer)
**Focus**: Data models, ID generation, grade calculation, password/email validation

### Files & Methods:
- **models/student.py** (전체)
  - `Student` dataclass - Core student model with ID, name, email, password, subjects
  - `generate_id()` - Unique 6-digit student ID generation
  - `to_dict()`, `from_dict()` - JSON serialization
  - `average_mark()` - Calculate average of enrolled subjects
  - `is_passing()` - Check if student passes (average >= 50)

- **models/subject.py** (전체)
  - `Subject` dataclass - Core subject model with ID, name, mark, grade
  - `generate_id()` - Unique 3-digit subject ID generation
  - `create()` - Factory method to create subject with random mark
  - `to_dict()`, `from_dict()` - JSON serialization

- **utils/password.py** (전체)
  - `validate_email()` - Email format validation (firstname.lastname@university.com)
  - `validate_password()` - Password format validation (uppercase + 5+ letters + 3 digits)
  - `hash_password()` - BCrypt password hashing
  - `check_password()` - Password verification against hash

- **utils/id_generator.py** (전체)
  - `generate_unique_id()` - Generate unique numeric string ID

- **utils/grade_calculator.py** (전체)
  - `calculate_grade()` - Calculate grade (HD/D/C/P/F) from mark

---

## Person B: Database Layer
**Focus**: JSON file-based persistence, all CRUD operations

### Files & Methods:
- **db.py** (전체)
  - `__init__()` - Initialize database with file path
  - `_ensure_file()` - Create data file if not exists
  - `_read_all()` - Read all students from JSON file
  - `_write_all()` - Write all students to JSON file
  - `list_students()` - Get all students
  - `get_student_by_email()` - Find student by email (for login)
  - `get_student_by_id()` - Find student by ID
  - `add_student()` - Register new student with validation
  - `update_student()` - Update student data (for enrollment/password changes)
  - `remove_student()` - Delete student by ID
  - `clear_all_students()` - Clear all data

---

## Person C: CLI Interface
**Focus**: Terminal-based UI with Rich Console, all student/admin features

### Files & Methods:
- **cli.py** (전체)
  - **Main Menu**:
    - `run()` - Main application loop
    - `menu_student()` - Student menu navigation
    - `menu_admin()` - Admin menu navigation
    - `menu_subject_enrollment()` - Subject enrollment menu
  
  - **Student Features**:
    - `student_register()` - Registration with email/password validation
    - `student_login()` - Login with retry limit (max 3 attempts)
    - `student_view_enrollment()` - View enrolled subjects with marks/grades
    - `student_enroll_subject()` - Enroll in subject (max 4 limit)
    - `student_remove_subject()` - Remove enrolled subject
    - `student_change_password()` - Change password with validation
  
  - **Admin Features**:
    - `admin_list_students()` - List all students with statistics
    - `admin_remove_student()` - Remove student by ID
    - `admin_group_by_grade()` - Group students by dominant grade
    - `admin_partition_pass_fail()` - Partition students by pass/fail status
    - `admin_clear_all()` - Clear all data with confirmation

---

## Person D: GUI Interface
**Focus**: CustomTkinter-based graphical UI, all student features

### Files & Methods:
- **gui.py** (전체)
  - **Frame Builders**:
    - `_build_login()` - Login screen with email/password fields
    - `_build_enrollment()` - Enrollment screen with subject name input
    - `_build_subjects_view()` - Subject list view with marks/grades
    - `_build_remove_subject()` - Remove subject screen with radio buttons
    - `_build_change_password()` - Password change screen
  
  - **Navigation**:
    - `show_login()` - Display login screen
    - `show_enrollment()` - Display enrollment screen
    - `show_subjects()` - Display subjects view
    - `show_remove_subject()` - Display remove subject screen
    - `show_change_password()` - Display password change screen
  
  - **Event Handlers**:
    - `_on_login()` - Handle login button click
    - `_on_enroll()` - Handle enroll button click
    - `_on_remove_subject()` - Handle remove button click
    - `_on_change_password()` - Handle password change button click
  
  - **Helper Methods**:
    - `_refresh_enrollment_buttons()` - Update button states based on enrollment count
    - `_refresh_student_info()` - Update student info display
    - `_show_enrollment_error()` - Show error popup for max 4 subjects

---

## Presentation Flow (20 minutes total)

### **Person A** (5 min): "Data Models & Utilities"
**Demo**:
- Open Python REPL and create Student/Subject instances
- Show ID generation (6-digit student, 3-digit subject)
- Show grade calculation (90→HD, 80→D, 70→C, 55→P, 40→F)
- Show email/password validation with regex

**Code Walkthrough**:
- Student/Subject dataclasses with type annotations
- `generate_unique_id()` algorithm (random.randint with collision check)
- `calculate_grade()` threshold logic
- BCrypt password hashing

---

### **Person B** (5 min): "Database Persistence Layer"
**Demo**:
- Show empty `students.data` file
- Add 2-3 students via Python REPL
- Show JSON structure in `students.data`
- Update student (add subject)
- Remove student, clear all

**Code Walkthrough**:
- `_read_all()` / `_write_all()` with JSON serialization
- `add_student()` with duplicate email check
- `update_student()` with in-place modification
- Error handling for file operations

---

### **Person C** (5 min): "CLI Interface"
**Demo**:
- Launch CLI with `python cli.py`
- Student flow: Register → Login → Enroll 2 subjects → View enrollment → Change password
- Admin flow: List students → Group by grade → Partition pass/fail → Remove student

**Code Walkthrough**:
- Rich Console styling (Colors.SUCCESS, Colors.ERROR)
- Menu navigation with `console.input()`
- `student_enroll_subject()` with MAX_SUBJECTS_PER_STUDENT validation
- `admin_group_by_grade()` with Grades.ORDER sorting

---

### **Person D** (5 min): "GUI Interface"
**Demo**:
- Launch GUI with `python gui.py`
- Login → Enroll 3 subjects → View subjects → Remove 1 subject → Change password
- Show error popup when trying to enroll 5th subject
- Show password mismatch error

**Code Walkthrough**:
- CustomTkinter frame building pattern
- `_build_login()` with Entry widgets and Enter key binding
- `_on_enroll()` with `_show_enrollment_error()` for max 4 validation
- `_refresh_enrollment_buttons()` to disable/enable enroll button

---

## Code Comments Legend
All files/methods are marked with layer assignments:
- `# Person A: Models & Utils (Data Layer)`
- `# Person B: Database Layer`
- `# Person C: CLI Interface`
- `# Person D: GUI Interface`
