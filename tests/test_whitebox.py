
import pytest

from registration import (
    Student,
    Course,
    registration_decision
)


# WB-C01: All capacity conditions allow execution to continue
def test_WB_C01_valid_capacity_conditions():
    student = Student("WB01")
    course = Course("CS101", 3, 1, enrolled=0)

    result = registration_decision(student, course)

    assert result == "REGISTERED"


# WB-C02: First atomic condition is False
def test_WB_C02_negative_enrollment():
    student = Student("WB02")
    course = Course("CS102", 3, 1, enrolled=-1)

    with pytest.raises(ValueError):
        registration_decision(student, course)


# WB-C03: Second atomic condition is False
def test_WB_C03_enrollment_above_capacity():
    student = Student("WB03")
    course = Course("CS103", 3, 1, enrolled=2)

    with pytest.raises(ValueError):
        registration_decision(student, course)


# WB-C04: Third atomic condition is True
def test_WB_C04_zero_capacity():
    student = Student("WB04")
    course = Course("CS104", 3, 0, enrolled=0)

    with pytest.raises(ValueError):
        registration_decision(student, course)


# WB01: Negative dues validation path
def test_WB01_negative_dues():
    student = Student("WB05", outstanding_dues=-1)
    course = Course("CS105", 3, 10)

    with pytest.raises(ValueError):
        registration_decision(student, course)


# WB02: Dues block decision path
def test_WB02_dues_block():
    student = Student("WB06", outstanding_dues=1001)
    course = Course("CS106", 3, 10)

    result = registration_decision(student, course)

    assert result == "DUES_BLOCK"


# WB03: Already registered decision path
def test_WB03_duplicate_registration():
    student = Student(
        "WB07",
        registered_courses={"CS107"}
    )
    course = Course("CS107", 3, 10)

    result = registration_decision(student, course)

    assert result == "ALREADY_REGISTERED"


# WB04: Missing prerequisite decision path
def test_WB04_missing_prerequisite():
    student = Student("WB08")
    course = Course(
        "CS108",
        3,
        10,
        prerequisites={"CS101"}
    )

    result = registration_decision(student, course)

    assert result == "PREREQUISITES_MISSING"


# WB05: Credit limit decision path
def test_WB05_credit_limit_exceeded():
    student = Student("WB09", current_credits=16)
    course = Course("CS109", 3, 10)

    result = registration_decision(student, course)

    assert result == "CREDIT_LIMIT"


# WB06: Successful registration decision path
def test_WB06_successful_registration():
    student = Student("WB10")
    course = Course("CS110", 3, 10)

    result = registration_decision(student, course)

    assert result == "REGISTERED"
