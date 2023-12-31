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
from typing import Optional, Dict, Tuple

from api.timetable_api_calls import *
from api.TTableInputs import *

"""
I am currently unable to recall what is the key for courseID like 'CSSE2010' and for activity length
Therefore line 60 and line 64 will not work
Will fix it later when API is back.
"""
class Solver:
    def __init__(self, courses: Optional[list[CourseTimetable]] = None):
        self.variables = []  # Initialise variables to be an empty list
        self.domains = {}  #Initialise a dictionary of domains
        self.length_constraint = {}
        self.intersect_constraints = [] # basically, the variables that must not intersect
        # for example, if a delayed lecture is assigned, we do not need to worry about it, so we will remove it from
        # intersect constraints. By default, every variable will be in the intersect constraint.

        if courses != None:
            for course in courses:
                self.process_conditions(course)

    def process_conditions(self, course: CourseTimetable):
        """
        :param course: a CourseTimetable that contains everything
        :return: A list of hard binary constraints

        Note: binary constraint means a constraint between two variables.
        """
        for activity in course.get_activities().values():
            code = activity.get("activity_code")
            if code not in self.variables:
                activity_id = (course.get_course()[0] + activity.get("activity_code")) # FIX!
                self.variables.append(activity_id)
                self.domains[code] = list()
                self.intersect_constraints.append(activity.get("activity_code"))
                self.length_constraint[activity_id] = None # FIX!


    """
    :var assignment: the dictionary representing the assigned values
         The key should be a tuple in the format of (course_code, activity_code)
         and value should be a tuple in the format of (day, start_time, end_time)
         where day must be an integer in range(1, 6)
         start_time and end_time must be in DAY_TIME_FORMAT
    """
    def check_intersect_constraints(self, assignment:dict[tuple[str, str], tuple[int, str, str]]) -> bool:
        pass

"""
Variables are the activities. 'activity-group-code'
Domains are everything inside the group
if activity == 'Delayed' then it is Clashable
"""




if __name__ == "__main__":
    course1 = CourseTimetable(course="CSSE2010",
                              semester=TTableInputs.Semester.S2,
                              campus_id=TTableInputs.Campus.STLUC,
                              form_type=TTableInputs.Form.IN)
    print(course1.course_versions)
    # act1 = course1.get_activities()
    # for i, j in act1.items():
    #     print(i, j)
    # course2 = CourseTimetable(course="CSSE2002", semester=TTableInputs.Semester.S2)
    # act2 = course2.get_activities()
    # print(act1, act2)
    # print(course1.get_overlap(course1,"CSSE2010-S2-STLUC-IN|LEC1|01",course2,"CSSE2002-S2-STLUC-IN|LEC1|01"))
