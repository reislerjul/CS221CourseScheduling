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
        course_description: str,
        quarter_indices: Tuple,
    ) -> None:

        self.reward = reward
        self.units = units
        self.course_number = course_number
        self.course_name = course_name
        self.course_subject = course_subject
        self.course_category = course_category
        self.course_description = course_description
        self.quarter_indices = quarter_indices


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
