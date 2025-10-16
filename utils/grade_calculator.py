"""Grade calculation utility for Subject model."""

from constants import Grades


# Member 2: Responsible for Subject Enrollment and Grade Calculation
def calculate_grade(mark: int) -> str:
    """Return grade string based on mark."""
    if mark >= Grades.THRESHOLDS[Grades.HD]:
        return Grades.HD
    if mark >= Grades.THRESHOLDS[Grades.D]:
        return Grades.D
    if mark >= Grades.THRESHOLDS[Grades.C]:
        return Grades.C
    if mark >= Grades.THRESHOLDS[Grades.P]:
        return Grades.P
    return Grades.F