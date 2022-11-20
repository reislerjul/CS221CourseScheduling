import os
import pandas as pd
from typing import List, Tuple

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

        self.df_requirements = pd.read_csv(program_filepath)
        self.total_requirement_units_taken = 0
        self.seminar_units_taken = 0
        self.courses_taken = set()

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

    def _is_foundations_satisfied(self) -> bool:
        return len(self.foundations_areas_left) == 0

    def _is_breadth_satisfied(self) -> bool:
        return len(self.breadth_areas_left) <= 1

    def _is_depth_satisfied(self) -> bool:
        for value in self.depth_areas_left.values():
            if value > 0:
                return False

        return self.depth_units_left <= 0

    def _is_significant_implementation_satisfied(self) -> bool:
        return self.significant_implementation_satisfied

    def _is_unit_requirement_satisfied(self) -> bool:
        return self.total_requirement_units_taken >= TOTAL_UNITS_REQUIRED

    def _is_elective_course(self, course_code) -> bool:
        non_elective_cs = {"CS 196", "CS 198", "CS 390A", "CS 390B", "CS 390C"}
        other_elective_departments = {"EE", "MATH", "STATS"}
        seminars = {"CS 300", "EE 380", "EE 385A"}

        department, course_id = course_code.split()
        course_id_num = int("".join(filter(course_id.isdigit, "aas30dsa20")))

        # Valid CS elective
        if (
            department == "CS"
            and course_id_num > 111
            and course_code not in non_elective_cs
        ):
            return True

        # Valid elective from other department
        if department in other_elective_departments and course_id_num >= 100:
            return True

        # Seminars
        if self.seminar_units_taken <= 3:
            if department == "CS" and course_id_num >= 500:
                return True

            if course_code in seminars:
                return True

        return False

    def is_program_satisfied(self) -> bool:
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

    def take_course(self, course_and_units: Tuple[Course, int]) -> None:
        """
        Update the remaining requirements for the degree program object based on the course that is taken.

        Arguments:
        course_and_units - A tuple containing a course and units it is taken for. Eg (<CS 221 object>, 4)
        """
        course, units = course_and_units
        full_course_code = f"{course.course_subject} {course.course_number}"

        requirements_satisfied = self.requirements_satisfied_by_course(course)

        if not requirements_satisfied:
            print(
                f"WARNING: taking {full_course_code} but it doesn't satisfy any requirements..."
            )
            self.courses_taken.add(full_course_code)
            return

        for category, subcategory in requirements_satisfied:

            if category == "foundation":
                self.foundations_areas_left = self.foundations_areas_left - {
                    subcategory
                }

            if category == "breadth":
                self.breadth_areas_left = self.breadth_areas_left - {subcategory}

            if category == "depth":
                self.depth_areas_left[subcategory] -= 1
                self.depth_units_left -= units

            if category == "significant implementation":
                self.significant_implementation_satisfied = True

        self.total_requirement_units_taken += units
        self.courses_taken.add(full_course_code)

    def waive_course(self, course: Course) -> None:
        """
        Update the remaining requirements for the degree program object based on the course that is waived.

        Arguments:
        course_and_units - A course object. Eg <CS 221 object>.
        """
        full_course_code = f"{course.course_subject} {course.course_number}"
        if full_course_code not in set(self.foundations["Course"]):
            raise Exception(
                f"Tried to waive {full_course_code}, but cannot waive a non-foundation course."
            )

        areas_satisfied = self.foundations.loc[
            self.foundations["Course"] == full_course_code
        ]["Subcategory"].to_list()
        for area in areas_satisfied:
            self.foundations_areas_left = self.foundations_areas_left - {area}

    def requirements_satisfied_by_course(self, course: Course) -> List[Tuple[str, str]]:
        """
        Returns a list of the remaining requirements that are satisfied by the course.

        Arguments:
        course - A Course object. Eg <CS 221 object>.

        Returns:
        requirements_satisfied - A list of all the requirement/sub-requirements pairs that are satisfied by the course.
        """
        full_course_code = f"{course.course_subject} {course.course_number}"
        df_course = self.df_requirements.loc[
            self.df_requirements["Course"] == full_course_code
        ]

        requirements_satisfied = []

        for _, row in df_course.iterrows():

            if row["Category"] == "foundation":
                if row["Subcategory"] in self.foundations_areas_left:
                    requirements_satisfied.append((row["Category"], row["Subcategory"]))

            if row["Category"] == "breadth":
                if (
                    len(self.breadth_areas_left) > 1
                    and row["Subcategory"] in self.breadth_areas_left
                ):
                    requirements_satisfied.append((row["Category"], row["Subcategory"]))

            if row["Category"] == "depth":
                if (
                    self.depth_units_left > 0
                    or self.depth_areas_left[row["Subcategory"]] > 0
                ):
                    requirements_satisfied.append((row["Category"], row["Subcategory"]))

            if row["Category"] == "significant implementation":
                if not self.significant_implementation_satisfied:
                    requirements_satisfied.append((row["Category"], row["Subcategory"]))

        if len(requirements_satisfied) == 0:
            if (
                self._is_elective_course(full_course_code)
                and self.total_requirement_units_taken < TOTAL_UNITS_REQUIRED
            ):
                requirements_satisfied.append(("elective", ""))

        return requirements_satisfied
