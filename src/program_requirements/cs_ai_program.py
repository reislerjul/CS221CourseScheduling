import os
import pandas as pd
from typing import Tuple

from ..course import Course
from .degree_program import DegreeProgram


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

        self.df_requirements = pd.read_csv(program_filepath)

        print(self.df_requirements)

    def _is_foundations_satisfied(self):
        pass

    def _is_breadth_satisfied(self):
        pass

    def _is_depth_satisfied(self):
        pass

    def _is_significant_implementation_satisfied(self):
        pass

    def _is_electives_satisfied(self):
        pass

    def is_program_satisfied(self):
        """
        Return True if the degree program is satisfied and False otherwise.
        """
        return (
            self._is_foundations_satisfied()
            and self._is_breadth_satisfied()
            and self._is_depth_satisfied()
            and self._is_significant_implementation_satisfied()
            and self._is_electives_satisfied()
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
        foundations = self.df_requirements[
            self.df_requirements.Category == "foundation"
        ]
        if f"{course.course_subject} {course.course_number}" not in set(
            foundations["Course"]
        ):
            raise Exception(
                f"Tried to waive {course.course_subject} {course.course_number}, but cannot waive a non-foundation course."
            )

    def does_course_satisfy_remaining_requirements(self, course: Course):
        """
        Return true if the course satisfies any requirements that are remaining in the degree program and False otherwise.

        Arguments:
        course - A Course object. Eg <CS 221 object>.
        """
        pass
