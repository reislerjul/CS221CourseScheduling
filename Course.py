class Course:
    # TODO complete it
    """_summary_


    Args:
        reward (float): _description_
        units (tuple): _description_
        course_number (str): _description_
        course_name (str): _description_
        quarter_indices (tuple): _description_
    """

    def __init__(
        self,
        reward: float,
        units: tuple,
        course_number: str,
        course_name: str,
        quarter_indices: tuple,
    ) -> None:

        self.reward = reward
        self.units = units
        self.course_number = course_number
        self.course_name = course_name
        self.quarter_indices = quarter_indices
