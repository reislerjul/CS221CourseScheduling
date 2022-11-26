from typing import Tuple, List, Dict, Optional
from .course_scheduler import State
from .course import ExploreCourse, Course
from itertools import combinations
import copy
import heapq

from .constants import MIN_UNITS_PER_QUARTER, MAX_UNITS_PER_QUARTER, MAX_CLASS_REWARD


class FindCourses:
    """_summary_
    Formulate the search problem: start state, isEnd, successors and costs
    """

    def __init__(
        self,
        explore_course: ExploreCourse,
        units_requirement: Dict[str, int],
        # Newly added instructors, research_units, internship and research_terms
        instructors: List,
        research_units: int,
        internship: bool,
        research_terms: List,
        max_quarter: int,
        max_successors: int,
    ) -> None:
        """_summary_

        Args:
            explore_course (ExploreCourse): database
            units_requirement (Dict[str, int]): applicable DEPARTMENT_REQUIREMENT dict from constants.py
            max_quarter (int): maximum quarter requirement
        """
        self.explore_course = explore_course
        self.units_requirement = units_requirement
        self.instructors = instructors
        self.research_units = research_units
        self.internship = internship
        self.research_terms = research_terms
        self.max_quarter = max_quarter
        self.max_successors = max_successors

    # TODO: move utility function to a better place
    def research_class(self, course):
        if ("research" in course.course_name) or ("Research" in course.course_name):
            return True
        return False

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
        # Filter out the quarter if planning to do internship during the summer
        nxt_quarter = state.current_quarter + 1
        if self.internship and (nxt_quarter == 4 or nxt_quarter == 8):
            return []

        # Offered in the next quarter
        courses_offered = self.explore_course.class_database[state.current_quarter + 1]

        # Not taken before
        taken_numbers = set([course.course_number for course in state.course_taken])
        candidate_courses = []
        for course in courses_offered:
            if course.course_number not in taken_numbers:
                candidate_courses.append(course)

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
            if int("".join(filter(str.isdigit, course.course_number))) >= 100
        ]

        # Filter to courses that satisfy remaining requirements
        candidate_courses = [
            course
            for course in candidate_courses
            if state.remaining_units[course.course_category] > 0
        ]

        # Combinations
        # Relax the number of courses available for each quarter
        # TODO: decide on what to include for the quarters of courses

        combins = combinations(candidate_courses, 2)
        actions = []

        for combin in combins:
            course1 = combin[0]
            course2 = combin[1]
            # Make sure to include research credits in appropriate quarter
            if nxt_quarter in self.research_terms:
                if (not self.research_class(course1)) and (
                    not self.research_class(course2)
                ):
                    return []

            for units1 in range(course1.units[0], course1.units[1] + 1):
                for units2 in range(course2.units[0], course2.units[1] + 1):

                    if (
                        units1 + units2 >= MIN_UNITS_PER_QUARTER
                        and units1 + units2 <= MAX_UNITS_PER_QUARTER
                    ):

                        actions.append([(course1, units1), (course2, units2)])

        return actions

    def _get_quarter_cost(
        self, enrolled_courses: List[Tuple[Course, int]], state: State, prereqs: List
    ) -> float:
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
            # course_and_unit[0]: Course object
            # course_and_unit[1]: unit count
            total_units += course_and_unit[1]
            total_rewards += course_and_unit[1] * course_and_unit[0].reward

        # Add soft requirement for previously taken courses
        # Give higher reward for completed prerequisites
        # Give lower reward for non-completed prerequisites
        # TODO: figure out how to include the prerequisites of the class

        prereq_count = 0
        for i in range(len(prereqs)):
            if prereqs[i] in state.course_taken:
                prereq_count += 1
        # Current logic:
        # Reward proportional to the number of prerequisites satisfied
        # Maximum of 5 total rewards possible
        total_rewards += 5 / len(prereqs) * prereq_count

        # TODO: add time component for course cost
        # Assign higher cost for courses larger than 300
        # Provide 3 different Gaussian Distributions for possible time costs
        #
        #
        #

        # Note: UCS cannot have cost below 0
        return max(total_units * MAX_CLASS_REWARD - total_rewards, 0)

    def start_state(self) -> State:
        """_summary_

        Args:
            remaining_units (Dict[str, int]): remaining units in each section, e.g. depth, foundation

        Returns:
            State: _description_
        """
        return State(
            0, [], self.units_requirement, self.instructors, self.research_units
        )

    def is_end(self, state: State) -> bool:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            bool: _description_
        """

        if (
            (state.remaining_instructors == [])
            and (state.remaining_research == 0)
            and sum(state.remaining_units.values()) <= 0
        ):
            return True
        else:
            return False

    def successors_and_cost(
        self, state: State
    ) -> List[Tuple[List[Tuple[Course, int]], State, float]]:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            Exception: _description_

        Returns:
            Tuple[State, float]: _description_
        """
        if state.current_quarter + 1 > self.max_quarter:
            return []

        actions = self._get_actions(state)
        successors = []

        for action in actions:
            suc_current_quarter = state.current_quarter + 1
            suc_remaining_units = copy.deepcopy(state.remaining_units)
            suc_remaining_instructors = copy.deepcopy(state.remaining_instructors)
            suc_remaining_research = copy.deepcopy(state.remaining_research)

            courses_this_quarter = []
            for course, units in action:
                # TODO: include the case where a single class satisfies multiple requirements
                suc_remaining_units[course.course_category] -= units
                if self.research_class(course):
                    suc_remaining_research -= units
                if course.instructor in suc_remaining_instructors:
                    suc_remaining_instructors.remove(course.instructor)
                courses_this_quarter.append(course)

            suc_courses_taken = state.course_taken + courses_this_quarter
            suc_cost = self._get_quarter_cost(action, state, [])

            successors.append(
                (
                    action,
                    State(
                        suc_current_quarter,
                        suc_courses_taken,
                        suc_remaining_units,
                        suc_remaining_instructors,
                        suc_remaining_research,
                    ),
                    suc_cost,
                )
            )

        if not successors:
            # If there are no successors, skip the term and set the cost to a high number.
            successors.append(
                (
                    [],
                    State(
                        state.current_quarter + 1,
                        copy.deepcopy(state.course_taken),
                        copy.deepcopy(state.remaining_units),
                        copy.deepcopy(state.remaining_instructors),
                        copy.deepcopy(state.remaining_research),
                    ),
                    1000,
                )
            )

        best_successors = sorted(successors, key=lambda x: x[2])[: self.max_successors]
        return best_successors


class UniformCostSearch:
    def __init__(self, verbose: int = 0):
        self.verbose = verbose

        self.actions: Optional[List[List[Tuple[Course, int]]]] = None
        self.path_cost: Optional[float] = None
        self.num_states_explored: int = 0
        self.past_costs: Dict[State, float] = {}

    def solve(self, problem: FindCourses) -> None:
        """
        Run Uniform Cost Search on the specified `problem` instance.

        """

        # Initialize data structures
        frontier = PriorityQueue()  # Explored states are maintained by the frontier.
        backpointers: Dict[
            State, Tuple[List[Tuple[Course, int]], State]
        ] = {}  # Map state -> previous state.

        # Add the start state
        start_state = problem.start_state()
        frontier.update(start_state, 0.0)

        while True:
            # Remove the state from the queue with the lowest past_cost (priority).
            state, past_cost = frontier.remove_min()
            if state is None and past_cost is None:
                if self.verbose >= 1:
                    print("Searched the entire search space!")
                return

            # Update tracking variables
            self.past_costs[state] = past_cost
            self.num_states_explored += 1
            if self.verbose >= 2:
                print(f"Exploring {state} with past_cost {past_cost}")

            # Check if we've reached an end state; if so, extract solution.
            if problem.is_end(state):
                self.actions = []
                while state != start_state:
                    action, prevState = backpointers[state]
                    self.actions.append(action)
                    state = prevState
                self.actions.reverse()
                self.path_cost = past_cost
                if self.verbose >= 1:
                    print(f"num_states_explored = {self.num_states_explored}")
                    print(f"path_cost = {self.path_cost}")
                    print(f"actions = {self.actions}")
                return

            # Expand from `state`, updating the frontier with each `new_state`
            for action, new_state, cost in problem.successors_and_cost(state):
                if self.verbose >= 3:
                    print(f"\t{state} => {new_state} (Cost: {past_cost} + {cost})")

                if frontier.update(new_state, past_cost + cost):
                    # We found better way to go to `new_state` --> update backpointer!
                    backpointers[new_state] = (action, state)


class PriorityQueue:
    def __init__(self):
        self.DONE = -100000
        self.heap = []
        self.priorities = {}  # Map from state to priority

        # heapq will compare the second elements in the tuple if there is a tie in the
        # first element; to prevent this, we will maintain a counter so that if there
        # are ties, the element inserted first is prioritized
        self.counter = 0

    # Insert `state` into the heap with priority `new_priority` if `state` isn't in
    # the heap or `new_priority` is smaller than the existing priority.
    #   > Return whether the priority queue was updated.
    def update(self, state: State, new_priority: float) -> bool:
        old_priority = self.priorities.get(state)
        if old_priority is None or new_priority < old_priority:
            self.priorities[state] = new_priority
            heapq.heappush(self.heap, (new_priority, self.counter, state))
            self.counter += 1
            return True
        return False

    # Returns (state with minimum priority, priority) or (None, None) if empty.
    def remove_min(self):
        while len(self.heap) > 0:
            priority, _, state = heapq.heappop(self.heap)
            if self.priorities[state] == self.DONE:
                # Outdated priority, skip
                continue
            self.priorities[state] = self.DONE
            return state, priority

        # Nothing left...
        return None, None
