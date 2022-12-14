import pandas as pd
from typing import List, Set, Tuple

from ..course import Course
from .degree_program import DegreeProgram, TOTAL_UNITS_REQUIRED


class CSAIProgram(DegreeProgram):
    def __init__(self, df_requirements: pd.DataFrame, verbose: int = 0):
        """
        Program requirements are based on https://cs.stanford.edu/degrees/mscs/programsheets/psguide2223.pdf

        Arguments:
        df_requirements - DataFrame for degree program
        """
        self.verbose = verbose

        self.total_requirement_units_taken = 0
        self.seminar_units_taken = 0
        self.courses_taken: Set[str] = set()

        # Foundations
        foundations = df_requirements[df_requirements["Category"] == "foundation"]
        self.foundations_areas_left = set(foundations["Subcategory"])
        self.foundation_units_counted = 0

        # Breadth
        breadth = df_requirements[df_requirements["Category"] == "breadth"]
        self.breadth_areas_left = set(breadth["Subcategory"])

        # Depth
        self.depth_areas_left = {"a": 1, "b": 4, "c": 0}
        self.depth_units_left = 21

        # Significant Implementation
        self.significant_implementation_satisfied = False

    def _is_foundations_satisfied(self) -> bool:
        """
        Check whether foundation requirements are satisfied.
        """
        return len(self.foundations_areas_left) == 0

    def _is_breadth_satisfied(self) -> bool:
        """
        Check whether breadth requirements are satisfied.
        """
        return len(self.breadth_areas_left) <= 1

    def _is_depth_satisfied(self) -> bool:
        """
        Check whether depth requirements are satisfied.
        """
        for value in self.depth_areas_left.values():
            if value > 0:
                return False

        return self.depth_units_left <= 0

    def _is_significant_implementation_satisfied(self) -> bool:
        """
        Check whether significant implementation requirements are satisfied.
        """
        return self.significant_implementation_satisfied

    def _is_unit_requirement_satisfied(self) -> bool:
        """
        Check whether unit requirements are satisfied.
        """
        return self.total_requirement_units_taken >= TOTAL_UNITS_REQUIRED

    @staticmethod
    def _is_seminar_course(course_code: str) -> bool:
        """
        Check whether course is a seminar.

        Arguments:
        course_code: course code for the class, eg "CS 221"
        """
        seminars = {"CS 300", "EE 380", "EE 385A"}
        department, course_id = course_code.split()
        course_id_num = int("".join(filter(str.isdigit, course_id)))
        if (department == "CS" and course_id_num >= 500) or course_code in seminars:
            return True

        return False

    def _is_elective_course(self, course_code: str) -> bool:
        """
        Check whether course is an elective.

        Arguments:
        course_code: course code for the class, eg "CS 221"
        """
        non_elective_cs = {"CS 196", "CS 198", "CS 390A", "CS 390B", "CS 390C"}
        other_elective_departments = {"EE", "MATH", "STATS"}

        department, course_id = course_code.split()
        course_id_num = int("".join(filter(str.isdigit, course_id)))

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
            return CSAIProgram._is_seminar_course(course_code)

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

    def take_course(
        self, df_requirements: pd.DataFrame, course_and_units: Tuple[Course, int]
    ) -> None:
        """
        Update the remaining requirements for the degree program object based on the course that is taken.

        Arguments:
        course_and_units - A tuple containing a course and units it is taken for. Eg (<CS 221 object>, 4)
        """
        course, units = course_and_units
        full_course_code = f"{course.course_subject} {course.course_number}"

        requirements_satisfied = self.requirements_satisfied_by_course(
            df_requirements, course
        )

        if not requirements_satisfied:
            if self.verbose > 0:
                print(
                    f"WARNING: taking {full_course_code} but it doesn't satisfy any requirements..."
                )
            self.courses_taken.add(full_course_code)
            return

        units_towards_degree = units
        for category, subcategory in requirements_satisfied:

            if category == "foundation":
                self.foundations_areas_left = self.foundations_areas_left - {
                    subcategory
                }
                units_towards_degree = min(units, 10 - self.foundation_units_counted)
                self.foundation_units_counted += units_towards_degree

            if category == "breadth":
                self.breadth_areas_left = self.breadth_areas_left - {subcategory}

            if category == "depth":
                self.depth_areas_left[subcategory] -= 1
                self.depth_units_left -= units

            if category == "significant implementation":
                self.significant_implementation_satisfied = True

        if CSAIProgram._is_seminar_course(full_course_code):
            units_towards_degree = min(units, 3 - self.seminar_units_taken)
            self.seminar_units_taken += units_towards_degree

        self.total_requirement_units_taken += units_towards_degree
        self.courses_taken.add(full_course_code)

    def waive_course(self, df_requirements: pd.DataFrame, course: Course) -> None:
        """
        Update the remaining requirements for the degree program object based on the course that is waived.

        Arguments:
        course_and_units - A course object. Eg <CS 221 object>.
        """
        foundations = df_requirements[df_requirements["Category"] == "foundation"]

        full_course_code = f"{course.course_subject} {course.course_number}"
        if full_course_code not in set(foundations["Course"]):
            raise Exception(
                f"Tried to waive {full_course_code}, but cannot waive a non-foundation course."
            )

        foundations = df_requirements[df_requirements["Category"] == "foundation"]

        areas_satisfied = foundations.loc[foundations["Course"] == full_course_code][
            "Subcategory"
        ].to_list()
        for area in areas_satisfied:
            self.foundations_areas_left = self.foundations_areas_left - {area}

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
        full_course_code = f"{course.course_subject} {course.course_number}"
        df_course = df_requirements.loc[df_requirements["Course"] == full_course_code]

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
