# import re
from typing import Dict, List, Tuple, Set, Any
from src.course import ExploreCourse, Course

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.


class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor # functions.
        # The table is represented as a dictionary of dictionary.
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain: List) -> None:
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()

    def get_neighbor_vars(self, var) -> List:
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return list(self.binaryFactors[var].keys())

    def add_unary_factor(self, var, factorFunc) -> None:
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value from the domain |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val: float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {
                val: self.unaryFactors[var][val] * factor[val] for val in factor
            }
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1|
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        # try:
        #     assert var1 != var2
        # except:
        #     print(
        #         "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #     )
        #     print(
        #         "!! Tip:                                                                      !!"
        #     )
        #     print(
        #         "!! You are adding a binary factor over a same variable...                    !!"
        #     )
        #     print(
        #         "!! Please check your code and avoid doing this.                              !!"
        #     )
        #     print(
        #         "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #     )
        #     raise

        self.update_binary_factor_table(
            var1,
            var2,
            {
                val1: {
                    val2: float(factor_func(val1, val2)) for val2 in self.values[var2]
                }
                for val1 in self.values[var1]
            },
        )
        self.update_binary_factor_table(
            var2,
            var1,
            {
                val2: {
                    val1: float(factor_func(val1, val2)) for val1 in self.values[var1]
                }
                for val2 in self.values[var2]
            },
        )

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]


############################################################
# Course scheduling specifics.

# Information about a course:
# - self.cid: course ID (e.g., CS221)
# - self.name: name of the course (e.g., Artificial Intelligence)
# - self.quarters: quarters without the years (e.g., Aut)
# - self.minUnits: minimum allowed units to take this course for (e.g., 3)
# - self.maxUnits: maximum allowed units to take this course for (e.g., 3)
# - self.prereqs: list of course IDs that must be taken before taking this course.
# class Course:
#     def __init__(self, info: Dict):
#         self.__dict__.update(info)

#     # # Return whether this course is offered in |quarter| (e.g., Aut2013).
#     def is_offered_in(self, quarter: str) -> bool:
#         return any(quarter.startswith(q) for q in self.quarters)

#     def short_str(self) -> str: return f'{self.cid}: {self.name}'

#     def __str__(self):
#         return f'Course: {self.cid}, name: {self.name}, quarters: {self.quarters}, \
#                 units: {self.minUnits}-{self.maxUnits}, prereqs: {self.prereqs}'

# Information about all the courses
class CourseBulletin:
    def __init__(self, explore_course: ExploreCourse):  # coursesPath: str
        """_summary_

        Args:
            courses (Dict[str, Course]): _description_
            remaining_units (int): _description_
            courses_taken (Set[Course]): _description_
        """
        # Read courses (JSON format)
        self.courses: Dict[str, Dict[str, Any]] = {}
        self.explore_course = explore_course
        # info = json.loads(open(coursesPath).read())
        for quarter in range(1, 9):
            for course in self.explore_course.class_database[quarter]:
                if course.course_number not in self.courses.keys():
                    # course = Course(courseInfo)
                    # quarter_name = ["Spring", "Summer", "Autumn", "Winter"]
                    self.courses[course.course_number] = {
                        "cid": course.course_number,
                        "description": "",
                        "maxUnits": max(course.units),
                        "minUnits": min(course.units),
                        "name": course.course_name,
                        "prereqs": [],
                        "py/object": "course.Course",
                        "quarters": list(course.quarter_indices),
                    }
        # print(self.courses)


# A request to take one of a set of courses at some particular times.
class Request:
    def __init__(
        self, cids: List[str], quarters: List[str], prereqs: List[str], weight: float
    ):
        """
        Create a Request object.

        @param cids: list of courses from which only one is chosen.
        @param quarters: list of strings representing the quarters (e.g. Aut2013)
            the course must be taken in.
        @param prereqs: list of strings representing courses pre-requisite of
            the requested courses separated by comma. (e.g. CS106,CS103,CS109)
        @param weight: real number denoting how much the student wants to take
            this/or one the requested courses.
        """
        self.cids = cids
        self.quarters = quarters
        self.prereqs = prereqs
        self.weight = weight

    def __str__(self):
        return "Request{%s %s %s %s}" % (
            self.cids,
            self.quarters,
            self.prereqs,
            self.weight,
        )

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)


# Given the path to a preference file and a
class Profile:
    def __init__(self, bulletin: CourseBulletin, prefsPath: str):
        """
        Parses the preference file and generate a student's profile.

        @param prefsPath: Path to a txt file that specifies a student's request
            in a particular format.
        """
        self.bulletin = bulletin

        # Read preferences
        self.minUnits = 9  # minimum units per quarter,
        self.maxUnits = 12  # maximum units per quarter
        self.quarters: List[int] = [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
        ]  # (e.g., Aut2013), quarters: List[int]"
        self.taken: Set[Course] = set()  # Courses that we've taken, Set[]
        self.requests = []
        # for line in open(prefsPath):
        #     m = re.match('(.*)\\s*#.*', line)
        #     if m: line = m.group(1)
        #     line = line.strip()
        #     if len(line) == 0: continue

        #     # Units
        #     m = re.match('minUnits (.+)', line)
        #     if m:
        #         self.minUnits = int(m.group(1))
        #         continue
        #     m = re.match('maxUnits (.+)', line)
        #     if m:
        #         self.maxUnits = int(m.group(1))
        #         continue

        #     # Register a quarter (quarter, year)
        #     m = re.match('register (.+)', line)
        #     if m:
        #         quarter = m.group(1)
        #         m = re.match('(Aut|Win|Spr|Sum)(\d\d\d\d)', quarter)
        #         if not m:
        #             raise Exception(f'Invalid quarter {quarter}, want something like Spr2013')
        #         self.quarters.append(quarter)
        #         continue

        #     # Already taken a course
        #     m = re.match('taken (.+)', line)
        #     if m:
        #         cid = self.ensure_course_id(m.group(1))
        #         self.taken.add(cid)
        #         continue

        # # Request to take something
        # # also match & to parse MS&E courses correctly
        # m = re.match('request ([\w&]+)(.*)', line)
        # if m:
        #     cids = [self.ensure_course_id(m.group(1))]
        #     quarters = []
        #     prereqs = []
        #     weight = 1  # Default: would want to take
        #     args = m.group(2).split()
        #     for i in range(0, len(args), 2):
        #         if args[i] == 'or':
        #             cids.append(self.ensure_course_id(args[i+1]))
        #         elif args[i] == 'after':  # Take after a course
        #             prereqs = [self.ensure_course_id(c) for c in args[i+1].split(',')]
        #         elif args[i] == 'in':  # Take in a particular quarter
        #             quarters = [self.ensure_quarter(q) for q in args[i+1].split(',')]
        #         elif args[i] == 'weight':  # How much is taking this class worth
        #             weight = float(args[i+1])
        #         elif args[i].startswith('#'): # Comments
        #             break
        #         else:
        #             raise Exception(f"Invalid arguments: {args}")
        #     self.requests.append(Request(cids, quarters, prereqs, weight))
        #     continue
        count = 0
        for course in bulletin.courses.values():
            # print(course["quarters"])
            self.requests.append(
                Request(course["cid"], course["quarters"], course["prereqs"], 1)
            )
            count += 1
            if count == 5:
                break
        # print(self.requests)

        # raise Exception(f"Invalid command: '{line}'")

        # # Determine any missing prereqs and validate the request.
        # self.taken = set(self.taken)
        # self.taking = set()

        # add every course as request

        # # Make sure each requested course is taken only once
        # for req in self.requests:
        #     for cid in req.cids:
        #         if cid in self.taking:
        #             raise Exception(f'Cannot request {cid} more than once')
        #     self.taking.update(req.cids)

        # # Make sure user-designated prerequisites are requested
        # for req in self.requests:
        #     for prereq in req.prereqs:
        #         if prereq not in self.taking:
        #             raise Exception("You must take " + prereq)

        # # Add missing prerequisites if necessary
        # for req in self.requests:
        #     for cid in req.cids:
        #         course = self.bulletin.courses[cid]
        # for prereq_cid in course.prereqs:
        #     if prereq_cid in self.taken:
        #         continue
        #     elif prereq_cid in self.taking:
        #         if prereq_cid not in req.prereqs:
        #             req.prereqs.append(prereq_cid)
        #             print(f'INFO: Additional prereqs inferred: {cid} after {prereq_cid}')
        #     else:
        #         print(f"WARNING: missing prerequisite of {cid} -- \
        #                 {self.bulletin.courses[prereq_cid].short_str()}; \
        #                 you should add it as 'taken' or 'request'")

    def print_info(self) -> None:
        print(f"Units: {self.minUnits}-{self.maxUnits}")
        print(f"Quarter: {self.quarters}")
        print(f"Taken: {self.taken}")
        print("Requests:")
        for req in self.requests:
            print(f"  {req}")

    def ensure_course_id(self, cid: str) -> str:
        if cid not in self.bulletin.courses:
            raise Exception("Invalid course ID: '%s'" % cid)
        return cid

    def ensure_quarter(self, quarter: str) -> str:
        if quarter not in self.quarters:
            raise Exception("Invalid quarter: '%s'" % quarter)
        return quarter


def extract_course_scheduling_solution(profile: Profile, assign: Dict) -> List[Tuple]:
    """
    Given an assignment returned from the CSP solver, reconstruct the plan. It
    is assume that (req, quarter) is used as the variable to indicate if a request
    is being assigned to a speific quarter, and (quarter, cid) is used as the variable
    to indicate the number of units the course should be taken in that quarter.

    @param profile: A student's profile and requests
    @param assign: An assignment of your variables as generated by the CSP
        solver.

    @return result: return a list of (quarter, courseId, units) tuples according
        to your solution sorted in chronological of the quarters provided.
    """
    result: List[Tuple] = []  # Any, str, None
    if not assign:
        return result
    for quarter in profile.quarters:
        for req in profile.requests:
            cid = assign[(req, quarter)]
            if cid is None:
                continue
            if (cid, quarter) not in assign:
                result.append((quarter, cid, None))
            else:
                result.append((quarter, cid, assign[(cid, quarter)]))
    return result


def print_course_scheduling_solution(solution: List[Tuple]) -> None:
    """
    Print a schedule in a nice format based on a solution.

    @para solution: A list of (quarter, course, units). Units can be None, in which
        case it won't get printed.
    """

    if solution is None or solution == []:
        print("No schedule found that satisfied all the constraints.")
    else:
        print("Here's the best schedule:")
        print("Quarter\t\tUnits\tCourse")
        for quarter, course, units in solution:
            if units is not None:
                print(("  %s\t%s\t%s" % (quarter, units, course)))
            else:
                print(("  %s\t%s\t%s" % (quarter, "None", course)))
