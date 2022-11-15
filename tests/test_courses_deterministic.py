import pytest

from ..courses_deterministic import CoursesDeterministic


COURSE_YEARS = ["2021-2022", "2022-2023", "2023-2024"]


@pytest.mark.parametrize("course_year", COURSE_YEARS)
def test_courses_deterministic_init(course_year, mocker):
    courses_deterministic = CoursesDeterministic([course_year])
    message = f"Year not set correctly in CoursesDeterministic! Expected {[course_year]}, got {courses_deterministic.years}."
    assert courses_deterministic.years == [course_year], message
