import pytest

from ..CoursesDeterministic import CoursesDeterministic


COURSE_YEARS = ["2021-2022", "2022-2023", "2023-2024"]


@pytest.mark.parametrize("course_year", COURSE_YEARS)
def test_courses_deterministic_init(course_year, mocker):

    # Mock course_extraction since this takes a long time
    mocker.patch.object(CoursesDeterministic, "course_extraction", return_value=None)
    courses_deterministic = CoursesDeterministic(course_year)

    message = f"Year is not set correctly in CoursesDeterministic! Expected {course_year}, got {courses_deterministic.year}."
    assert courses_deterministic.year == course_year, message
