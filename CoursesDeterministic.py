from explorecourses import CourseConnection


class CoursesDeterministic:
    """
    A Courses Deterministic Class use explorecourse API to grab the courses from each department (CS, EE, and ICME).

    The data pulled in this class will be used to populate the Course and ExploreCourse class
    """

    def __init__(self, year="2022-2023"):
        """
        path: string input to the path that stores the course information from ExploreCourses API

        year: the academic year that the course is offered.

        by_quarter: True if we want to extract courses by quarter; False if we want to extract for the whole year

        """
        self.connect = CourseConnection()
        self.year = year
        self.course_extraction()

    def course_extraction(self):
        """
        Currently only extracting courses from CS, EE and ICME department
        """
        for dept in ["CS", "EE", "CME"]:
            self.courses = self.connect.get_courses_by_department(dept, year=self.year)

    def course_to_Course(self):
        """
        Return units, course number, course name, quarter indices
        """
        raise NotImplementedError("Not implemented yet.")

    def course_to_ExploreCourse(self):
        """
        Convert the extracted courses to dict[quarter_name] = (all courses in the quarter)
        """
        courses = {"Autumn": [], "Winter": [], "Spring": [], "Summer": []}
        for i in range(len(self.courses)):
            cur_course = self.courses[i]
            for j in range(len(cur_course.sections)):
                _, term = cur_course.sections[j].term.split()
                courses[term].append(cur_course)
        return courses
