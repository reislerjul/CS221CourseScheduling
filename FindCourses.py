from ExploreCourse import ExploreCourse
from State import State
from typing import Tuple


class FindCourses:
    """_summary_

    Args:
        explore_course (ExploreCourse): _description_
    """

    def __init__(self, explore_course: ExploreCourse) -> None:
        self.explore_course = explore_course

    def start_state(self, remaining_units: int) -> State:
        """_summary_

        Args:
            remaining_units (int): _description_

        Raises:
            Exception: _description_

        Returns:
            State: _description_
        """
        raise Exception("Not Implemented yet")

    def is_end(self, state: State) -> bool:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            bool: _description_
        """
        raise Exception("Not Implemented yet")

    def successors_and_cost(self, state: State) -> Tuple[State, float]:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            Tuple[State, float]: _description_
        """
        raise Exception("Not Implemented yet")
