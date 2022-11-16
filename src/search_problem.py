from typing import Tuple, List, Dict
from .course_scheduler import State
from .course import ExploreCourse, Course
from itertools import combinations
import copy

from .constants import MIN_UNITS_PER_QUARTER, MAX_UNITS_PER_QUARTER, MAX_CLASS_REWARD


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

    def _get_actions(self, state: State) -> List[List[Tuple[Course, int]]]:
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
        # Offered in the next quarter
        courses_offered = self.explore_course.class_database[state.current_quarter + 1]

        # Not taken before
        candidate_courses = list(set(courses_offered) - set(state.course_taken))

        # TODO: remove this logic; it is only here for MVP
        # Only get courses where min is >=3 units and max is <=5 units, and courses where the
        # course number is >=200
        candidate_courses = [
            course
            for course in candidate_courses
            if course.units[0] >= 3 and course.units[1] <= 5
        ]
        candidate_courses = [
            course
            for course in candidate_courses
            if int("".join(filter(str.isdigit, course.course_number))) >= 200
        ]

        # Filter to courses that satisfy remaining requirements
        candidate_courses = [
            course
            for course in candidate_courses
            if state.remaining_units[course.course_category] > 0
        ]

        # Combinations
        combins = combinations(candidate_courses, 2)
        actions = []

        for combin in combins:
            course1 = combin[0]
            course2 = combin[1]

            for units1 in range(course1.units[0], course1.units[1] + 1):
                for units2 in range(course2.units[0], course2.units[1] + 1):

                    if (
                        units1 + units2 >= MIN_UNITS_PER_QUARTER
                        and units1 + units2 <= MAX_UNITS_PER_QUARTER
                    ):
                        actions.append([(course1, units1), (course2, units2)])

        return actions

    def _get_quarter_cost(self, enrolled_courses: List[Tuple[Course, int]]) -> float:
        """_summary_

        Args:
            enrolled_courses (List[Tuple[Course, int]]): a combination of course

        Raises:
            Exception: _description_

        Returns:
            float: cost for the combination of course
        """
        total_units = 0.0
        total_rewards = 0.0

        for course_and_unit in enrolled_courses:
            total_units += course_and_unit[1]
            total_rewards += course_and_unit[1] * course_and_unit[0].reward

        return total_units * MAX_CLASS_REWARD - total_rewards

    def start_state(self) -> State:
        """_summary_

        Args:
            remaining_units (Dict[str, int]): remaining units in each section, e.g. depth, foundation

        Returns:
            State: _description_
        """
        # raise Exception("Not Implemented yet")
        return State(0, [], self.units_requirement)

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
        if (
            state.current_quarter == self.max_quarter
            or sum(state.remaining_units.values()) == 0
        ):
            return True
        else:
            return False

    def successors_and_cost(self, state: State) -> List[Tuple[State, float]]:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            Tuple[State, float]: _description_
        """
        actions = self._get_actions(state)
        successors = []

        for action in actions:
            suc_current_quarter = state.current_quarter + 1
            suc_remaining_units = copy.deepcopy(state.remaining_units)

            courses_this_quarter = []
            for course, units in action:
                suc_remaining_units[course.course_category] -= units
                courses_this_quarter.append(course)

            suc_courses_taken = state.course_taken + courses_this_quarter
            suc_cost = self._get_quarter_cost(action)

            successors.append(
                (
                    State(suc_current_quarter, suc_courses_taken, suc_remaining_units),
                    suc_cost,
                )
            )

        return successors
