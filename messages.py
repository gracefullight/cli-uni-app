"""
Message constants for CLIUniApp.
All user-facing prompts, success/error messages, and format templates.
"""


# ======================== Prompts ========================
class Prompts:
    """User input prompts"""
    
    # University System
    UNIVERSITY = "University System: (A)dmin, (S)tudent, or [X] : "
    
    # Student System
    STUDENT_MENU = "Student System: [L]ogin, [R]egister, or X): "
    
    # Admin System
    ADMIN_MENU = "[C]lear Database, [G]roup Students, [P]artition Students, [R]emove Student, [S]how Students or [X]: "
    
    # Enrollment System
    ENROLLMENT_OPTIONS = "Select an option: "
    
    # Registration
    FIRST_NAME = "First name: "
    LAST_NAME = "Last name: "
    EMAIL = "Email (firstname.lastname@university.com): "
    PASSWORD = "Password (Start uppercase, 5+ letters, end with 3 digits): "
    
    # Login
    LOGIN_EMAIL = "Email: "
    LOGIN_PASSWORD = "Password: "
    
    # Subject
    SUBJECT_NAME = "Subject name: "
    SUBJECT_ID_TO_REMOVE = "Enter Subject ID to remove: "
    
    # Admin
    STUDENT_ID_TO_REMOVE = "Enter Student ID to remove: "
    CONFIRM_CLEAR = "Are you sure you want to clear the database (Y)ES/(N)O?: "
    
    # Password Change
    NEW_PASSWORD = "New password: "
    CONFIRM_PASSWORD = "Confirm password: "


# ======================== Success Messages ========================
class SuccessMessages:
    """Success message templates"""
    
    # Registration
    REGISTER = "Success: Student registered with ID {student_id}."
    
    # Login
    LOGIN = "Welcome, {first_name}!"
    
    # Enrollment
    ENROLL = "Success: Enrolled in {subject_name} with Subject ID {subject_id}. Mark: {mark}, Grade: {grade}"
    ENROLL_COUNT = "You are now enrolled in {count} out of {max_subjects} subjects."
    
    # Subject Removal
    REMOVE_SUBJECT = "Dropping subject {subject_id}"
    
    # Password
    PASSWORD_CHANGED = "Success: Password changed."
    
    # Admin
    STUDENT_REMOVED = "Success: Student removed."
    ALL_CLEARED = "Success: All student data cleared."
    OPERATION_CANCELLED = "Operation cancelled."


# ======================== Error Messages ========================
class ErrorMessages:
    """Error message templates"""
    
    # Validation Errors
    INVALID_EMAIL_FORMAT = "Error: Invalid email format. Expected firstname.lastname@university.com"
    INVALID_PASSWORD_FORMAT = "Error: Invalid password format. Must start uppercase, 5+ letters, end with 3 digits"
    EMAIL_NAME_MISMATCH = "Error: Email name parts must match first and last name provided."
    INVALID_EMAIL_COMPONENTS = "Error: Invalid email format components."
    
    # Registration Errors
    EMAIL_ALREADY_REGISTERED = "Error: Email already registered."
    
    # Login Errors
    INCORRECT_FORMAT = "Incorrect email or password format"
    INVALID_CREDENTIALS = "Error: Invalid email or password."
    TOO_MANY_ATTEMPTS = "Too many failed attempts."
    
    # Subject Errors
    SUBJECT_LIMIT_REACHED = "Error: Subject limit reached ({max_subjects})."
    SUBJECT_NAME_EMPTY = "Error: Subject name cannot be empty."
    SUBJECT_ALREADY_ENROLLED = "Error: Already enrolled in a subject with this name."
    SUBJECT_NOT_FOUND = "Error: Subject not found."
    NO_SUBJECTS_TO_REMOVE = "No subjects to remove."
    
    # Password Errors
    PASSWORD_MISMATCH = "Error: Password does not match."
    
    # Admin Errors
    STUDENT_NOT_FOUND = "Error: Student not found."
    NO_STUDENTS_FOUND = "No students found."
    
    # General Errors
    INVALID_OPTION = "Invalid option. Try again."
    INVALID_STUDENT_OPTION = "Invalid student option. Try again."
    INVALID_ADMIN_OPTION = "Invalid admin option. Try again."


# ======================== Info Messages ========================
class InfoMessages:
    """Informational message templates"""
    
    # Headers
    UNIVERSITY_SYSTEM = "The University System"
    STUDENT_SIGN_UP = "Student Sign Up"
    STUDENT_SIGN_IN = "Student Sign In"
    ADMIN_SYSTEM = "Admin System:"
    ENROLL_IN_SUBJECT = "------ Enroll in Subject ------"
    STUDENT_LIST = "Student List"
    REMOVE_STUDENT = "Remove Student"
    GRADE_GROUPING = "Grade Grouping"
    PASS_FAIL_PARTITION = "PASS/FAIL Partition"
    CLEARING_DATABASE = "Clearing students database"
    UPDATING_PASSWORD = "Updating Password"
    
    # Subject Menu
    STUDENT_COURSE_MENU = "Student Course Menu ({first_name} {last_name} | ID: {student_id})"
    COURSE_MENU_OPTIONS = "[C]hange Password, [E]nroll Subject, [R]emove Subject, [S]how Enrollment, or [X]"
    
    # Subject Display
    SHOWING_SUBJECTS = "Showing {count} subjects"
    NO_SUBJECTS_ENROLLED = "No subjects enrolled."
    AVERAGE_STATUS = "Average: {average:.2f} ({status})"
    
    # Admin Display
    NOTHING_TO_DISPLAY = "<Nothing to Display>"
    NO_STUDENTS_TO_PARTITION = "No students to partition."
    
    # Grade Labels
    GRADE_LABEL = "Grade {grade}:"
    PASS_LABEL = "PASS:"
    FAIL_LABEL = "FAIL:"
    
    # Status
    STATUS_PASS = "PASS"
    STATUS_FAIL = "FAIL"
    
    # Exit
    THANK_YOU = "Thank You"


# ======================== Format Templates ========================
class FormatTemplates:
    """Output format templates"""
    
    # Subject Display
    SUBJECT_ITEM = "[{subject_id}] {name} - Mark: {mark}, Grade: {grade}"
    SUBJECT_LIST_ITEM = "[{subject_id}] {name}"
    
    # Student Display
    STUDENT_DETAIL = "{student_id} | {first_name} {last_name} | {email} | Subjects: {subject_count} | Avg: {average:.2f} ({status})"
    STUDENT_SUMMARY = "  {student_id} | {first_name} {last_name} | Avg {average:.2f}"
    
    # GUI
    GUI_ENROLLMENT_TITLE = "Enrollment - {first_name} {last_name} ({student_id})"
    GUI_STUDENT_INFO = "Subjects: {num_subjects} | Average: {avg:.2f} | Status: {pass_fail}"
    GUI_SUBJECT_ROW = "{subject_id} - {name}"


# ======================== GUI Messages ========================
class GUIMessages:
    """GUI-specific messages"""
    
    # Titles
    LOGIN_TITLE = "Student Login"
    ENROLLMENT_TITLE = "Enrollment"
    SUBJECTS_TITLE = "Subjects"
    REMOVE_SUBJECT_TITLE = "Remove Subject"
    CHANGE_PASSWORD_TITLE = "Change Password"
    
    # Labels
    EMAIL_LABEL = "Email:"
    PASSWORD_LABEL = "Password:"
    NEW_PASSWORD_LABEL = "New password (Start uppercase, 5+ letters, end with 3 digits):"
    CONFIRM_PASSWORD_LABEL = "Confirm password:"
    
    # Placeholders
    EMAIL_PLACEHOLDER = "Firstname.Lastname@university.com"
    
    # Buttons
    LOGIN_BUTTON = "Login"
    EXIT_BUTTON = "Exit"
    ENROLL_BUTTON = "Enroll"
    VIEW_SUBJECTS_BUTTON = "View Subjects"
    REMOVE_SUBJECT_BUTTON = "Remove Subject"
    CHANGE_PASSWORD_BUTTON = "Change Password"
    LOGOUT_BUTTON = "Logout"
    BACK_BUTTON = "Back"
    REMOVE_BUTTON = "Remove"
    SAVE_BUTTON = "Save"
    
    # Table Headers
    SUBJECT_HEADER = "Subject"
    MARK_HEADER = "Mark"
    GRADE_HEADER = "Grade"
    
    # Error Dialog Titles
    LOGIN_ERROR = "Login Error"
    ENROLL_ERROR = "Enroll Error"
    REMOVE_ERROR = "Remove Error"
    PASSWORD_ERROR = "Password Error"
    
    # Error Messages
    EMAIL_PASSWORD_REQUIRED = "Email and password are required."
    INVALID_FORMAT = "Invalid email or password format."
    INVALID_CREDENTIALS = "Invalid credentials or unregistered user."
    NO_STUDENT_LOGGED_IN = "No student logged in."
    STUDENT_NOT_FOUND_GUI = "Student not found."
    MAX_SUBJECTS_EXCEEDED = "Maximum of 4 subjects exceeded."
    SELECT_SUBJECT_TO_REMOVE = "Please select a subject to remove."
    SUBJECT_NOT_FOUND_GUI = "Subject not found."
    PASSWORDS_DO_NOT_MATCH = "New passwords do not match."
    INVALID_PASSWORD_FORMAT_GUI = "Invalid password format."
    
    # Success Messages
    ENROLL_SUCCESS = "Enrolled in {name} (ID {subject_id}) with mark {mark} and grade {grade}."
    SUBJECT_REMOVED = "Subject removed."
    PASSWORD_CHANGED = "Password changed successfully."
    
    # Info
    NO_SUBJECTS_GUI = "No subjects enrolled."
    NO_SUBJECTS_TO_REMOVE_GUI = "No subjects to remove."
    ENROLLMENT_DEFAULT_TITLE = "Enrollment"
    SUBJECT_DEFAULT_NAME = "Subject {number}"


# ======================== Color Styles (for rich console) ========================
class Colors:
    """Color styles for rich console output"""
    
    CYAN = "cyan"
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    
    # Semantic colors
    HEADER = CYAN
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = YELLOW
