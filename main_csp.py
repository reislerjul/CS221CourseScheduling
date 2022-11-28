# import random

# import graderUtil
from src.util import (
    CourseBulletin,
    Profile,
    extract_course_scheduling_solution,
    print_course_scheduling_solution,
)

# import collections
import copy
from src.csp_problem import SchedulingCSPConstructor, BacktrackingSearch

# import argparse
from typing import List

# import os

from src.courses_deterministic import CoursesDeterministic

# from src.constants import DEPARTMENT_REQUIREMENT, INDEX_QUARTER

# from search_problem import FindCourses
from src.course import ExploreCourse

data_directory: str = "data"
program: str = "CS"
years: List[str] = ["2021-2022", "2022-2023"]
max_quarter: int = 8
verbose: int = 0
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
bulletin = CourseBulletin(explore_course)
# print(bulletin.courses)
profile = Profile(bulletin, "src/profile.txt")
# print(profile.requests)
cspConstructor = SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
csp = cspConstructor.get_basic_csp()
# cspConstructor.add_unit_constraints(csp, bulletin)
# cspConstructor.add_quarter_constraints(csp)
alg = BacktrackingSearch()
alg.solve(csp)

if alg.optimalAssignment:
    print((alg.optimalWeight))
    # for key, value in list(alg.optimalAssignment.items()):
    # print((key, '=', value))

for assignment in alg.allOptimalAssignments:
    solution = extract_course_scheduling_solution(profile, assignment)
    if solution:
        # displays one of the best assignments
        print_course_scheduling_solution(solution)
        break
    elif alg.numOptimalAssignments == 1:
        print("The best schedule is to take 0 units every quarter.")
