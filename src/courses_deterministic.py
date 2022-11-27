import collections
import os
import pandas as pd
from explorecourses import CourseConnection
from .course import Course

from ast import literal_eval
from typing import Dict, List
import random

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
        read_file_loc="./data/cs_requirements.csv",
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

        self.read_file_loc = read_file_loc
        # self.requirement_file loads all the requirements for cs_tracks
        # requirement_path = "./data/cs_requirements.csv"  # TODO later, change this to accommodate for all the deparments

        if os.path.exists(self.read_file_loc):
            self.requirement_file = pd.read_csv(self.read_file_loc)
        else:
            raise FileNotFoundError("Missing department requirement file!")

    def run(self):
        """
        Currently only extracting courses from CS, EE and ICME department
        Check if course information file exists: if yes, extract from explorecourses api;
        extract from file otherwise. Output courses sorted by year and department in
        self.output_dir/{year}_{dept}.csv
        """
        # Store the information extracted from explorecourses api to .csv files for easier lookup

        if not os.path.exists(self.output_dir):
            print("Creating new path to ", self.output_dir)
            os.makedirs(self.output_dir)

        for year in self.years:
            for dept in self.depts:

                year_dept_filepath = os.path.join(self.output_dir, f"{year}_{dept}.csv")

                if not os.path.exists(year_dept_filepath):
                    print(
                        f"No file available for {year} {dept}, will extract from explorecourses."
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
                            "units_min": course.units_min,
                            "units_max": course.units_max,
                            "course_number": str(course.code),
                            "course_name": course.title,
                            "course_subject": course.subject,
                            "instructor": "",
                        }

                        total_term = set()
                        for j in range(len(course.sections)):
                            _, term = course.sections[j].term.split()
                            total_term.add(term)

                        # If the course isn't offered any of the terms, don't add it.
                        if not total_term:
                            continue

                        # Extract primary instructor for the course
                        for i in range(len(course.sections)):
                            for j in range(len(course.sections[i].schedules)):
                                for k in range(
                                    len(course.sections[i].schedules[j].instructors)
                                ):
                                    if (
                                        course.sections[i]
                                        .schedules[j]
                                        .instructors[k]
                                        .is_primary_instructor
                                    ):
                                        single_course_object["instructor"] = (
                                            course.sections[i]
                                            .schedules[j]
                                            .instructors[k]
                                            .name
                                        )
                                        break
                                if single_course_object["instructor"] != "":
                                    break
                            if single_course_object["instructor"] != "":
                                break

                        single_course_object["quarters"] = list(total_term)
                        course_by_dept_list.append(single_course_object)

                    course_by_dept = pd.DataFrame(course_by_dept_list)

                    course_by_dept.to_csv(year_dept_filepath)
                    print("File saved to ", year_dept_filepath)
                else:
                    print(f"Using existing file for {year} {dept}.")

        print("Extraction ended! Start processing courses...")

        # convert courses to class Course by quarter
        return self.course_to_class_database()

    def find_course_category(self, course_number: str) -> str:
        for _, course in self.requirement_file.iterrows():
            number = course[0].split()[1]
            category = course[0].split()[2]
            if number == course_number:
                return category
        return "elective"

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

                year_dept_filepath = os.path.join(self.output_dir, f"{year}_{dept}.csv")
                if not os.path.exists(year_dept_filepath):
                    raise Exception(f"{year_dept_filepath} does not exist!")

                cur_course = pd.read_csv(year_dept_filepath)

                # When storing as csv, the list gets converted to a string. So we have to convert it back.
                cur_course["quarters"] = cur_course.apply(
                    lambda row: literal_eval(row["quarters"]), axis=1
                )

                for _, row in cur_course.iterrows():
                    # Iterate through all courses without duplicates
                    if row["course_number"] not in self.all_courses:
                        terms = [
                            4 * year_ind + QUARTER_TO_INDEX[term]
                            for term in row["quarters"]
                        ]

                        # TODO: insert real course category
                        self.all_courses[row["course_number"]] = Course(
                            random.uniform(0, 5),
                            (row["units_min"], row["units_max"]),
                            row["course_number"],
                            row["course_name"],
                            row["course_subject"],
                            self.find_course_category(row["course_number"]),
                            row["instructor"],
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
