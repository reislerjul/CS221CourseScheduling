from typing import Dict, List


class State:
    """_summary_

    Args:
        current_quarter (int): _description_
        course_taken (Set): _description_
        remaining_units (Dict[str, int]): _description_
        remaining_instructors (List): _description_
        remaining_research (int): _description_
    """

    def __init__(
        self,
        current_quarter: int,
        course_taken: List,
        remaining_units: Dict[str, int],
        # Remaining desired professors
        remaining_instructors: List,
        # Remaining mandatory research units
        remaining_resesarch: int,
    ) -> None:
        self.current_quarter = current_quarter
        self.course_taken = course_taken
        self.remaining_units = remaining_units
        self.remaining_instructors = remaining_instructors
        self.remaining_research = remaining_resesarch

    def print_state(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(f"** Quarter **: {self.current_quarter}")
        print("---------------")

        print("** Remaining Units: **")
        for key, value in self.remaining_units.items():
            if value > 0:
                print(f"{key}: {value} units")
        print("---------------")

        print("** Courses taken so far: **")
        for course in self.course_taken:
            print(f"{course.course_number} {course.course_name}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
