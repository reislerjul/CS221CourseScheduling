from csp import CSP, Profile
from course import ExploreCourse


class SchedulingCSPConstructor:
    def __init__(self, explore_course: ExploreCourse, profile: Profile):
        """
        Saves the necessary data.

        @param bulletin: Stanford Bulletin that provides a list of courses
        @param profile: A student's profile and requests
        """

        self.explore_course = explore_course
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
                csp.add_variable((request, quarter), request.cids + [None])

    def add_bulletin_constraints(self, csp: CSP) -> None:
        """
        Add the constraints that a course can only be taken if it's offered in
        that quarter.

        @param csp: The CSP where the additional constraints will be added to.
        """

        for request in self.profile.requests:
            for quarter in self.profile.quarters:
                csp.add_unary_factor((request, quarter),
                                     lambda cid: cid is None or
                                     self.bulletin.courses[cid].is_offered_in(quarter))

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
                    csp.add_binary_factor((request, quarter1), (request, quarter2),
                                          lambda cid1, cid2: cid1 is None or cid2 is None)

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

    def add_quarter_constraints(self, csp: CSP) -> None:
        """
        If the profile explicitly wants a request to be satisfied in some given
        quarters, e.g. Aut2013, then add constraints to not allow that request to
        be satisfied in any other quarter. If a request doesn't specify the
        quarter(s), do nothing.

        @param csp: The CSP where the additional constraints will be added to.
        """
        # Problem 2a
        # Hint: If a request doesn't specify the quarter(s), do nothing.
        # Hint: To check which quarters are specified by a request variable
        #       named `request`, use request.quarters (NOT self.profile.quarters).
        # BEGIN_YOUR_CODE (our solution is 5 lines of code, but don't worry if you deviate from this)


        # if the value of cid is None, then constraint is satisfied.


        for request in self.profile.requests:
            if request.quarters == []:
                continue
            for quarter in self.profile.quarters:
                csp.add_unary_factor((request,quarter),
                                        lambda cid: \
                                            True if (quarter in request.quarters or cid is None)
                                            else False )

        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    def add_request_weights(self, csp: CSP) -> None:
        """
        Incorporate weights into the CSP. By default, a request has a weight
        value of 1 (already configured in Request). You should only use the
        weight when one of the requested course is in the solution. A
        unsatisfied request should also have a weight value of 1.

        @param csp: The CSP where the additional constraints will be added to.
        """

        for request in self.profile.requests:
            for quarter in self.profile.quarters:
                csp.add_unary_factor((request, quarter),
                                     lambda cid: request.weight if cid != None else 1.0)

    def add_prereq_constraints(self, csp: CSP) -> None:
        """
        Adding constraints to enforce prerequisite. A course can have multiple
        prerequisites. You can assume that *all courses in req.prereqs are
        being requested*. Note that if our parser inferred that one of your
        requested course has additional prerequisites that are also being
        requested, these courses will be added to req.prereqs. You will be notified
        with a message when this happens. Also note that req.prereqs apply to every
        single course in req.cids. If a course C has prerequisite A that is requested
        together with another course B (i.e. a request of 'A or B'), then taking B does
        not count as satisfying the prerequisite of C. You cannot take a course
        in a quarter unless all of its prerequisites have been taken *before* that
        quarter. You should take advantage of get_or_variable().

        @param csp: The CSP where the additional constraints will be added to.
        """

        # Iterate over all request courses
        for req in self.profile.requests:
            if len(req.prereqs) == 0:
                continue
            # Iterate over all possible quarters
            for quarter_i, quarter in enumerate(self.profile.quarters):
                # Iterate over all prerequisites of this request
                for pre_cid in req.prereqs:
                    # Find the request with this prerequisite
                    for pre_req in self.profile.requests:
                        if pre_cid not in pre_req.cids:
                            continue
                        # Make sure this prerequisite is taken before the requested course(s)
                        prereq_vars = [(pre_req, q)
                                       for i, q in enumerate(self.profile.quarters) if i < quarter_i]
                        v = (req, quarter)
                        orVar = get_or_variable(
                            csp, (v, pre_cid), prereq_vars, pre_cid)
                        # Note this constraint is enforced only when the course is taken
                        # in `quarter` (that's why we test `not val`)
                        csp.add_binary_factor(
                            orVar, v, lambda o, val: not val or o)

    def add_unit_constraints(self, csp: CSP) -> None:
        """
        Add constraints to the CSP to ensure that course units are correctly assigned.
        This means meeting two conditions:

        1- If a course is taken in a given quarter, it should be taken for
           a number of units that is within bulletin.courses[cid].minUnits/maxUnits.
           If not taken, it should be 0.
        2- In each quarter, the total number of units of courses taken should be between
           profile.minUnits/maxUnits, inclusively.
           You should take advantage of create_sum_variable() to implement this.

        For every requested course, you must create a variable named (courseId, quarter)
        (e.g. ('CS221', 'Aut2013')) and its assigned value is the number of units.
        This variable is how our solution extractor will obtain the number of units,
        so be sure to add it.

        For a request 'A or B', if you choose to take A, then you must use a unit
        number that's within the range of A.

        @param csp: The CSP where the additional constraints will be added to.
        """
        # Problem 2b
        # Hint 1: read the documentation above carefully
        # Hint 2: the domain for each (courseId, quarter) variable should contain 0
        #         because the course might not be taken
        # Hint 3: add appropriate binary factor between (request, quarter) and
        #         (courseId, quarter) variables. Remember that a course can only
        #         be requested at most once in a profile and that if you have a
        #         request such as 'request A or B', then A being taken must
        #         mean that B is NOT taken in the schedule.
        # Hint 4: you must ensure that the sum of units per quarter for your schedule
        #         are within the min and max threshold inclusive
        # Hint 5: use nested functions and lambdas like what get_or_variable and
        #         add_prereq_constraints do
        # Hint 6: don't worry about quarter constraints in each Request as they'll
        #         be enforced by the constraints added by add_quarter_constraints
        # Hint 7: if 'a' and 'b' are the names of two variables constrained to have
        #         sum 7, you can create a variable for their sum
        #         by calling var = create_sum_variable(csp, SOME_NAME, ['a', 'b'], 7).
        #         Note: 7 in the call just helps create the domain; it does
        #         not define a constraint. You can add a constraint to the
        #         sum variable (e.g., to make sure that the number of units
        #         taken in a quarter are within a specific range) just as
        #         you've done for other variables.
        # Hint 8: if having trouble with starting, here is some general structure
        #         that you could use to get started:
        #           loop through self.profile.quarters
        #               ...
        #               loop through self.profile.requests
        #                   loop through request.cids
        #                       ...
        #               ...
        # BEGIN_YOUR_CODE (our solution is 21 lines of code, but don't worry if you deviate from this)


        for quarter in self.profile.quarters:
            var_list = []
            for request in self.profile.requests:
                for cid in request.cids:
                    course = self.bulletin.courses[cid]
                    if course.is_offered_in(quarter):
                        domain = [i for i in range(course.minUnits,course.maxUnits+1)] + [0]
                        new_var = (cid,quarter)
                        csp.add_variable((cid,quarter),domain)
                        csp.add_binary_factor((request,quarter),\
                                                (cid,quarter), lambda c_id, unit:
                                                unit > 0 if cid == c_id else
                                                unit == 0
                                                )
                        var_list.append(new_var)
            result = create_sum_variable(csp,quarter,var_list,self.profile.maxUnits)
            csp.add_unary_factor(result, lambda unit:\
                                            True if (unit >= self.profile.minUnits \
                                                and unit <= self.profile.maxUnits)\
                                                else False)


        # raise Exception("Not implemented yet")
        # END_YOUR_CODE

    def add_all_additional_constraints(self, csp: CSP) -> None:
        """
        Add all additional constraints to the CSP.

        @param csp: The CSP where the additional constraints will be added to.
        """
        self.add_quarter_constraints(csp)
        self.add_request_weights(csp)
        self.add_prereq_constraints(csp)
        self.add_unit_constraints(csp)
