import argparse
from typing import List

from src.courses_deterministic import CoursesDeterministic
from src.constants import DEPARTMENT_REQUIREMENT
from src.search_problem import FindCourses, UniformCostSearch
from src.course import ExploreCourse


def main(
    data_directory: str = "data",
    program: str = "CS",
    years: List[str] = ["2021-2022", "2022-2023"],
    max_quarter: int = 8,
    verbose: int = 0,
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

    # This second argument to ExploreCourse is never used; we could probably do
    # away with ExploreCourse and just pass course_by_quarter to FindCourses
    explore_course = ExploreCourse(course_by_quarter, {})
    department_requirement = DEPARTMENT_REQUIREMENT[program]
    search_problem = FindCourses(
        explore_course, department_requirement, max_quarter=max_quarter
    )
    ucs = UniformCostSearch(verbose=verbose)

    # Step 3: Run UCS to get the optimal schedule.
    print("BEGIN UCS.")
    ucs.solve(search_problem)
    found_solution = ucs.actions is not None and len(ucs.actions) > 0
    print("END UCS. Found {} solution.".format("a" if found_solution else "no"))

    # Step 4: Store and analyze the output.
    print("END Course Scheduling.")


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
        help='The degree program. Should be in {CS, EE, ICME}. Defaults to "CS".',
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
        "-m",
        "--max_quarter",
        type=int,
        default=8,
        help="The maximum number of quarters to graduate in.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        default=0,
        help="Whether to run UCS in verbose mode.",
    )

    args = parser.parse_args()
    main(**vars(args))
