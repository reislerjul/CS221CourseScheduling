from abc import ABC, abstractmethod
from typing import Tuple

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
    def take_course(self, course_and_units: Tuple[Course, int]):
        """
        Update the remaining requirements for the degree program object based on the course that is taken.

        Arguments:
        course_and_units - A tuple containing a course and units it is taken for. Eg (<CS 221 object>, 4)
        """
        pass

    @abstractmethod
    def waive_course(self, course: Course):
        """
        Update the remaining requirements for the degree program object based on the course that is waived.

        Arguments:
        course_and_units - A course object. Eg <CS 221 object>.
        """
        pass

    @abstractmethod
    def does_course_satisfy_remaining_requirements(self, course: Course):
        """
        Return true if the course satisfies any requirements that are remaining in the degree program and False otherwise.

        Arguments:
        course - A Course object. Eg <CS 221 object>.
        """
        pass
