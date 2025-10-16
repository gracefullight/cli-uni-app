"""
Configuration constants for CLIUniApp.
"""

# ======================== Configuration ========================
MAX_SUBJECTS_PER_STUDENT = 4
PASSING_AVERAGE = 50
DATA_FILE = "students.data"
MAX_LOGIN_ATTEMPTS = 3


# ======================== Grade Constants ========================
class Grades:
    """Grade-related constants"""
    
    HD = "HD"  # High Distinction (85-100)
    D = "D"    # Distinction (75-84)
    C = "C"    # Credit (65-74)
    P = "P"    # Pass (50-64)
    F = "F"    # Fail (0-49)
    
    # Grade thresholds
    THRESHOLDS = {
        HD: 85,
        D: 75,
        C: 65,
        P: 50,
        F: 0
    }
    
    # Grade order (for sorting)
    ORDER = {HD: 4, D: 3, C: 2, P: 1, F: 0}
    
    # All grade categories
    ALL = [HD, D, C, P, F]

