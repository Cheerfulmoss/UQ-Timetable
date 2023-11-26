"""
TO DO:
Implement 4 methods
process_conditions: process the timetable into a group of hard constraints

apply_arc: apply arc-consistency to the domain and return the arc-consistent domain
    - Returns failure if an arc-consistent domain cannot be found.
    - Should only accept hard constraints - i.e. the ones that must be satisfied, such as
      there must be no clashes between non-clashable clashes, must enrol in one and only
      one prac etc.
    - Should accept a list of hard constraints and the domain

method_1: solve the constraint satisfaction problem and return a list of solutions

method_2: rate solution with some reward funtion and order them based on the score.
    Should accept a list/dict of reward functions and a single solution from method_1
    Return a dictionary with keys being the score and values being the plan.

    Note: It would be good to have some constants to represent each reward function
    e.g. 0 stands for classes at 8 am

    Suggestions for available score conditions (Anyone can add to it):
    - negative reward for classes too early (because we all hate classes at 8 am)
    - Avoid having 8 hours of class in one day?
    - Maybe customize time frame to avoid?
"""
import timetable_api_calls

def process_conditions(course: timetable_api_calls.CourseTimetable):
    """
    :param course: a CourseTimetable that contains everything
    :return: A list of hard binary constraints

    Note: binary constraint means a constraint between two variables.
    """
    pass


