import pandas as pd
import random

SENTIMENT_ANALYSIS = False


class ReviewSynthesizer:
    """
    Takes a csv created by ExploreCourse and uniformly randomly applies a Coursera course's
    review content (reviews and 1-5 score) to each course. It stores the result as a pd dataframe.
    Column key:
    "course_number" is Stanford course number
    "review" is a string containing a single review
    "label" is a review score on a 1-5 integer scale
    """

    # TODO: THIS FILE IS WORK IN PROGRESS! See points below
    """
    Needs to be integrated into courses_deterministic. 2 design questions to answer:
    1. do we want this class to read Stanford from a csv? Seems may be more efficient if this class can take
    Stanford course list as an array from courses_deterministic.
    2. I am just using a uniform random allocation of Coursera courses to Stanford courses. We may want to do
    something else. Also, we may want to filter the Coursera courses for number of reviews or some other
    proxy for quality. Some Coursera courses may only have 1 or 2 reviews associated with them.
    """

    def __init__(
        self,
        course_list_loc="../data/2022-2023_CS.csv",  # NEEDS FIXING WHEN INTEGRATED INTO COURSES_DETERMINISTIC
        coursera_file_loc="../data/coursera_reviews_by_course.csv",
    ):
        self.course_list_loc = course_list_loc
        self.coursera_file_loc = coursera_file_loc
        self.courses_with_reviews = pd.DataFrame()
        self.course_numbers = []
        self.course_syn_scores = {}

    def synthesize_reviews(self):
        course_list = pd.read_csv(self.course_list_loc)
        self.course_numbers = course_list["course_number"]
        coursera_reviews = pd.read_csv(self.coursera_file_loc)
        unique_coursera = coursera_reviews.CourseId.unique()
        courses_with_reviews = pd.DataFrame()
        for i in range(len(self.course_numbers)):
            selection = random.choice(unique_coursera)
            temp = coursera_reviews.loc[coursera_reviews["CourseId"] == selection]
            temp = temp.drop("CourseId", axis=1)
            temp.insert(loc=0, column="course_number", value=self.course_numbers[i])
            courses_with_reviews = courses_with_reviews.append(temp)
        self.courses_with_reviews = courses_with_reviews

    def get_synthetic_ratings(self):
        """

        Returns: dictionary self.course_syn_scores {course_num : review score} where course_num is digits of the course
        and "review score" is a float on a 1.0 to 5.0 scale.
        e.g. CS 229 with a review of 4.3 course_num is {229: 4.3}.

        TODO: add in sentiment analysis. Currently, review score is simply the median of the labels of the Coursera
        reviews randomly allocated by synthesize_reviews().
        """
        self.synthesize_reviews()
        if SENTIMENT_ANALYSIS:
            raise Exception("Not implemented yet")
        else:
            for course_num in self.course_numbers:
                course_num_reviews = self.courses_with_reviews.loc[
                    self.courses_with_reviews["course_number"] == course_num
                ]
                self.course_syn_scores[course_num] = course_num_reviews[
                    "Label"
                ].median()
            return self.course_syn_scores
