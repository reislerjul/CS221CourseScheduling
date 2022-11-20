import pytest

from src.constants import CS_AI_PROGRAM_FILE
from src.course import Course
from src.program_requirements.cs_ai_program import CSAIProgram


COURSES_TO_WAIVE = [
    (
        [
            Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "161", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "107", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
        ],
        set(),
    ),
    (
        [
            Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "106", "AI", "CME", "foundation", (1,)),
        ],
        {"logic", "algorithm", "organ", "systems"},
    ),
    (
        [
            Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
        ],
        {"algorithm", "organ", "probability"},
    ),
]


@pytest.mark.parametrize("courses_to_waive", COURSES_TO_WAIVE)
def test_waive_courses(courses_to_waive):
    program = CSAIProgram(CS_AI_PROGRAM_FILE)

    courses, foundations_left = courses_to_waive
    for course in courses:
        program.waive_course(course)

    assert program.total_requirement_units_taken == 0
    assert program.foundations_areas_left == foundations_left


def test_waive_courses_exception():
    pass
