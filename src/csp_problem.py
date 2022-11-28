import copy
from .util import CSP, CourseBulletin, Profile  # get_or_variable,
from typing import Dict, List, Any

# from .course import ExploreCourse, Course


class BacktrackingSearch:
    def reset_results(self) -> None:
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment: Dict[Any, Any] = {}
        self.optimalWeight = 0

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
        self.allAssignments: List[Any] = []
        self.allOptimalAssignments: List[Any] = []

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

    def backtrack(self, assignment: Dict, numAssigned: int, weight: float) -> None:
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
                self.optimalWeight = int(weight)

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

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
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
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

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

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
            # raise Exception("Not implemented yet")
            domain_num = float("Inf")
            var_notassigned = [
                var for var in self.csp.variables if var not in assignment
            ]
            for var in var_notassigned:
                domains = self.domains[var]
                num = 0
                for val in domains:
                    if self.satisfies_constraints(assignment, var, val):
                        num += 1
                if num < domain_num:
                    domain_num = num
                    var_min = var
            return var_min

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


class SchedulingCSPConstructor:
    def __init__(self, bulletin: CourseBulletin, profile: Profile):
        """
        Saves the necessary data.

        @param bulletin: Stanford Bulletin that provides a list of courses
        @param profile: A student's profile and requests
        """

        self.bulletin = bulletin
        self.profile = profile

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

        for request in self.profile.requests:

            for quarter in self.profile.quarters:
                # print(quarter)
                # print("\n",request.cids)
                # print("\n",(request, quarter))
                csp.add_variable((request, quarter), [request.cids] + [None])

    def is_offered_in(self, course_info: Dict, quarter: int):
        return quarter in course_info["quarters"]

    def add_bulletin_constraints(self, csp: CSP) -> None:
        """
        Add the constraints that a course can only be taken if it's offered in
        that quarter.
        @param csp: The CSP where the additional constraints will be added to.
        """
        for request in self.profile.requests:
            for quarter in self.profile.quarters:
                csp.add_unary_factor(
                    (request, quarter),
                    lambda cid: cid is None
                    or self.is_offered_in(self.bulletin.courses[cid], quarter),
                )

    def add_norepeating_constraints(self, csp: CSP) -> None:
        """
        No course can be repeated. Coupling with our problem's constraint that
        only one of a group of requested course can be taken, this implies that
        every request can only be satisfied in at most one quarter.
        @param csp: The CSP where the additional constraints will be added to.
        """
        for request in self.profile.requests:
            for quarter1 in self.profile.quarters:
                for quarter2 in self.profile.quarters:
                    if quarter1 == quarter2:
                        continue
                    csp.add_binary_factor(
                        (request, quarter1),
                        (request, quarter2),
                        lambda cid1, cid2: cid1 is None or cid2 is None,
                    )

    def get_basic_csp(self) -> CSP:
        """
        Return a CSP that only enforces the basic constraints that a course can
        only be taken when it's offered and that a request can only be satisfied
        in at most one quarter.

        @return csp: A CSP where basic variables and constraints are added.
        """

        csp = CSP()
        self.add_variables(csp)
        self.add_bulletin_constraints(csp)
        self.add_norepeating_constraints(csp)
        return csp
