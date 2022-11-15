from typing import Tuple, List, Dict, Set
from course_scheduler import State
from course import ExploreCourse, Course
from itertools import combinations


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

    def club_courses(
        self,
        curr_courses: Set[Course],
        number_units: int,
        course_available: Set[Course],
        candidate_courses: Set[Set[Course]],
    ) -> None:
        if number_units == 10:
            candidate_courses.add(curr_courses)
            return

        for course in course_available:
            for unit in course.units:
                if number_units + unit <= 10 and course not in curr_courses:
                    curr_courses.add(course)
                    self.club_courses(
                        curr_courses,
                        number_units + course.units,
                        course_available,
                        candidate_courses,
                    )
                    curr_courses.remove(course)

        if number_units >= 8:
            if number_units == 10:
                candidate_courses.add(curr_courses)
                return

    def get_actions(self, state: State) -> List[List[Course]]:
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
        # raise Exception("Not Implemented yet")
        # Offered in the quarter
        courses_offered = self.explore_course.class_database(state.current_quarter)
        # Not taken before
        candiate_courses = courses_offered - state.course_taken
        # Combinations
        combins = combinations(candiate_courses, 2)
        actions = []

        for combin in combins:
            units = [combin[0].units, combin[1].units]
            categories = [combin[0].category, combin[1].category]
            # Quarter 8-10 units
            if sum(units) <= 10 and sum(units) >= 8:
                if (
                    state.remaining_units[categories[0]] >= units[0]
                    and state.remaining_units[categories[1]] >= units[1]
                ):
                    actions.append(List(combin))
        return actions

    def get_quarter_cost(self, enrolled_courses: List[Course]) -> float:
        """_summary_

        Args:
            enrolled_courses (Set[Tuple[str, int]]): a combination of course

        Raises:
            Exception: _description_

        Returns:
            float: cost for the combination of course
        """
        # raise Exception("Not implemented yet")
        units = [List(enrolled_courses)[0].units, List(enrolled_courses)[1].units]
        return (
            sum(units) * 5
            - units[0] * enrolled_courses[0].reward
            - units[1] * enrolled_courses[1].reward
        )

    def start_state(self) -> State:
        """_summary_

        Args:
            remaining_units (Dict[str, int]): remaining units in each section, e.g. depth, foundation

        Returns:
            State: _description_
        """
        # raise Exception("Not Implemented yet")
        return State(0, Set(), self.units_requirement)

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
        # raise Exception("Not Implemented yet")
        actions = self.get_actions(state)
        successors = []
        for action in actions:
            List(state.course_taken).append(action)
            suc_current_quarter = state.current_quarter + 1
            for f, v in list(action[0].units.items()):
                state.remaining_units[f] = state.remaining_units.get(f, 0) - v
            for f, v in list(action[1].units.items()):
                state.remaining_units[f] = state.remaining_units.get(f, 0) - v
            suc_cost = self.get_quarter_cost(action)
            successors.append(
                (
                    State(
                        suc_current_quarter, state.course_taken, state.remaining_units
                    ),
                    suc_cost,
                )
            )
        return successors
