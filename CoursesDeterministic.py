import pickle
import collections
from explorecourses import CourseConnection
from Course import Course

INDEX_QUARTER = {
    "Autumn": 1,
    "Winter": 2,
    "Spring": 3,
    "Summer": 4,
}


class CoursesDeterministic:
    """
    A Courses Deterministic Class use explorecourse API to grab the courses from each department (CS, EE, and ICME).

    The data pulled in this class will be used to populate the Course and ExploreCourse class
    """

    def __init__(
        self,
        years=["2021-2022", "2022-2023"],
        departments=["CS", "EE", "CME"],
        extract_courses=True,
    ):
        """
        path: string input to the path that stores the course information from ExploreCourses API.

        years: a list of possible academic year that the course is offered. Every year interval should be 1 year.

        departments: a list of departments that we want to extract for course planning.

        extract_courses: a boolean value indicating if we want to extract the courses online, or read from
        file storing course information
        """
        self.connect = CourseConnection()
        # Sort the years first so that the following course mapping is in sequence
        self.years = sorted(years)
        self.depts = departments
        if extract_courses:
            self.course_extraction()

        self.create_course_object()
        self.course_to_class_database()

    def course_extraction(self, outputfile="courses"):
        """
        Currently only extracting courses from CS, EE and ICME department

        outputfile: the location of file to serialize the list of courses.
        """
        # Extract into dicts so that the courses are saved according to years
        self.courses = {}
        for year in self.years:
            for dept in self.depts:
                self.courses[year] = self.connect.get_courses_by_department(
                    dept, year=year
                )

        # Use pickle to store courses because the courses are of class "Course",
        # which stores more information
        # Can be extracted using pickle.load()
        with open(outputfile + ".pickle", "wb") as handle:
            pickle.dump(self.courses, handle)

    def create_course_object(self, inputfile="courses"):
        """
        Return units, course number, course name, quarter indices
        """
        with open(inputfile + ".pickle", "rb") as handle:
            self.courses = pickle.load(handle)

        self.all_courses = {}
        for year in range(len(self.years)):
            courses_per_year = self.courses[self.years[year]]
            for j in range(len(courses_per_year)):
                single_course = courses_per_year[j]
                # Save a single copy of a single course
                if single_course.title not in self.all_courses:
                    # TODO: what to put in reward, putting 0 for placeholder
                    """
                    reward: float,
                    units: tuple of (min_unit, max_unit)
                    course_number: string of unique course ID
                    course_name: string of full name of the course
                    quarter_indices: tuple of available quarters,
                    """
                    # set quarter_indices to () and wait for it to be populated in course_to_class_database()
                    single_course_object = Course(
                        0,
                        (single_course.units_min, single_course.units_max),
                        str(single_course.course_id),
                        single_course.title,
                        (),
                    )
                    self.all_courses[single_course.title] = single_course_object

    def course_to_class_database(self):
        """
        Convert the extracted courses to dict[quarter_number] = (all courses available in the quarter)
        """
        course_by_quarter = collections.defaultdict(list)

        for year in range(len(self.years)):
            year_courses = self.courses[self.years[year]]
            for i in range(len(year_courses)):
                cur_course = year_courses[i]
                total_term = []
                for j in range(len(cur_course.sections)):
                    _, term = cur_course.sections[j].term.split()
                    # Four quarters per year
                    term_ind = INDEX_QUARTER[term] + 4 * year
                    total_term.append(term_ind)
                # Update the quarter_indices
                total_term = list(set(total_term)) + list(
                    self.all_courses[cur_course.title].quarter_indices
                )
                self.all_courses[cur_course.title].quarter_indices = tuple(
                    set(total_term)
                )

                # Update for course_by_courter and avoid duplicates
                for term in total_term:
                    course_by_quarter[term] = list(
                        set(
                            course_by_quarter[term]
                            + [self.all_courses[cur_course.title]]
                        )
                    )
        return course_by_quarter


# A simple test case to see the course outputs
# new = CoursesDeterministic(departments=["CME"]).course_to_class_database()
# for key, val in new.items():
#    for j in range(len(val)):
#        print(key, val[j].course_name, val[j].course_number, val[j].quarter_indices)
