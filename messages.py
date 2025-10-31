"""
Message constants for CLIUniApp.
All user-facing prompts, success/error messages, and format templates.
"""


# ======================== Prompts ========================
class Prompts:
    """User input prompts"""

    # University System
    UNIVERSITY = "University System: (A)dmin, (S)tudent, or X : "

    # Student System
    STUDENT_MENU = "Student System: (l/r/x): "

    # Enrollment System
    ENROLLMENT_OPTIONS = "Select an option: "

    # Login
    LOGIN_EMAIL = "Email: "
    LOGIN_PASSWORD = "Password: "
    
    # Subject
    SUBJECT_ID_TO_REMOVE = "Remove Subject by ID: "
    
    # Admin
    STUDENT_ID_TO_REMOVE = "\tRemove by ID: "
    CONFIRM_CLEAR = "Are you sure you want to clear the database (Y)ES/(N)O: "
    
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
    ENROLL = "Enrolling in Subject-{subject_id}"
    ENROLL_COUNT = "You are now enrolled in {count} out of {max_subjects} subjects."
    
    # Subject Removal
    REMOVE_SUBJECT = "Dropping Subject-{subject_id}"
    
    # Password
    PASSWORD_CHANGED = "Password changed."
    
    # Admin
    ALL_CLEARED = "Students data cleared."


# ======================== Error Messages ========================
class ErrorMessages:
    """Error message templates"""
    
    # Registration Errors
    EMAIL_ALREADY_REGISTERED = "Student {first_name} {last_name} already exists."
    
    # Login Errors
    TOO_MANY_ATTEMPTS = "Too many failed attempts."

    # Subject Errors
    NO_SUBJECTS_TO_REMOVE = "No subjects to remove."

    # General Errors
    INVALID_OPTION = "Invalid option. Try again."
    INVALID_ADMIN_OPTION = "Invalid admin option. Try again."


# ======================== Info Messages ========================
class InfoMessages:
    """Informational message templates"""
    
    # Headers
    STUDENT_SIGN_UP = "Student Sign Up"
    STUDENT_SIGN_IN = "Student Sign In"
    ADMIN_SYSTEM = "Admin System (c/g/p/r/s/x): "
    ENROLL_IN_SUBJECT = "------ Enroll in Subject ------"
    STUDENT_LIST = "Student List"
    GRADE_GROUPING = "Grade Grouping"
    PASS_FAIL_PARTITION = "PASS/FAIL Partition"
    CLEARING_DATABASE = "Clearing students database"
    UPDATING_PASSWORD = "Updating Password"
    
    # Subject Menu
    STUDENT_COURSE_MENU = "Student Course Menu (c/e/r/s/x): "
    
    # Subject Display
    SHOWING_SUBJECTS = "Showing {count} subjects"
    NO_SUBJECTS_ENROLLED = "No subjects enrolled."
    AVERAGE_STATUS = "Average: {average:.2f} ({status})"
    
    # Admin Display
    NOTHING_TO_DISPLAY = "< Nothing to Display >"
    
    # Status
    STATUS_PASS = "PASS"
    STATUS_FAIL = "FAIL"

    # Exit
    THANK_YOU = "Thank You"


# ======================== Format Templates ========================
class FormatTemplates:
    """Output format templates"""
    
    # Subject Display
    SUBJECT_ITEM = "[ Subject::{subject_id} -- Mark = {mark} -- Grade = {grade:>3} ]"
    SUBJECT_LIST_ITEM = "[{subject_id}] {name}"
    
    # Student Display
    STUDENT_DETAIL = "{first_name} {last_name} :: {student_id} --> Email: {email}"
    STUDENT_SUMMARY = "{first_name} {last_name} :: {student_id} --> GRADE: {grade} - MARK: {average:.2f}"
    
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

    # Error Dialog Titles
    LOGIN_ERROR = "Login Error"
    ENROLL_ERROR = "Enroll Error"
    REMOVE_ERROR = "Remove Error"
    PASSWORD_ERROR = "Password Error"
    
    # Error Messages
    NO_STUDENT_LOGGED_IN = "No student logged in."
    
    # Success Messages
    ENROLL_SUCCESS = "Enrolled in {name} (ID {subject_id}) with mark {mark} and grade {grade}."
    SUBJECT_REMOVED = "Subject removed."
    PASSWORD_CHANGED = "Password changed successfully."
    
    # Info
    NO_SUBJECTS_GUI = "No subjects enrolled."
    NO_SUBJECTS_TO_REMOVE_GUI = "No subjects to remove."
    ENROLLMENT_DEFAULT_TITLE = "Enrollment"


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
