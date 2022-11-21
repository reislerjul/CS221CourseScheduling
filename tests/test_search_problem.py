# import pytest
#
# from ..search_problem import FindCourses


# @pytest.mark.parametrize()
# def test_search_problem_init():  # TO BE UPDATED
#     """
#     [Comment to follow]
#     """


# @pytest.mark.parametrize()
# def test_get_actions():  # TO BE UPDATED
#     """
#     [Comment to follow]
#     """


# Need to create scenarios by hand and check our program runs them. All kinds of edge cases.
# 1 term scenario:
# 2 classes to choose from
# 4 classes
# Classes with various units
# Someone has no remaining units in Foundations so would do electives

# 2 term scenario (will have to call it twice)
# Doesn’t repeat classes
# Similar approach to 1 term


# @pytest.mark.parametrize()
# def test_get_quarter_costs():  # TO BE UPDATED
#     """
#     [Comment to follow]
#     """


# Ensure quarter indices are all within correct range
# Check no state has an incrementally negative reward
# (Sum of units * max score) - sum(rewards for a course * units for that course): to
# ensure that number of courses doesn’t drive reward score
# Pass in varying number of courses


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
