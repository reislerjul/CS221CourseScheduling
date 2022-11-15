from typing import Tuple, List, Dict, Set
from course_scheduler import State
from course import ExploreCourse, Course


class FindCourses:
    """_summary_
    Formulate the search problem: start state, isEnd, successors and costs
    """

    def __init__(
        self,
        explore_course: ExploreCourse,
        units_requirement: Dict[str, int],
        max_quarter: int,
    ) -> None:
        """_summary_

        Args:
            explore_course (ExploreCourse): database
            units_requirement (Dict[str, int]): _description_
            max_quarter (int): maximum quarter requirement
        """
        self.explore_course = explore_course
        self.units_requirement = units_requirement
        self.max_quarter = max_quarter

    def get_actions(
        self, quarter_index: int, remaining_units: int, courses_taken: Set[Course]
    ) -> List[Set[Course]]:
        """_summary_
        Get filtered actions(course combinations).
        Filters: 1.offered in the quarter, 2.not taken before, 3.satisfy
        units requirement in categories, 4.quarter unit requirement(8-10)
        5.maximum 2 courses/quarter

        Args:
            quarter_index (int): _description_
            remaining_units (int): _description_
            courses_taken (Set[Course]): _description_

        Raises:
            Exception: _description_

        Returns:
            Set[Course]: _description_
        """
        raise Exception("Not Implemented yet")

    def get_quarter_cost(self, enrolled_courses: Set[Course]) -> float:
        """_summary_

        Args:
            enrolled_courses (Set[Tuple[str, int]]): a combination of course

        Raises:
            Exception: _description_

        Returns:
            float: cost for the combination of course
        """

        raise Exception("Not implemented yet")

    def start_state(self, remaining_units: Dict[str, int]) -> State:
        """_summary_

        Args:
            remaining_units (Dict[str, int]): remaining units in each section, e.g. depth, foundation

        Returns:
            State: _description_
        """
        raise Exception("Not Implemented yet")
        # return State(0, Set(), remaining_units)

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
        # if state.current_quarter == self.max_quarter or sum(state.remaining_units.values()) == 0:
        #     return True
        # else:
        #     return False

    def successors_and_cost(
        self, state: State, explorecourse: ExploreCourse
    ) -> List[Tuple[State, float]]:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            Tuple[State, float]: _description_
        """
        raise Exception("Not Implemented yet")

        # succesors = []
        # actions = explorecourse.get_actions(state.current_quarter, state.remaining_units, state.course_taken)
        # for action in actions:
        #     if action not in state.course_taken:
        #         cost = explorecourse.get_quarter_cost(action)
        # succesors.append((succesor,cost))
