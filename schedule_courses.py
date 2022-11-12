import argparse
from typing import List


def main(
    data_directory: str = "data",
    program: str = "CS",
    years: List[str] = ["2021-2022", "2022-2023"],
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
    # course_loader = CoursesDeterministic(data_directory=data_directory, program=program, years=years)
    # course_loader.run()

    # Step 2: Initialize the problem.

    # Step 3: Run UCS to get the optimal schedule.

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

    args = parser.parse_args()
    main(**vars(args))
