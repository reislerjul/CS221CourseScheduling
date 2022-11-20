import os
import pandas as pd
from typing import Tuple

from ..course import Course
from .degree_program import DegreeProgram, TOTAL_UNITS_REQUIRED


class CSAIProgram(DegreeProgram):
    def __init__(self, program_filepath):
        """
        Arguments:
        program_filepath - path to file containing requirements for the degree program
        """

        if not os.path.exists(program_filepath):
            raise Exception(
                f"Cannot find path to program requirements! {program_filepath} does not exist."
            )

        self.total_requirement_units_taken = 0
        self.df_requirements = pd.read_csv(program_filepath)

        # Foundations
        self.foundations = self.df_requirements[
            self.df_requirements["Category"] == "foundation"
        ]
        self.foundations_areas_left = set(self.foundations["Subcategory"])

        # Breadth
        self.breadth = self.df_requirements[
            self.df_requirements["Category"] == "breadth"
        ]
        self.breadth_areas_left = set(self.breadth["Subcategory"])

        # Depth
        self.depth = self.df_requirements[self.df_requirements["Category"] == "depth"]
        self.depth_areas_left = {"a": 1, "b": 4}
        self.depth_units_left = 21

        # Significant Implementation
        self.significant_implementation_satisfied = False

    def _is_foundations_satisfied(self):
        return len(self.foundations_areas_left) == 0

    def _is_breadth_satisfied(self):
        return len(self.breadth_areas_left) <= 1

    def _is_depth_satisfied(self):
        for value in self.depth_areas_left.values():
            if value > 0:
                return False

        return self.depth_units_left <= 0

    def _is_significant_implementation_satisfied(self):
        return self.significant_implementation_satisfied

    def _is_unit_requirement_satisfied(self):
        return self.total_requirement_units_taken >= TOTAL_UNITS_REQUIRED

    def is_program_satisfied(self):
        """
        Return True if the degree program is satisfied and False otherwise.
        """
        return (
            self._is_foundations_satisfied()
            and self._is_breadth_satisfied()
            and self._is_depth_satisfied()
            and self._is_significant_implementation_satisfied()
            and self._is_unit_requirement_satisfied()
        )

    def take_course(self, course_and_units: Tuple[Course, int]):
        """
        Update the remaining requirements for the degree program object based on the course that is taken.

        Arguments:
        course_and_units - A tuple containing a course and units it is taken for. Eg (<CS 221 object>, 4)
        """
        pass

    def waive_course(self, course: Course):
        """
        Update the remaining requirements for the degree program object based on the course that is waived.

        Arguments:
        course_and_units - A course object. Eg <CS 221 object>.
        """
        full_course_code = f"{course.course_subject} {course.course_number}"
        if full_course_code not in set(self.foundations["Course"]):
            raise Exception(
                f"Tried to waive {course.course_subject} {course.course_number}, but cannot waive a non-foundation course."
            )
        areas_satisfied = self.foundations.loc[
            self.foundations["Course"] == full_course_code
        ]["Subcategory"].to_list()
        for area in areas_satisfied:
            self.foundations_areas_left = self.foundations_areas_left - {area}

    def does_course_satisfy_remaining_requirements(self, course: Course):
        """
        Return true if the course satisfies any requirements that are remaining in the degree program and False otherwise.

        Arguments:
        course - A Course object. Eg <CS 221 object>.
        """
        pass
