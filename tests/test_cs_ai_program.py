import pandas as pd
import pytest
from typing import List, Set, Tuple

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
        True,
    ),
    (
        [
            Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "106", "AI", "CME", "foundation", (1,)),
        ],
        {"logic", "algorithm", "organ", "systems"},
        False,
    ),
    (
        [
            Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
            Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
        ],
        {"algorithm", "organ", "probability"},
        False,
    ),
]

COURSES_TO_WAIVE_EXCEPTION = [
    Course(0, (3, 4), "229", "AI", "CS", "depth", (1,)),
    Course(0, (3, 4), "271", "AI", "CS", "depth", (1,)),
]

DEPTH_COURSES = [
    (Course(0, (3, 5), "205", "AI", "ENGR", "breadth", (1,)), 4),
    (Course(0, (3, 5), "238", "AI", "CS", "breadth", (1,)), 3),
]


@pytest.fixture
def program() -> CSAIProgram:
    """
    A pytest fixture returning a CSAIProgram object
    """
    df_requirements = pd.read_csv(CS_AI_PROGRAM_FILE)
    return CSAIProgram(df_requirements)


@pytest.fixture
def requirements() -> CSAIProgram:
    """
    A pytest fixture returning a CSAIProgram object
    """
    return pd.read_csv(CS_AI_PROGRAM_FILE)


@pytest.mark.parametrize("courses_to_waive", COURSES_TO_WAIVE)
def test_waive_courses(
    requirements: pd.DataFrame,
    courses_to_waive: Tuple[List[Course], Set, bool],
    program: CSAIProgram,
):
    """
    Check that waving foundation courses works and doesn't decrease the total requirement units left.

    Arguments:
    courses_to_waive: A list containing the courses to waive, the expected value for program.foundations_areas_left,
    and whether or not the foundations are satisfied
    program: a newly initialized CSAIProgram
    """
    courses, foundations_left, foundation_done = courses_to_waive
    for course in courses:
        program.waive_course(requirements, course)

    assert program.total_requirement_units_taken == 0
    assert program.foundations_areas_left == foundations_left
    assert program._is_foundations_satisfied() == foundation_done
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 4
    assert program.depth_units_left == 21
    assert not program.significant_implementation_satisfied


@pytest.mark.parametrize("course_to_waive", COURSES_TO_WAIVE_EXCEPTION)
def test_waive_courses_exception(
    requirements: pd.DataFrame, course_to_waive: Course, program: CSAIProgram
):
    """
    Check that an Exception is raised when trying to wave non-foundation requirements.

    Arguments:
    course_to_waive: A course to waive. This should not be a foundation course.
    program: a newly initialized CSAIProgram
    """
    with pytest.raises(Exception):
        program.waive_course(requirements, course_to_waive)


def test_take_single_foundation_course(
    requirements: pd.DataFrame, program: CSAIProgram
):
    """
    Test that values are set correctly after taking a single foundation course.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    course = Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,))
    units = 5
    program.take_course(requirements, (course, units))

    assert program.total_requirement_units_taken == units
    assert program.foundations_areas_left == {
        "probability",
        "algorithm",
        "organ",
        "systems",
    }
    assert program.foundation_units_counted == 5
    assert not program._is_foundations_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 4
    assert program.depth_units_left == 21
    assert not program.significant_implementation_satisfied


def test_satisfy_foundation(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after taking enough foundation courses to satisfy foundation requirement.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    courses = [
        Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "161", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "107", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
    ]

    for course in courses:
        program.take_course(requirements, (course, 3))

    assert program.total_requirement_units_taken == 10
    assert program.foundations_areas_left == set()
    assert program.foundation_units_counted == 10
    assert program._is_foundations_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 4
    assert program.depth_units_left == 21
    assert not program.significant_implementation_satisfied


def test_take_significant_implementation_course(
    requirements: pd.DataFrame, program: CSAIProgram
):
    """
    Test that values are set correctly after taking a significant implementation course.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    course = Course(0, (3, 5), "151", "AI", "CS", "significant implementation", (1,))
    program.take_course(requirements, (course, 3))

    assert program.total_requirement_units_taken == 3
    assert len(program.foundations_areas_left) == 5
    assert program.foundation_units_counted == 0
    assert program._is_significant_implementation_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 4
    assert program.depth_units_left == 21
    assert program.significant_implementation_satisfied


def test_take_breadth_course(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after taking a breadth course.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    course = Course(0, (3, 5), "166", "AI", "COMM", "breadth", (1,))
    program.take_course(requirements, (course, 3))

    assert program.total_requirement_units_taken == 3
    assert len(program.foundations_areas_left) == 5
    assert program.foundation_units_counted == 0
    assert not program._is_breadth_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert program.breadth_areas_left == {"theory", "systems", "applications"}
    assert program.depth_units_left == 21
    assert not program.significant_implementation_satisfied


def test_satisfy_breadth(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after taking enough breadth courses to satisfy the requirement.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    courses = [
        Course(0, (3, 5), "166", "AI", "COMM", "breadth", (1,)),
        Course(0, (3, 5), "251", "AI", "PHIL", "breadth", (1,)),
        Course(0, (3, 5), "180", "AI", "EE", "breadth", (1,)),
    ]

    for course in courses:
        program.take_course(requirements, (course, 4))

    assert program.total_requirement_units_taken == 12
    assert len(program.foundations_areas_left) == 5
    assert program.foundation_units_counted == 0
    assert program._is_breadth_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert program.breadth_areas_left == {"applications"}
    assert program.depth_units_left == 21
    assert not program.significant_implementation_satisfied


@pytest.mark.parametrize("depth_course", DEPTH_COURSES)
def test_take_depth_course(
    requirements: pd.DataFrame, depth_course: Tuple[Course, int], program: CSAIProgram
):
    """
    Test that values are set correctly after taking a depth course.

    Arguments:
    depth_course: A depth course to take and the expected value for program.depth_areas_left["b"]
    program: a newly initialized CSAIProgram
    """
    course, b = depth_course
    program.take_course(requirements, (course, 4))

    assert program.total_requirement_units_taken == 4
    assert len(program.foundations_areas_left) == 5
    assert program.foundation_units_counted == 0
    assert not program._is_depth_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 4
    assert program.depth_units_left == 17
    assert program.depth_areas_left["a"] == 1
    assert program.depth_areas_left["b"] == b
    assert not program.significant_implementation_satisfied


def test_satisfy_depth(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after satisfying depth requirements.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    courses = [
        Course(0, (3, 5), "238", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "237B", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224V", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224S", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "221", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "205", "AI", "ENGR", "breadth", (1,)),
    ]
    for course in courses:
        program.take_course(requirements, (course, 4))

    assert program.total_requirement_units_taken == 24
    assert len(program.foundations_areas_left) == 5
    assert program.foundation_units_counted == 0
    assert program._is_depth_satisfied()
    assert not program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) == 3
    assert program.depth_units_left <= 0
    assert program.depth_areas_left["a"] <= 0
    assert program.depth_areas_left["b"] <= 0
    assert program.depth_areas_left["c"] <= 0
    assert program.significant_implementation_satisfied


def test_satisfy_degree_no_waivers(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after satisfying the degree program with no waivers.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    courses = [
        Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "161", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "107", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "238", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "237B", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224V", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224S", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "221", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "205", "AI", "ENGR", "breadth", (1,)),
        Course(0, (3, 5), "166", "AI", "COMM", "breadth", (1,)),
        Course(0, (3, 5), "251", "AI", "PHIL", "breadth", (1,)),
        Course(0, (3, 5), "180", "AI", "EE", "breadth", (1,)),
    ]
    for course in courses:
        program.take_course(requirements, (course, 4))

    assert program.total_requirement_units_taken == 46
    assert len(program.foundations_areas_left) == 0
    assert program.foundation_units_counted == 10
    assert program.is_program_satisfied()
    assert program.seminar_units_taken == 0
    assert len(program.breadth_areas_left) <= 1
    assert program.depth_units_left <= 0
    assert program.depth_areas_left["a"] <= 0
    assert program.depth_areas_left["b"] <= 0
    assert program.depth_areas_left["c"] <= 0
    assert program.significant_implementation_satisfied


def test_satisfy_degree_three_waivers(requirements: pd.DataFrame, program: CSAIProgram):
    """
    Test that values are set correctly after satisfying the degree program with 3 waivers.

    Arguments:
    program: a newly initialized CSAIProgram
    """
    waived_courses = [
        Course(0, (3, 5), "109", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "103", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "161", "AI", "CS", "foundation", (1,)),
    ]
    for course in waived_courses:
        program.waive_course(requirements, course)

    courses_taken = [
        Course(0, (3, 5), "107", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "110", "AI", "CS", "foundation", (1,)),
        Course(0, (3, 5), "238", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "237B", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224V", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "224S", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "221", "AI", "CS", "breadth", (1,)),
        Course(0, (3, 5), "205", "AI", "ENGR", "breadth", (1,)),
        Course(0, (3, 5), "166", "AI", "COMM", "breadth", (1,)),
        Course(0, (3, 5), "251", "AI", "PHIL", "breadth", (1,)),
        Course(0, (3, 5), "180", "AI", "EE", "breadth", (1,)),
    ]
    seminars_taken = [Course(0, (1, 2), "300", "AI", "CS", "seminar", (1,))]

    for course in courses_taken:
        program.take_course(requirements, (course, 4))

    for seminar in seminars_taken:
        program.take_course(requirements, (seminar, 1))

    assert program.total_requirement_units_taken == 45
    assert len(program.foundations_areas_left) == 0
    assert program.foundation_units_counted == 8
    assert program.is_program_satisfied()
    assert program.seminar_units_taken == 1
    assert len(program.breadth_areas_left) <= 1
    assert program.depth_units_left <= 0
    assert program.depth_areas_left["a"] <= 0
    assert program.depth_areas_left["b"] <= 0
    assert program.depth_areas_left["c"] <= 0
    assert program.significant_implementation_satisfied
