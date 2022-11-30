import copy
from .csp_util import CSP
from typing import Any, Dict, List
import random


class BacktrackingSearch:
    def reset_results(self) -> None:
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment: Dict[Any, Any] = {}
        self.optimalWeight = 0.0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments: List[Dict[Any, Any]] = []
        self.allOptimalAssignments: List[Dict[Any, Any]] = []

    def print_stats(self) -> None:
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print(
                f"Found {self.numOptimalAssignments} optimal assignments \
                    with weight {self.optimalWeight} in {self.numOperations} operations"
            )
            print(
                f"First assignment took {self.firstAssignmentNumOperations} operations"
            )
        else:
            print(
                "No consistent assignment to the CSP was found. The CSP is not solvable."
            )

    def get_delta_weight(self, assignment: Dict, var, val) -> float:
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0:
                return w
        for var2, factor in list(self.csp.binaryFactors[var].items()):
            if var2 not in assignment:
                continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0:
                return w
        return w

    def satisfies_constraints(self, assignment: Dict, var, val) -> bool:
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return whether or not assigning the variable with the proposed new value
        still statisfies all of the constraints.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        return self.get_delta_weight(assignment, var, val) != 0

    def solve(self, csp: CSP, mcv: bool = False, ac3: bool = False) -> None:
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        self.print_stats()

    def backtrack(self, assignment: Dict, numAssigned: int, weight: float) -> bool:
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                    self.allOptimalAssignments.append(newAssignment)
                else:
                    self.numOptimalAssignments = 1
                    self.allOptimalAssignments = [newAssignment]
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return True

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    found_solution = self.backtrack(
                        assignment, numAssigned + 1, weight * deltaWeight
                    )
                    del assignment[var]

                    if found_solution:
                        return True
        else:
            # Arc consistency check is enabled. This is helpful to speed up 3c.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.apply_arc_consistency(var)

                    found_solution = self.backtrack(
                        assignment, numAssigned + 1, weight * deltaWeight
                    )
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

                    if found_solution:
                        return True

        return False

    def get_unassigned_variable(self, assignment: Dict):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable. The type of the variable
            depends on what was added with csp.add_variable
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment:
                    return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values.
            #       Make sure you're finding the domain of the right variable!
            # Hint: satisfies_constraints determines whether or not assigning a
            #       variable to some value given a partial assignment continues
            #       to satisfy all constraints.
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_CODE (our solution is 13 lines of code, but don't worry if you deviate from this)

            least_remaining_domain = float("inf")
            chosen_var = None

            for var in self.csp.variables:
                if var not in assignment:
                    num_consistent_assignments = 0
                    all_values = self.domains[var]
                    for value in all_values:
                        if self.satisfies_constraints(assignment, var, value):
                            num_consistent_assignments += 1

                    if num_consistent_assignments < least_remaining_domain:
                        least_remaining_domain = num_consistent_assignments
                        chosen_var = var

            return chosen_var
            # END_YOUR_CODE

    def apply_arc_consistency(self, var) -> None:
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """

        def remove_inconsistent_values(var1, var2):
            removed = False
            # the binary factor must exist because we add var1 from var2's neighbor
            factor = self.csp.binaryFactors[var1][var2]
            for val1 in list(self.domains[var1]):
                # Note: in our implementation, it's actually unnecessary to check unary factors,
                #       because in get_delta_weight() unary factors are always checked.
                if (
                    self.csp.unaryFactors[var1]
                    and self.csp.unaryFactors[var1][val1] == 0
                ) or all(factor[val1][val2] == 0 for val2 in self.domains[var2]):
                    self.domains[var1].remove(val1)
                    removed = True
            return removed

        queue = [var]
        while len(queue) > 0:
            curr = queue.pop(0)
            for neighbor in self.csp.get_neighbor_vars(curr):
                if remove_inconsistent_values(neighbor, curr):
                    queue.append(neighbor)


def create_sum_variable(csp: CSP, name: str, variables: List, maxSum: int) -> tuple:
    """
    Given a list of |variables| each with non-negative integer domains,
    returns the name of a new variable with domain range(0, maxSum+1), such that
    it's consistent with the value |n| iff the assignments for |variables|
    sums to |n|.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('sum', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables that are already in the CSP that
        have non-negative integer values as its domain.
    @param maxSum: An integer indicating the maximum sum value allowed. You
        can use it to get the auxiliary variables' domain

    @return result: The name of a newly created variable with domain range
        [0, maxSum] such that it's consistent with an assignment of |n|
        iff the assignment of |variables| sums to |n|.
    """

    result = ("sum", name, "aggregated")
    csp.add_variable(result, list(range(maxSum + 1)))

    if len(variables) == 0:
        csp.add_unary_factor(result, lambda x: x == 0)
        return result

    domain = []
    for i in range(maxSum + 1):
        for j in range(i, maxSum + 1):
            domain.append((i, j))

    for i in range(len(variables)):
        csp.add_variable(("sum", name, str(i)), domain)

    csp.add_unary_factor(("sum", name, "0"), lambda x: x[0] == 0)

    for i in range(len(variables)):
        f = ("sum", name, str(i))
        csp.add_binary_factor(f, variables[i], lambda x, y: x[1] == x[0] + y)

    for i in range(len(variables) - 1):
        f0 = ("sum", name, str(i))
        f1 = ("sum", name, str(i + 1))
        csp.add_binary_factor(f0, f1, lambda x, y: x[1] == y[0])

    csp.add_binary_factor(
        ("sum", name, str(len(variables) - 1)), result, lambda x, y: x[1] == y
    )

    return result


############################################################
# Problem 2

# A class providing methods to generate CSP that can solve the course scheduling
# problem.


class SchedulingCSPConstructor:
    def __init__(
        self,
        courses_by_quarter,
        df_requirements,
        breadth_to_satisfy,
        foundations_not_satisfied,
        nlp_courses,
        robotics_courses,
        vision_courses,
        custom_requests,
    ):
        """
        Saves the necessary data.

        @param bulletin: Stanford Bulletin that provides a list of courses
        @param profile: A student's profile and requests
        """

        self.courses_by_quarter = courses_by_quarter
        self.df_requirements = df_requirements
        self.satisfies_dict = {}
        self.breadth_to_satisfy = breadth_to_satisfy
        self.foundations_not_satisfied = foundations_not_satisfied
        self.nlp_courses = nlp_courses
        self.robotics_courses = robotics_courses
        self.vision_courses = vision_courses
        self.custom_requests = custom_requests

        courses = df_requirements["Course"].values
        satisfies = df_requirements["Subcategory"].values

        for i in range(len(courses)):
            course = courses[i]

            if course not in self.satisfies_dict:
                self.satisfies_dict[course] = set()

            self.satisfies_dict[course].add(satisfies[i])

    def add_variables(self, csp: CSP) -> None:
        """
        Adding the variables into the CSP. Each variable, (request, quarter),
        can take on the value of one of the courses requested in request or None.
        For instance, for quarter='Aut2013', and a request object, request, generated
        from 'CS221 or CS246', (request, quarter) should have the domain values
        ['CS221', 'CS246', None]. Conceptually, if var is assigned 'CS221'
        then it means we are taking 'CS221' in 'Aut2013'. If it's None, then
        we are not taking either of them in 'Aut2013'.

        @param csp: The CSP where the additional constraints will be added to.
        """

        def _quarter_units_constraint(classes, units):
            """
            If classes are taken in a quarter, the number of units must not be 0
            """
            if classes is not None:
                return units > 0
            return units == 0

        def _depth_units_constraint(classes, units):
            """
            Correctly set the number of depth units taken in the quarter
            """
            if classes is None:
                return units == 0

            depth_subcategories = {"a", "b", "c"}
            num_depth_units = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                for element in satisfies:
                    if element in depth_subcategories:
                        num_depth_units += 4
                        break

            return num_depth_units == units

        def _significant_implementation_constraint(classes, significant_course_taken):
            """
            Correctly set the number of significant implementation classes taken in the quarter
            """
            if classes is None:
                return significant_course_taken == 0

            significant_courses = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]

                for element in satisfies:
                    if element == "significant implementation":
                        significant_courses += 1
                        break

            if significant_course_taken == 0:
                return significant_course_taken == significant_courses

            return significant_courses >= significant_course_taken

        def _depth_a_constraint(classes, depth_a_taken):
            if classes is None:
                return depth_a_taken == 0

            depth_a = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "a" in satisfies:
                    depth_a += 1
                    break

            return depth_a_taken == depth_a

        def _depth_b_constraint(classes, depth_b_taken):
            if classes is None:
                return depth_b_taken == 0

            depth_b = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "b" in satisfies:
                    depth_b += 1

            return depth_b_taken == depth_b

        def _breadth_systems_constraint(classes, breadth_systems_taken):
            if classes is None:
                return breadth_systems_taken == 0

            breadth_systems = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "systems" in satisfies:
                    breadth_systems += 1
                    break

            return breadth_systems_taken == breadth_systems

        def _breadth_society_constraint(classes, breadth_society_taken):
            if classes is None:
                return breadth_society_taken == 0

            breadth_society = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "society" in satisfies:
                    breadth_society += 1
                    break

            return breadth_society_taken == breadth_society

        def _breadth_theory_constraint(classes, breadth_theory_taken):
            if classes is None:
                return breadth_theory_taken == 0

            breadth_theory = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "society" in satisfies:
                    breadth_theory += 1
                    break

            return breadth_theory_taken == breadth_theory

        def _foundations_logic_constraint(classes, foundations_logic_taken):
            if classes is None:
                return foundations_logic_taken == 0

            foundations_logic = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "logic" in satisfies:
                    foundations_logic += 1
                    break

            return foundations_logic_taken == foundations_logic

        def _foundations_probability_constraint(classes, foundatons_probability_taken):
            if classes is None:
                return foundatons_probability_taken == 0

            foundations_probability = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "probability" in satisfies:
                    foundations_probability += 1
                    break

            return foundatons_probability_taken == foundations_probability

        def _foundations_algorithm_constraint(classes, foundations_algorthm_taken):
            if classes is None:
                return foundations_algorthm_taken == 0

            foundations_algorthm = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "algorithm" in satisfies:
                    foundations_algorthm += 1
                    break

            return foundations_algorthm_taken == foundations_algorthm

        def _foundations_organ_constraint(classes, foundations_organ_taken):
            if classes is None:
                return foundations_organ_taken == 0

            foundations_organ = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "organ" in satisfies:
                    foundations_organ += 1
                    break

            return foundations_organ_taken == foundations_organ

        def _foundations_systems_constraint(classes, foundations_systems_taken):
            if classes is None:
                return foundations_systems_taken == 0

            foundations_systems = 0
            for course in classes:
                satisfies = self.satisfies_dict[course]
                if "foundation systems" in satisfies:
                    foundations_systems += 1
                    break

            return foundations_systems_taken == foundations_systems

        def _robotics_constraint(classes, robotics_taken):
            if classes is None:
                return robotics_taken == 0

            robotics = 0
            for course in classes:
                if course in self.robotics_courses:
                    robotics += 1

            return robotics == robotics_taken

        def _nlp_constraint(classes, nlp_taken):
            if classes is None:
                return nlp_taken == 0

            nlp = 0
            for course in classes:
                if course in self.nlp_courses:
                    nlp += 1

            return nlp == nlp_taken

        def _vision_constraint(classes, vision_taken):
            if classes is None:
                return vision_taken == 0

            vision = 0
            for course in classes:
                if course in self.vision_courses:
                    vision += 1

            return vision == vision_taken

        def _no_repeat_class_constraint(courses1, courses2):
            if courses1 is None or courses2 is None:
                return True

            for course in courses1:
                if course in courses2:
                    return False
            return True

        def _no_repeat_foundations(courses):
            if courses is None:
                return True

            course1_satisfies = self.satisfies_dict[courses[0]]
            course2_satisfies = self.satisfies_dict[courses[1]]

            foundation_courses = {
                "logic",
                "probability",
                "algorithm",
                "organ",
                "foundation systems",
            }
            satisfies_intersection = course1_satisfies.intersection(course2_satisfies)
            for element in satisfies_intersection:
                if element in foundation_courses:
                    return False
            return True

        def _no_repeat_foundations_quarters(courses1, courses2):
            if courses1 is None or courses2 is None:
                return True

            foundation_courses = {
                "logic",
                "probability",
                "algorithm",
                "organ",
                "foundation systems",
            }

            course1_satisfies = self.satisfies_dict[courses1[0]]
            course2_satisfies = self.satisfies_dict[courses1[1]]
            course3_satisfies = self.satisfies_dict[courses2[0]]
            course4_satisfies = self.satisfies_dict[courses2[1]]

            for element in course1_satisfies:
                if element in foundation_courses:
                    if (
                        element in course2_satisfies
                        or element in course3_satisfies
                        or element in course4_satisfies
                    ):
                        return False

            for element in course2_satisfies:
                if element in foundation_courses:
                    if element in course3_satisfies or element in course4_satisfies:
                        return False

            for element in course3_satisfies:
                if element in foundation_courses:
                    if element in course4_satisfies:
                        return False

            return True

        # Note that CS221 has to be taken to satisfy depth a.
        # In doing so, we also satisfy significant implementation and breadth applications.
        quarter_units_variables = []
        quarter_class_variables = []
        quarter_depth_variables = []
        quarter_depth_a_variables = []
        quarter_depth_b_variables = []
        quarter_breadth_systems_variables = []
        quarter_breadth_society_variables = []
        quarter_breadth_theory_variables = []
        quarter_foundations_logic_variables = []
        quarter_foundations_probability_variables = []
        quarter_foundations_algorithm_variables = []
        quarter_foundations_organ_variables = []
        quarter_foundations_systems_variables = []
        quarter_robotics_variables = []
        quarter_nlp_variables = []
        quarter_vision_variables = []

        for quarter, courses in self.courses_by_quarter.items():

            domain: List[Any] = [None]

            random.shuffle(courses)

            for i in range(len(courses) - 1):
                course1 = courses[i]

                if course1.units[0] <= 4 and course1.units[1] >= 4:

                    for j in range(i + 1, len(courses)):

                        course2 = courses[j]
                        if course2.units[0] <= 4 and course2.units[1] >= 4:

                            course_code1 = (
                                f"{course1.course_subject} {course1.course_number}"
                            )
                            course_code2 = (
                                f"{course2.course_subject} {course2.course_number}"
                            )

                            domain.append((course_code1, course_code2))

            csp.add_variable(f"Quarter {quarter} classes", domain)
            csp.add_unary_factor(f"Quarter {quarter} classes", _no_repeat_foundations)

            quarter_class_variables.append(f"Quarter {quarter} classes")

            csp.add_variable(f"Quarter {quarter} units", [0, 8])
            csp.add_binary_factor(
                f"Quarter {quarter} classes",
                f"Quarter {quarter} units",
                _quarter_units_constraint,
            )
            quarter_units_variables.append(f"Quarter {quarter} units")

            csp.add_variable(f"Quarter {quarter} depth units", [0, 4, 8])
            csp.add_binary_factor(
                f"Quarter {quarter} classes",
                f"Quarter {quarter} depth units",
                _depth_units_constraint,
            )
            quarter_depth_variables.append(f"Quarter {quarter} depth units")

            csp.add_variable(f"Quarter {quarter} depth a classes", [0, 1])
            csp.add_binary_factor(
                f"Quarter {quarter} classes",
                f"Quarter {quarter} depth a classes",
                _depth_a_constraint,
            )
            quarter_depth_a_variables.append(f"Quarter {quarter} depth a classes")

            csp.add_variable(f"Quarter {quarter} depth b classes", [0, 1, 2])
            csp.add_binary_factor(
                f"Quarter {quarter} classes",
                f"Quarter {quarter} depth b classes",
                _depth_b_constraint,
            )
            quarter_depth_b_variables.append(f"Quarter {quarter} depth b classes")

            if "systems" in self.breadth_to_satisfy:
                csp.add_variable(f"Quarter {quarter} breadth systems classes", [0, 1])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} breadth systems classes",
                    _breadth_systems_constraint,
                )
                quarter_breadth_systems_variables.append(
                    f"Quarter {quarter} breadth systems classes"
                )

            if "society" in self.breadth_to_satisfy:
                csp.add_variable(f"Quarter {quarter} breadth society classes", [0, 1])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} breadth society classes",
                    _breadth_society_constraint,
                )
                quarter_breadth_society_variables.append(
                    f"Quarter {quarter} breadth society classes"
                )

            if "theory" in self.breadth_to_satisfy:
                csp.add_variable(f"Quarter {quarter} breadth theory classes", [0, 1])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} breadth theory classes",
                    _breadth_theory_constraint,
                )
                quarter_breadth_theory_variables.append(
                    f"Quarter {quarter} breadth theory classes"
                )

            if "logic" in self.foundations_not_satisfied:
                csp.add_variable(f"Quarter {quarter} foundations logic classes", [0, 1])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} foundations logic classes",
                    _foundations_logic_constraint,
                )
                quarter_foundations_logic_variables.append(
                    f"Quarter {quarter} foundations logic classes"
                )

            if "probability" in self.foundations_not_satisfied:
                csp.add_variable(
                    f"Quarter {quarter} foundations probability classes", [0, 1]
                )
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} foundations probability classes",
                    _foundations_probability_constraint,
                )
                quarter_foundations_probability_variables.append(
                    f"Quarter {quarter} foundations probability classes"
                )

            if "algorithm" in self.foundations_not_satisfied:
                csp.add_variable(
                    f"Quarter {quarter} foundations algorithm classes", [0, 1]
                )
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} foundations algorithm classes",
                    _foundations_algorithm_constraint,
                )
                quarter_foundations_algorithm_variables.append(
                    f"Quarter {quarter} foundations algorithm classes"
                )

            if "organ" in self.foundations_not_satisfied:
                csp.add_variable(f"Quarter {quarter} foundations organ classes", [0, 1])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} foundations organ classes",
                    _foundations_organ_constraint,
                )
                quarter_foundations_organ_variables.append(
                    f"Quarter {quarter} foundations organ classes"
                )

            if "foundation systems" in self.foundations_not_satisfied:
                csp.add_variable(
                    f"Quarter {quarter} foundation systems classes", [0, 1]
                )
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} foundation systems classes",
                    _foundations_systems_constraint,
                )
                quarter_foundations_systems_variables.append(
                    f"Quarter {quarter} foundation systems classes"
                )

            if "robotics" in self.custom_requests:
                csp.add_variable(f"Quarter {quarter} robotics classes", [0, 1, 2])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} robotics classes",
                    _robotics_constraint,
                )
                quarter_robotics_variables.append(f"Quarter {quarter} robotics classes")

            if "nlp" in self.custom_requests:
                csp.add_variable(f"Quarter {quarter} nlp classes", [0, 1, 2])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} nlp classes",
                    _nlp_constraint,
                )
                quarter_nlp_variables.append(f"Quarter {quarter} nlp classes")

            if "vision" in self.custom_requests:
                csp.add_variable(f"Quarter {quarter} vision classes", [0, 1, 2])
                csp.add_binary_factor(
                    f"Quarter {quarter} classes",
                    f"Quarter {quarter} vision classes",
                    _vision_constraint,
                )
                quarter_vision_variables.append(f"Quarter {quarter} vision classes")

        for i in range(len(quarter_class_variables) - 1):
            quarter1 = quarter_class_variables[i]

            for j in range(i + 1, len(quarter_class_variables)):
                quarter2 = quarter_class_variables[j]
                csp.add_binary_factor(quarter1, quarter2, _no_repeat_class_constraint)
                csp.add_binary_factor(
                    quarter1, quarter2, _no_repeat_foundations_quarters
                )

        # Degree program should be at least 45 units
        sum_var = create_sum_variable(
            csp, "program_units_var", quarter_units_variables, 60
        )
        csp.add_unary_factor(sum_var, lambda total_units: total_units >= 45)

        # At least 21 depth units should be satisfied
        sum_var = create_sum_variable(
            csp, "program_depth_units_var", quarter_depth_variables, 58
        )
        csp.add_unary_factor(sum_var, lambda total_depth_units: total_depth_units >= 21)

        # At least 1 depth a class
        sum_var = create_sum_variable(
            csp, "program_depth_a_var", quarter_depth_a_variables, 7
        )
        csp.add_unary_factor(sum_var, lambda depth_a_taken: depth_a_taken >= 1)

        # At least 4 depth b classes
        sum_var = create_sum_variable(
            csp, "program_depth_b_var", quarter_depth_b_variables, 14
        )
        csp.add_unary_factor(sum_var, lambda depth_b_taken: depth_b_taken >= 4)

        # At least 1 breadth systems class
        if "systems" in self.breadth_to_satisfy:
            sum_var = create_sum_variable(
                csp,
                "program_breadth_systems_var",
                quarter_breadth_systems_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var, lambda breadth_systems_taken: breadth_systems_taken >= 1
            )

        # At least 1 breadth society class
        if "society" in self.breadth_to_satisfy:
            sum_var = create_sum_variable(
                csp,
                "program_breadth_society_var",
                quarter_breadth_society_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var, lambda breadth_society_taken: breadth_society_taken >= 1
            )

        # At least 1 breadth theory class
        if "theory" in self.breadth_to_satisfy:
            sum_var = create_sum_variable(
                csp, "program_breadth_theory_var", quarter_breadth_theory_variables, 7
            )
            csp.add_unary_factor(
                sum_var, lambda breadth_theory_taken: breadth_theory_taken >= 1
            )

        # At least 1 foundations logic class
        if "logic" in self.foundations_not_satisfied:
            sum_var = create_sum_variable(
                csp,
                "program_foundations_logic_var",
                quarter_foundations_logic_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var, lambda foundations_logic_taken: foundations_logic_taken >= 1
            )

        # At least 1 foundations probability class
        if "probability" in self.foundations_not_satisfied:
            sum_var = create_sum_variable(
                csp,
                "program_foundations_probability_var",
                quarter_foundations_probability_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda foundations_probability_taken: foundations_probability_taken
                >= 1,
            )

        # At least 1 foundations algorithm class
        if "algorithm" in self.foundations_not_satisfied:
            sum_var = create_sum_variable(
                csp,
                "program_foundations_algorithm_var",
                quarter_foundations_algorithm_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda foundations_algorithm_taken: foundations_algorithm_taken >= 1,
            )

        # At least 1 foundations organ class
        if "organ" in self.foundations_not_satisfied:
            sum_var = create_sum_variable(
                csp,
                "program_foundations_organ_var",
                quarter_foundations_organ_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var, lambda foundations_organ_taken: foundations_organ_taken >= 1
            )

        # At least 1 foundations systems class
        if "foundation systems" in self.foundations_not_satisfied:
            sum_var = create_sum_variable(
                csp,
                "program_foundations_systems_var",
                quarter_foundations_systems_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda foundations_systems_taken: foundations_systems_taken >= 1,
            )

        if "robotics" in self.custom_requests:
            sum_var = create_sum_variable(
                csp,
                "program_robotics_var",
                quarter_robotics_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda robotics_taken: robotics_taken
                >= self.custom_requests["robotics"],
            )

        if "nlp" in self.custom_requests:
            sum_var = create_sum_variable(
                csp,
                "program_nlp_var",
                quarter_nlp_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda nlp_taken: nlp_taken >= self.custom_requests["nlp"],
            )

        if "vision" in self.custom_requests:
            sum_var = create_sum_variable(
                csp,
                "program_vision_var",
                quarter_vision_variables,
                7,
            )
            csp.add_unary_factor(
                sum_var,
                lambda vision_taken: vision_taken >= self.custom_requests["vision"],
            )

    def get_csp(self) -> CSP:
        """
        Return a CSP that only enforces the basic constraints that a course can
        only be taken when it's offered and that a request can only be satisfied
        in at most one quarter.

        @return csp: A CSP where basic variables and constraints are added.
        """

        csp = CSP()
        self.add_variables(csp)
        return csp
