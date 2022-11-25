import pandas as pd
import random


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
    1. do we want this class to read Stanford from a csv? Seems may be more efficient if it can take
    Stanford course list as an array.
    2. where do we want to store the courses with reviews? It makes sense to keep it as a separate dataframe,
    and I suggest we store that dataframe as an instance variable of CoursesDeterministic.
    3. I am just using a uniform random allocation of coursera courses to Stanford courses. We may want to do
    something else. Also, we may want to filter the coursera courses for number of reviews or some other
    proxy for quality.
    """

    def __init__(
        self,
        course_list_loc="../data/2022-2023_CS.csv",  # NEEDS FIXING WHEN INTEGRATED INTO COURSES_DETERMINISTIC
        coursera_file_loc="../data/coursera_reviews_by_course.csv",
    ):
        course_list = pd.read_csv(course_list_loc)
        course_numbers = course_list["course_number"]
        coursera_reviews = pd.read_csv(coursera_file_loc)
        unique_coursera = coursera_reviews.CourseId.unique()
        courses_with_reviews = pd.DataFrame(
            columns=["course_number", "review", "label"]
        )
        for i in range(len(course_numbers)):
            selection = random.choice(
                unique_coursera
            )  # note this is with replacement, which we may not want
            temp = coursera_reviews.loc[coursera_reviews["CourseId"] == selection]
            temp = temp.drop("CourseId", axis=1)
            temp.insert(loc=0, column="course_number", value=course_numbers[i])
            courses_with_reviews = courses_with_reviews.append(temp)
        self.courses_with_reviews = courses_with_reviews

    def get_courses_with_reviews(self):
        return self.courses_with_reviews


def main():
    ReviewSynthesizer()


if __name__ == "__main__":
    main()
