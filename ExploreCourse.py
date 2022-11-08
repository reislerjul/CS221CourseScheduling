# TODO Finish all the function implementations
# and add all the docstring info

from typing import Dict, Set, Tuple


class ExploreCourse:
    def __init__(self, class_database: Dict[int, Set], course_category: Dict[str, Set]):
        """_summary_

        Args:
            class_database (Dict[int, Set]): _description_
            course_category (Dict[str, Set]): _description_
        """
        self.class_database = class_database
        self.course_category = course_category

    def get_actions(self, quarter_index: int, remaining_units: int):
        """_summary_

        Args:
            quarter_index (int): _description_
            remaining_units (int): _description_
        """

        raise Exception("Not Implemented yet")

    def get_quarter_cost(self, enrolled_courses: Set[Tuple[str, int]]):
        """_summary_

        Args:
            enrolled_courses (Set[Tuple[str, int]]): _description_
        """

        raise Exception("Not implemented yet")
