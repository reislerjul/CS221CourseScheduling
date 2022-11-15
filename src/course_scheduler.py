from typing import Dict, List


class State:
    """_summary_

    Args:
        current_quarter (int): _description_
        course_taken (Set): _description_
        remaining_units (Dict[str, int]): _description_
    """

    def __init__(
        self, current_quarter: int, course_taken: List, remaining_units: Dict[str, int]
    ) -> None:
        self.current_quarter = current_quarter
        self.course_taken = course_taken
        self.remaining_units = remaining_units
