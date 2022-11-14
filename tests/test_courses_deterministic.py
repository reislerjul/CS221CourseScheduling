import pytest

from ..CoursesDeterministic import CoursesDeterministic


COURSE_YEARS = ["2021-2022", "2022-2023", "2023-2024"]
QUARTERS= [] # Needs to be defined for test_courses_deterministic_no_empty_quarters

@pytest.mark.parametrize("course_year", COURSE_YEARS)
def test_courses_deterministic_init(course_year, mocker):
    """
    Ensure CoursesDeterministic is initializing with only years from COURSE_YEARS
    """
    # Mock course_extraction since this takes a long time
    mocker.patch.object(CoursesDeterministic, "course_extraction", return_value=None)
    courses_deterministic = CoursesDeterministic(course_year)

    message = f"Year is not set correctly in CoursesDeterministic! Expected {course_year}, got {courses_deterministic.year}."
    assert courses_deterministic.year == course_year, message

# May want this to be for every quarter and every year?
@pytest.mark.parametrize("quarters", QUARTERS)
def test_courses_deterministic_no_empty_quarters():
    """
    Ensure every quarter that CoursesDeterministic initializes has courses available to take
    """
    raise NotImplementedError("Not implemented yet.")


@pytest.mark.parametrize("quarters", QUARTERS)
def test_courses_deterministic_object_not_modified():
    """
    Ensure this class is not modified during the program run by confirming it is identical at the end to the beginning
    """
    raise NotImplementedError("Not implemented yet.")