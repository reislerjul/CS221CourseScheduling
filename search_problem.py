from typing import Tuple, List, Dict, Set
from course_scheduler import State
from course import ExploreCourse


class FindCourses:
    """_summary_

    Args:
        explore_course (ExploreCourse): _description_
    """

    def __init__(self, explore_course: ExploreCourse) -> None:
        self.explore_course = explore_course

    def start_state(self, remaining_units: Dict[str, int]) -> State:
        """_summary_

        Args:
            remaining_units (Dict[str, int]): remaining units in each section, e.g. depth, foundation

        Returns:
            State: _description_
        """
        # raise Exception("Not Implemented yet")
        return State(0, Set(), remaining_units)

    def is_end(self, state: State) -> bool:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            bool: _description_
        """
        # raise Exception("Not Implemented yet")
        if state.current_quarter == 6 or sum(state.remaining_units.values()) == 0:
            return True
        else:
            return False

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
