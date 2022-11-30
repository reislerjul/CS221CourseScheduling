import argparse
import os
import pandas as pd
from typing import Dict, List
import yaml  # type: ignore[import]
import random

from src.constants import (
    CONFIG_FOLDER,
    CS_AI_PROGRAM_FILE,
    DEPARTMENT_REQUIREMENT,
    INDEX_QUARTER,
)
from src.courses_deterministic import CoursesDeterministic
from src.course import Course, ExploreCourse
from src.search_problem import FindCourses, UniformCostSearch
from src.csp import SchedulingCSPConstructor, BacktrackingSearch
from src.program_requirements.cs_ai_program import CSAIProgram


def get_course_id_to_name(courses_by_quarter):
    course_id_to_name = {}
    for _, courses in courses_by_quarter.items():
        for course in courses:
            course_id = f"{course.course_subject} {course.course_number}"
            course_id_to_name[course_id] = course.course_name
    return course_id_to_name


def get_one_unit_seminar_courses(courses_by_quarter):
    seminars = {}
    for quarter_index, courses in courses_by_quarter.items():
        seminars[quarter_index] = []
        for course in courses:
            course_id = f"{course.course_subject} {course.course_number}"
            if (
                CSAIProgram._is_seminar_course(course_id)
                and course.units[0] >= 1
                and course.units[0] <= 2
            ):
                seminars[quarter_index].append(course)
    return seminars


def main(
    data_directory: str = "data",
    program: str = "CS",
    years: List[str] = ["2021-2022", "2022-2023"],
    max_quarter: int = 8,
    max_successors: int = 5,
    model: str = "CSP",
    config_name: str = "profile1.yaml",
    internship: bool = True,
    verbose: int = 4,
):
    """
    Runs the course scheduling program.

    Arguments:
    data_directory (str) - The local directory where course data is stored.
    program (str) - the academic year that the course is offered.
    years (List[str]) - The program years.
    """
    print(f"BEGIN Course Scheduling for program: {program} and years: {years}.")

    # Step 1: Load in the course data.
    course_loader = CoursesDeterministic(
        output_dir=data_directory, departments=[program], years=years
    )
    course_by_quarter = course_loader.run()
    print(f"Populated {len(course_by_quarter)} quarters.")

    # Step 2: Initialize the problem.
    if model not in {"CSP", "search"}:
        raise Exception(f"model {model} not implemented!")
    # This second argument to ExploreCourse is never used; we could probably do
    # away with ExploreCourse and just pass course_by_quarter to FindCourses
    if model == "search":
        explore_course = ExploreCourse(course_by_quarter, {})
        department_requirement = DEPARTMENT_REQUIREMENT[program]
        search_problem = FindCourses(
            explore_course,
            department_requirement,
            max_quarter=max_quarter,
            max_successors=max_successors,
            internship=internship,
            verbose=verbose,
        )
        ucs = UniformCostSearch(verbose=verbose)

        # Step 3: Run UCS to get the optimal schedule.
        print("BEGIN UCS.")
        ucs.solve(search_problem)
        found_solution = ucs.actions is not None and len(ucs.actions) > 0
        print("END UCS. Found {} solution.".format("a" if found_solution else "no"))

        # Step 4: Store and analyze the output.
        if ucs.actions is not None:
            print("PRINTING course schedule...")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
            for i in range(len(ucs.actions)):
                season = INDEX_QUARTER[i % len(INDEX_QUARTER)]
                print(f"** Quarter: {i + 1}, Season: {season} **")

                for course, units in ucs.actions[i]:

                    print(
                        f"Course: {course.course_number} {course.course_name} || Units: {units}"
                    )

                if not ucs.actions[i]:
                    print("Taking this quarter off! :(")

                print()
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("END Course Scheduling.")

    elif model == "CSP":
        # Load config from yaml file
        config_filepath = os.path.join(CONFIG_FOLDER, config_name)

        if not os.path.exists(config_filepath):
            raise Exception(f"Invalid config path! {config_filepath} does not exist!")

        with open(config_filepath, "r") as file:
            student_config = yaml.safe_load(file)

        internship = student_config["internship"]
        breadth_to_satisfy = student_config["breadth_areas"]
        foundations_not_satisfied = (
            student_config["foundations_not_satisfied"]
            if student_config["foundations_not_satisfied"]
            else []
        )
        custom_requests = student_config["subject_requests"]

        if len(breadth_to_satisfy) != 2:
            raise Exception(
                f"Must specify 2 breadth areas! Got {len(breadth_to_satisfy)}"
            )

        if len(foundations_not_satisfied) > 2:
            raise Exception(
                f"Can only handle up to 2 unsatisfied foundations! Got {len(foundations_not_satisfied)}"
            )

        # Filter to courses that satisfy CS program requirements (not including electives)
        df_requirements = pd.read_csv(CS_AI_PROGRAM_FILE)

        # Remove foundations that are already satisfied
        foundations_satisfied = {
            "logic",
            "probability",
            "algorithm",
            "organ",
            "foundation systems",
        } - set(foundations_not_satisfied)
        df_requirements = df_requirements.loc[
            ~df_requirements["Subcategory"].isin(foundations_satisfied)
        ]

        courses_by_quarter_filtered: Dict[int, List[Course]] = {}
        requirement_courses = set(df_requirements["Course"])
        for quarter_index, courses in course_by_quarter.items():
            courses_by_quarter_filtered[quarter_index] = []

            for course in courses:
                course_code = f"{course.course_subject} {course.course_number}"
                if course_code in requirement_courses:
                    courses_by_quarter_filtered[quarter_index].append(course)

        # No summer quarter after second year
        del courses_by_quarter_filtered[8]

        # Remove the summer quarter if student is doing an internship
        if internship:
            del courses_by_quarter_filtered[4]

        natural_language_keywords = ["natural language", "language understanding"]
        nlp_courses = set()
        for quarter_index, courses in courses_by_quarter_filtered.items():
            for course in courses:
                for keyword in natural_language_keywords:
                    if keyword in course.course_description.lower():
                        nlp_courses.add(
                            f"{course.course_subject} {course.course_number}"
                        )
                        break

        robotics_keywords = ["robot"]
        robotics_courses = set()
        for quarter_index, courses in courses_by_quarter_filtered.items():
            for course in courses:
                for keyword in robotics_keywords:
                    if keyword in course.course_name.lower():
                        robotics_courses.add(
                            f"{course.course_subject} {course.course_number}"
                        )
                        break

        print("START constructing CSP")
        cspConstructor = SchedulingCSPConstructor(
            courses_by_quarter_filtered,
            df_requirements,
            breadth_to_satisfy,
            foundations_not_satisfied,
            nlp_courses,
            robotics_courses,
            custom_requests,
        )
        csp = cspConstructor.get_csp()
        print("FINISHED constructing CSP")

        print("START solving CSP")
        alg = BacktrackingSearch()
        alg.solve(csp, mcv=True, ac3=True)
        print("FINISHED solving CSP")

        if len(alg.allOptimalAssignments) >= 1:
            assignment = alg.allOptimalAssignments[0]
            course_id_to_name = get_course_id_to_name(courses_by_quarter_filtered)
            seminar_courses_one_unit = get_one_unit_seminar_courses(course_by_quarter)
            seminars_taken = set()

            print("PRINTING course schedule...")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
            for i in range(7):

                season = INDEX_QUARTER[i % len(INDEX_QUARTER)]
                print(f"** Quarter: {i + 1}, Season: {season} **")

                quarter_schedule = assignment.get(f"Quarter {i + 1} classes")

                if not quarter_schedule:
                    print("Taking this quarter off!")
                else:
                    for course in quarter_schedule:
                        print(
                            f"Course: {course} {course_id_to_name[course]} || Units: 4"
                        )

                    take_seminar = random.random() <= 0.5
                    if take_seminar:
                        seminar_courses_quarter = seminar_courses_one_unit[i + 1]
                        seminar = random.sample(seminar_courses_quarter, 1)[0]
                        seminar_id = f"{seminar.course_subject} {seminar.course_number}"
                        print(f"Course: {seminar_id} {seminar.course_name} || Units: 1")
                        seminars_taken.add(seminar)

                print()

            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("END Course Scheduling.")
        else:
            print("CSP is unsolvable!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ScheduleCourses",
        description="Create a course schedule for a two year Stanford MS program.",
    )
    parser.add_argument(
        "-d",
        "--data_directory",
        type=str,
        default="data",
        help='The local directory where course data is stored. Defaults to "data/".',
    )
    parser.add_argument(
        "-p",
        "--program",
        type=str,
        default="CS",
        help='The degree program. Should be in {CS, EE, CME}. Defaults to "CS".',
    )
    parser.add_argument(
        "-y",
        "--years",
        type=str,
        default=["2021-2022", "2022-2023"],
        help='The program years. Each year should be formatted as <YYYY>-<YYYY>. Defaults to "2021-2022 2022-2023".',
        nargs="+",
    )
    parser.add_argument(
        "-mq",
        "--max_quarter",
        type=int,
        default=8,
        help="The maximum number of quarters to graduate in.",
    )
    parser.add_argument(
        "-ms",
        "--max_successors",
        type=int,
        default=5,
        help="The maximum number of successors to return from successors_and_cost.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="search",
        help="Whether to model the problem as a search problem or CSP.",
    )
    parser.add_argument(
        "-c",
        "--config_name",
        type=str,
        default="profile1.yaml",
        help="The config filename corresponding to a student's schedule requests.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        default=4,
        help="Whether to run UCS in verbose mode.",
    )

    args = parser.parse_args()
    main(**vars(args))
