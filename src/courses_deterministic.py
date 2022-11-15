import pickle
import collections
import os
import pandas as pd
from explorecourses import CourseConnection
from .course import Course

from typing import Dict, List

QUARTER_TO_INDEX = {
    "Autumn": 1,
    "Winter": 2,
    "Spring": 3,
    "Summer": 4,
}


class CoursesDeterministic:
    """
    A Courses Deterministic Class use explorecourse API to grab the courses from each department (CS, EE, and ICME).

    The data pulled in this class will be used to populate the Course and ExploreCourse class
    """

    def __init__(
        self,
        years=["2021-2022", "2022-2023"],
        departments=["CS", "EE", "CME"],
        output_dir="course_info",
    ):
        """
        years: a list of possible academic year that the course is offered. Every year interval should be 1 year.

        departments: a list of departments that we want to extract for course planning.

        output_dir: the directory that saves the extracted course info
        """
        self.connect = CourseConnection()
        # Sort the years first so that the following course mapping is in sequence
        self.years = sorted(years)
        self.depts = departments
        self.output_dir = output_dir
        # self.all_courses is used for easier lookup between course number and course object
        self.all_courses = {}

    def run(self):
        """
        Currently only extracting courses from CS, EE and ICME department

        Check if course information pickle exists: if yes, extract from explorecourses api;
        extract from file otherwise. Output courses sorted by year and department in
        self.output_dir/{year}_{dept}.pickle
        """
        # Store the information extracted from explorecourses api to .csv files for easier lookup

        if not os.path.exists(self.output_dir):
            print("Creating new path to ", self.output_dir)
            os.makedirs(self.output_dir)

        for year in self.years:
            for dept in self.depts:

                year_dept_filepath = os.path.join(
                    self.output_dir, f"{year}_{dept}.pickle"
                )

                if not os.path.exists(year_dept_filepath):
                    print(
                        f"No pickle file available for {year} {dept}, will extract from explorecourses."
                    )
                    print("Connecting to explorecourses...")

                    cur_courses = self.connect.get_courses_by_department(
                        dept, year=year
                    )
                    course_by_dept_list = []
                    for i in range(len(cur_courses)):
                        course = cur_courses[i]
                        # TODO: what to put in reward, putting 0 for placeholder
                        """
                        reward: float,
                        units: tuple of (min_unit, max_unit)
                        course_number: string of unique course ID
                        course_name: string of full name of the course
                        quarter_indices: tuple of available quarters,
                        """
                        single_course_object = {
                            "reward": 0,
                            "units_min": course.units_min,
                            "units_max": course.units_max,
                            "course_number": str(course.course_id),
                            "course_name": course.title,
                        }

                        total_term = []
                        for j in range(len(course.sections)):
                            _, term = course.sections[j].term.split()
                            total_term.append(term)

                        single_course_object["quarters"] = total_term
                        course_by_dept_list.append(single_course_object)

                    course_by_dept = pd.DataFrame(course_by_dept_list)
                    course_by_dept.to_pickle(year_dept_filepath)
                    print("File saved to ", year_dept_filepath)
                else:
                    print(f"Using existing pickle file for {year} {dept}.")

        print("Extraction ended! Start processing courses...")

        # convert courses to class Course by quarter
        return self.course_to_class_database()

    def course_to_class_database(self) -> Dict[int, List[Course]]:
        """
        Convert the extracted courses to dict[quarter_number] = (all courses available in the quarter)
        """
        # course_by_quarter stores dict[quarter_indices] = [list of course objects]
        course_by_quarter = collections.defaultdict(list)

        for year_ind in range(len(self.years)):
            year = self.years[year_ind]
            for dept in self.depts:
                # Read in courses by the specified years and departments

                year_dept_filepath = os.path.join(
                    self.output_dir, f"{year}_{dept}.pickle"
                )
                if not os.path.exists(year_dept_filepath):
                    raise Exception(f"{year_dept_filepath} does not exist!")

                with open(year_dept_filepath, "rb") as handle:
                    cur_course = pickle.load(handle)

                for _, row in cur_course.iterrows():
                    # Iterate through all courses without duplicates
                    if row["course_number"] not in self.all_courses:
                        terms = [
                            4 * year_ind + QUARTER_TO_INDEX[term]
                            for term in row["quarters"]
                        ]
                        self.all_courses[row["course_number"]] = Course(
                            0,
                            (row["units_min"], row["units_max"]),
                            row["course_number"],
                            row["course_name"],
                            tuple(set(terms)),
                        )
                    # Add same courses offered in the new year
                    else:
                        prev_terms = list(
                            self.all_courses[row["course_number"]].quarter_indices
                        )
                        terms = [
                            4 * year_ind + QUARTER_TO_INDEX[term]
                            for term in row["quarters"]
                        ]
                        self.all_courses[row["course_number"]].quarter_indices = tuple(
                            set(prev_terms + terms)
                        )

        # Sort by quarter
        for _, course in self.all_courses.items():
            for term in course.quarter_indices:
                course_by_quarter[term].append(course)

        return course_by_quarter


# A simple test case to see the course outputs
# courses = CoursesDeterministic(["2021-2022", "2022-2023", "2023-2024"])
# new = courses.run()
# print(courses.years)
# for key, val in new.items():
#    for j in range(len(val)):
#        print(key, val[j].course_name, val[j].course_number, val[j].quarter_indices)