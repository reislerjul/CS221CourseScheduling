from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Tuple

from ..course import Course


TOTAL_UNITS_REQUIRED = 45


class DegreeProgram(ABC):
    @abstractmethod
    def __init__(self, program_filepath):
        """
        Arguments:
        program_filepath - path to file containing requirements for the degree program
        """
        pass

    @abstractmethod
    def is_program_satisfied(self):
        """
        Return True if the degree program is satisfied and False otherwise.
        """
        pass

    @abstractmethod
    def take_course(
        self, df_requirements: pd.DataFrame, course_and_units: Tuple[Course, int]
    ):
        """
        Update the remaining requirements for the degree program object based on the course that is taken.

        Arguments:
        course_and_units - A tuple containing a course and units it is taken for. Eg (<CS 221 object>, 4)
        """
        pass

    @abstractmethod
    def waive_course(self, df_requirements: pd.DataFrame, course: Course):
        """
        Update the remaining requirements for the degree program object based on the course that is waived.

        Arguments:
        course_and_units - A course object. Eg <CS 221 object>.
        """
        pass

    @abstractmethod
    def requirements_satisfied_by_course(
        self, df_requirements: pd.DataFrame, course: Course
    ) -> List[Tuple[str, str]]:
        """
        Returns a list of the remaining requirements that are satisfied by the course.

        Arguments:
        course - A Course object. Eg <CS 221 object>.

        Returns:
        requirements_satisfied - A list of all the requirement/sub-requirements pairs that are satisfied by the course.
        """
        pass
