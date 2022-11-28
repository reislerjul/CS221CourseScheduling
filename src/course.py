from typing import Dict, Set, Tuple


class Course:
    """_summary_


    Args:
        reward (float): _description_
        units (tuple): _description_
        course_number (str): _description_
        course_name (str): _description_
        course_subject (str): _description_
        course_category (str): _description_
        quarter_indices (tuple): _description_
    """

    def __init__(
        self,
        reward: float,
        units: Tuple,
        course_number: str,
        course_name: str,
        course_subject: str,
        course_category: str,
        quarter_indices: Tuple,
    ) -> None:

        self.reward = reward
        self.units = units
        self.course_number = course_number
        self.course_name = course_name
        self.course_subject = course_subject
        self.course_category = course_category
        self.quarter_indices = quarter_indices
        # # Return whether this course is offered in |quarter| (e.g., Aut2013).

    # Return whether this course is offered in |quarter| (e.g., Aut2013).
    # def is_offered_in(self, quarter: str) -> bool:
    #     print("a")
    #     # return any(quarter.startswith(q) for q in self.quarter_indices)
    #     return quarter in self.quarter_indices

    # def short_str(self) -> str: return f'{self.course_number}: {self.course_name}'

    # def __str__(self):
    #     return f'Course: {self.course_number}, name: {self.course_name}, quarters: {self.quarter_indices}, '
    #             # units: {self.minUnits}-{self.maxUnits}, prereqs: {self.prereqs}


class ExploreCourse:
    def __init__(
        self,
        class_database: Dict[int, Set[Course]],
        course_category: Dict[str, Set[Course]],
    ):
        """_summary_

        Args:
            class_database (Dict[int, Set]): courses having the same quarter index
            course_category (Dict[str, Set]): courses having the same units category
        """
        self.class_database = class_database
        self.course_category = course_category
