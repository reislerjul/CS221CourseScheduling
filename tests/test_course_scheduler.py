# import pytest
#
# from src.course_scheduler import State
#

# @pytest.mark.parametrize()
# def test_courses_state_init():  # TO BE UPDATED
#     """
#     [Comment to follow]
#     """


# State:

# (1) Check member variables are incrementally updated correctly:
# current_quarter
# course_taken
# Remaining_units

# (2) Check they’re initialized correctly:
# Quarter_index is 0 before any courses taken?

# (3) Course_taken:
# Ensure no duplicates (maybe some exceptions? Eg seminars)
# Correct data type
# Check every new course is present in the dictionary

# (4) Check foundations, breadth, depth, electives are all keys in dict, and there are no other keys

# (5) IsEnd:
# Check requirements are satisfied at end of any term, or
# Has not fulfilled requirements before end of [2] years (should also return true)
# Returns False if not an end state

# (6) Successors_and_costs
# Same as get_quarter_cost, get_action tests, because this method will call those functions
