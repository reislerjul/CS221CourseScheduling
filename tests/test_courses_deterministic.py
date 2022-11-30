import pytest
import csv
import re

from src.courses_deterministic import CoursesDeterministic

COURSE_YEARS = ["2021-2022", "2022-2023", "2023-2024"]
DEPARTMENTS = ["CS", "EE", "CME"]
QUARTER_TO_INDEX = {
    "Autumn": 1,
    "Winter": 2,
    "Spring": 3,
    "Summer": 4,
}


def get_courses_to_categories():
    """
    Used by test_find_course_category

    Returns: Dict mapping course number to foundation, breadth, elective etc
    as per cs_requirements.csv

    """
    csv_contents = {}
    with open("../data/cs_requirements.csv") as course_reqs:
        for line in csv.reader(course_reqs):
            line = line[0].split()
            csv_contents[line[1]] = line[2]
    return csv_contents


def get_courses_by_term():
    """
    Used by test_find_course_category

    Returns: Dict mapping course number to terms when offered
    as per 2022-2023.csv

    """
    csv_contents = {}
    with open("../data/2022-2023_CS.csv") as courses_terms:
        next(courses_terms)
        for line in csv.reader(courses_terms):
            course_num = line[3]
            terms_split = line[5].split(",")
            terms = []
            for term in terms_split:
                terms.append("".join(re.split("[^a-zA-Z]*", term)))
            csv_contents[course_num] = terms
    return csv_contents


def database_helper():
    db = CoursesDeterministic(["2022-2023"], read_file_loc="./data/cs_requirements.csv")
    db = db.run()
    return db


COURSES_TO_CATEGORIES = get_courses_to_categories()

TERMS_EACH_COURSE_IS_OFFERED = get_courses_by_term()

DATABASE = database_helper()


@pytest.mark.parametrize("course_year", COURSE_YEARS)
def test_years_courses_deterministic_init(course_year, mocker):
    """
    Confirms that CoursesDeterministic is only initializing with the specified course years.

    """
    courses_deterministic = CoursesDeterministic([course_year])
    message = f"Year not set correctly in CoursesDeterministic! Expected {[course_year]}, got {courses_deterministic.years}."
    assert courses_deterministic.years == [course_year], message


@pytest.mark.parametrize("course", COURSES_TO_CATEGORIES.keys())
def test_find_course_category(course):
    """
    Confirm that for every course, CoursesDeterministic is allocating it to the correct category
    based upon requirements.csv as the source of truth.
    Note - currently only checking cs_requirements.csv

    """
    courses_deterministic = CoursesDeterministic(
        ["2022-2023"], read_file_loc="./data/cs_requirements.csv"
    )
    test_response = courses_deterministic.find_course_category(course)
    message = (
        f"Category error in CoursesDeterministic.find_course_category()! For {course}, "
        f"expected {COURSES_TO_CATEGORIES[course]}, got {test_response}."
    )
    assert (
        courses_deterministic.find_course_category(course)
        == COURSES_TO_CATEGORIES[course]
    ), message


@pytest.mark.parametrize("course", TERMS_EACH_COURSE_IS_OFFERED.keys())
def test_course_to_class_database(course):
    """
    Confirm that for every course, course_to_class_database is correctly recording
    the terms in which it is offered. Source of truth is the csv created by CoursesDeterministic.

    """
    test_response = DATABASE
    terms_to_check = TERMS_EACH_COURSE_IS_OFFERED[course]
    for term in terms_to_check:
        term_index = QUARTER_TO_INDEX[term]
        message = (
            f"Error in CoursesDeterministic.course_to_class_database()! For {course}, "
            f"expected {term_index}, got {test_response[term]}."
        )
        present = False
        for candidates in test_response[term_index]:
            if candidates.course_number == course:
                present = True
                break
        assert present, message
