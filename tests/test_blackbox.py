import pytest

from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course
)


# ECP tests

def test_ECP01_BVA15_zero_dues_allow_registration():
    student = Student("S01", outstanding_dues=0)
    course = Course("CS101", 3, 10)
    assert registration_decision(student, course) == "REGISTERED"


def test_ECP02_BVA16_one_rupee_dues_block_registration():
    student = Student("S02", outstanding_dues=1)
    course = Course("CS101", 3, 10)
    assert registration_decision(student, course) == "DUES_BLOCK"


def test_ECP03_negative_dues_are_invalid():
    student = Student("S03", outstanding_dues=-1)
    course = Course("CS101", 3, 10)
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


def test_ECP04_no_prerequisite_is_valid():
    assert prerequisites_satisfied(set(), set()) is True


def test_ECP05_all_prerequisites_completed():
    assert prerequisites_satisfied({"CS101", "MA101"}, {"CS101"}) is True


def test_ECP06_one_prerequisite_missing():
    assert prerequisites_satisfied({"CS101"}, {"CS101", "MA101"}) is False


def test_ECP07_course_not_registered_before():
    student = Student("S07")
    course = Course("CS101", 3, 10)
    assert registration_decision(student, course) == "REGISTERED"


def test_ECP08_course_already_registered():
    student = Student("S08", registered_courses={"CS101"})
    course = Course("CS101", 3, 10)
    assert registration_decision(student, course) == "ALREADY_REGISTERED"


def test_ECP09_BVA11_one_seat_left():
    student = Student("S09")
    course = Course("CS101", 3, 10, enrolled=9)
    assert registration_decision(student, course) == "REGISTERED"


def test_ECP10_BVA12_course_at_capacity():
    student = Student("S10")
    course = Course("CS101", 3, 10, enrolled=10)
    assert registration_decision(student, course) == "WAITLISTED"


# BVA tests

def test_BVA01_current_credits_at_zero():
    assert check_credit_limit(0, 1) is True


def test_BVA02_current_credits_at_eighteen():
    assert check_credit_limit(18, 1) is False


def test_BVA03_current_credits_below_zero():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 1)


def test_BVA04_current_credits_above_eighteen():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 1)


def test_BVA05_course_credit_at_one():
    assert check_credit_limit(0, 1) is True


def test_BVA06_course_credit_at_four():
    assert check_credit_limit(14, 4) is True


def test_BVA07_course_credit_below_one():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(0, 0)


def test_BVA08_course_credit_above_four():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(0, 5)


def test_BVA09_total_credits_exactly_eighteen():
    assert check_credit_limit(15, 3) is True


def test_BVA10_total_credits_one_over_limit():
    assert check_credit_limit(16, 3) is False


def test_BVA13_course_enrollment_above_capacity():
    student = Student("S13")
    course = Course("CS201", 3, 10, enrolled=11)
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_BVA14_course_capacity_is_zero():
    student = Student("S14")
    course = Course("CS201", 3, 0)
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


# Decision table and priority tests

def test_DT01_all_conditions_allow_registration():
    student = Student("S17")
    course = Course("CS401", 3, 10)
    assert registration_decision(student, course) == "REGISTERED"


def test_DT02_dues_have_first_priority():
    student = Student("S18", outstanding_dues=10, registered_courses={"CS401"})
    course = Course("CS401", 3, 10, prerequisites={"CS100"})
    assert registration_decision(student, course) == "DUES_BLOCK"


def test_DT03_duplicate_has_priority_over_prerequisites():
    student = Student("S19", registered_courses={"CS401"})
    course = Course("CS401", 3, 10, prerequisites={"CS100"})
    assert registration_decision(student, course) == "ALREADY_REGISTERED"


def test_DT04_prerequisite_has_priority_over_credit_limit():
    student = Student("S20", current_credits=18)
    course = Course("CS402", 3, 10, prerequisites={"CS100"})
    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


def test_DT05_credit_limit_has_priority_over_full_seat():
    student = Student("S21", current_credits=18)
    course = Course("CS403", 3, 1, enrolled=1)
    assert registration_decision(student, course) == "CREDIT_LIMIT"


def test_DT06_full_seat_waitlists_eligible_student():
    student = Student("S22")
    course = Course("CS404", 3, 1, enrolled=1)
    assert registration_decision(student, course) == "WAITLISTED"


def test_DT07_missing_prerequisite_is_returned():
    student = Student("S23")
    course = Course("CS405", 3, 10, prerequisites={"CS100"})
    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


# State change tests

def test_STATE01_successful_registration_updates_all_values():
    student = Student("S24")
    course = Course("CS501", 3, 10)
    result = register_course(student, course)
    assert result == "REGISTERED"
    assert student.registered_courses == {"CS501"}
    assert student.current_credits == 3
    assert course.enrolled == 1


def test_STATE02_waitlist_adds_student_without_enrolling():
    student = Student("S25")
    course = Course("CS502", 3, 1, enrolled=1)
    result = register_course(student, course)
    assert result == "WAITLISTED"
    assert course.waitlist == ["S25"]
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 1


def test_STATE03_waitlist_does_not_add_same_student_twice():
    student = Student("S26")
    course = Course("CS503", 3, 1, enrolled=1, waitlist=["S26"])
    register_course(student, course)
    assert course.waitlist == ["S26"]


def test_STATE04_failed_registration_does_not_change_data():
    student = Student("S27", outstanding_dues=5)
    course = Course("CS504", 3, 10)
    result = register_course(student, course)
    assert result == "DUES_BLOCK"
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 0
    assert course.waitlist == []


def test_STATE05_withdrawal_updates_student_and_course():
    student = Student("S28", current_credits=3, registered_courses={"CS505"})
    course = Course("CS505", 3, 10, enrolled=1)
    assert withdraw_course(student, course) is True
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 0


def test_STATE06_unsuccessful_withdrawal_changes_nothing():
    student = Student("S29", current_credits=3)
    course = Course("CS506", 3, 10, enrolled=2)
    assert withdraw_course(student, course) is False
    assert student.registered_courses == set()
    assert student.current_credits == 3
    assert course.enrolled == 2


def test_STATE07_registration_decision_does_not_change_data():
    student = Student("S30")
    course = Course("CS507", 3, 10)
    assert registration_decision(student, course) == "REGISTERED"
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 0
