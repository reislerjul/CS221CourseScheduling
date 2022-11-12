import pickle
import collections
import os
from explorecourses import CourseConnection
from course import Course

QUARTER_TO_INDEX = {
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
        output_dir="course_info",
    ):
        """
        years: a list of possible academic year that the course is offered. Every year interval should be 1 year.

        departments: a list of departments that we want to extract for course planning.

        output_dir: the directory that saves the extracted course info
        """
        self.connect = CourseConnection()
        # Sort the years first so that the following course mapping is in sequence
        self.years = sorted(years)
        self.depts = departments
        self.output_dir = output_dir

        # Check if course information pickle exists
        # If yes, extract from explorecourses api; extract from file otherwise
        extract = False
        for year in self.years:
            for dept in self.depts:
                if not os.path.exists(
                    os.path.join(self.output_dir, f"{year}_{dept}.pickle")
                ):
                    print("No pickle file available, will extract from explorecourses.")
                    extract = True
        if extract:
            self.courses_by_quarter = self.run()
        else:
            self.courses_by_quarter = self.course_to_class_database()

    def run(self):
        """
        Currently only extracting courses from CS, EE and ICME department

        Output courses sorted by year and department in self.output_dir/{year}_{dept}.pickle
        """
        # self.all_courses is used for easier lookup between course title and course object
        self.all_courses = {}
        # self.courses stores all courses extracted from explorecourses by year
        self.courses = collections.defaultdict(list)
        # course_by_year_dept stores dict[year][department] = [list of course objects]
        course_by_year_dept = collections.defaultdict(dict)
        # course_by_quarter stores dict[quarter_indices] = [list of course objects]
        course_by_quarter = collections.defaultdict(list)

        print("Connecting to explorecourses...")
        print("Current extracting years:", " ".join(self.years))
        print("Current extracting departments:", " ".join(self.depts))

        for year in self.years:
            for dept in self.depts:
                cur_courses = self.connect.get_courses_by_department(dept, year=year)
                self.courses[year] = self.courses[year] + cur_courses
                for i in range(len(cur_courses)):
                    course = cur_courses[i]
                    # TODO: what to put in reward, putting 0 for placeholder
                    """
                    reward: float,
                    units: tuple of (min_unit, max_unit)
                    course_number: string of unique course ID
                    course_name: string of full name of the course
                    quarter_indices: tuple of available quarters,
                    """
                    single_course_object = Course(
                        0,
                        (course.units_min, course.units_max),
                        str(course.course_id),
                        course.title,
                        (),
                    )
                    self.all_courses[course.title] = single_course_object

        print("Extraction ended! Start processing courses...")

        # Update all possible quarters after reading in all the courses
        for year in range(len(self.years)):
            cur_year = self.years[year]
            year_courses = self.courses[cur_year]
            for i in range(len(year_courses)):
                cur_course = year_courses[i]
                total_term = []
                for j in range(len(cur_course.sections)):
                    _, term = cur_course.sections[j].term.split()
                    # Four quarters per year
                    term_ind = QUARTER_TO_INDEX[term] + 4 * year
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

                # Populate course_by_year_dept to be stored in pickle files
                dept = cur_course.subject
                course_by_year_dept[cur_year][dept] = course_by_year_dept[cur_year].get(
                    dept, []
                ) + [self.all_courses[cur_course.title]]

        if not os.path.exists(self.output_dir):
            print("Creating new path to", self.output_dir)
            os.mkdir(self.output_dir)

        for year, val in course_by_year_dept.items():
            for dept, course_info in val.items():
                # Use pickle to store courses because the courses are of class "Course",
                # which stores more information
                # Can be extracted using pickle.load()
                with open(
                    os.path.join(self.output_dir, f"{year}_{dept}.pickle"), "wb"
                ) as handle:
                    pickle.dump(course_info, handle)
                print(
                    "File saved to",
                    os.path.join(self.output_dir, f"{year}_{dept}.pickle"),
                )

        return course_by_quarter

    def course_to_class_database(self):
        """
        Convert the extracted courses to dict[quarter_number] = (all courses available in the quarter)
        """

        course_by_quarter = collections.defaultdict(list)
        # listed avoids duplicates by storing all processed course_number
        listed = []

        for year in self.years:
            for dept in self.depts:
                # Read in courses by the specified years and departments
                with open(
                    os.path.join(self.output_dir, f"{year}_{dept}.pickle"), "rb"
                ) as handle:
                    cur_course = pickle.load(handle)
                for i in range(len(cur_course)):
                    quarter_indices = cur_course[i].quarter_indices
                    for quart in quarter_indices:
                        if cur_course[i].course_number not in listed:
                            course_by_quarter[quart].append(cur_course[i])
                    listed.append(cur_course[i].course_number)

        return course_by_quarter


# A simple test case to see the course outputs
# new = CoursesDeterministic(departments=["CME"]).courses_by_quarter
# for key, val in new.items():
#    for j in range(len(val)):
#        print(key, val[j].course_name, val[j].course_number, val[j].quarter_indices)
