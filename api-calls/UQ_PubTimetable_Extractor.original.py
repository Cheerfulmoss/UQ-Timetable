"""
Written: Oliver Sparrow

Original version of the API tool, for posterity :)

License: GPL3
"""

import requests
import datetime as dt

################################################################################

class CourseTimetable:

    # Reference Arrays, for the parameters of an API Request
    semesters = ["ALL", "S1", "S2", "S3"]
    campus = ["ALL", "STLUC", "HERST", "GATTN"]
    form = ["IN", "EX"]

    
    def __init__(self, course : str, sem_no : int = 0,
                     campus_id : int = 0, form_type : int = 0):

        self.course_versions = self.requestCourses(course, sem_no, campus_id)
        course_id = f"{course}_{self.semesters[sem_no]}_{self.campus[campus_id]}_{self.form[form_type]}"

        if course_id in self.course_versions:
            self.course = self.course_versions[course_id]

        elif not self.course_versions:
            raise ValueError("Invalid combination entered!")

        else:
            print(
                "Request parameters were too ambiguous.", 
                "So, first option was selected."
            )
            self.course = self.course_versions[list(self.course_versions)[0]]
            for version in self.course_versions:
                if version.split("_")[-1] == self.form[form_type]:
                    self.course = self.course_versions[version]
                    break

        self.setActivities()


    def requestCourses(self, course : str, sem_no : int = 0,
                              campus_id : int = 0):
        url = "https://timetable.my.uq.edu.au/odd/rest/timetable/subjects"
        data = {
            "search-term": course,
            "semester": self.semesters[sem_no],
            "campus": self.campus[campus_id],
            "faculty": "ALL",
            "type": "ALL",
            "days": [1, 2, 3, 4, 5, 6, 0],
            "start-time": "00:00",
            "end-time": "23:00"
        }
        return requests.post(url, data=data).json()



    def setActivities(self):
        self.activities = {}
        
        for activity in (activities := self.course["activities"]):

            activity_code = activities[activity]["activity_group_code"] + " " + activities[activity]["activity_code"]
            start_time = dt.datetime.strptime(
                activities[activity]["start_time"],
                "%H:%M"
            )
            end_time = start_time + dt.timedelta(
                minutes=int(activities[activity]["duration"])
            )
            
            self.activities[activity_code] = {
                "activity_code": activity_code,
                "activity": activities[activity]["activity_type"],
                "day": activities[activity]["day_of_week"],
                "location": activities[activity]["location"],
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "schedule": activities[activity]["activitiesDays"],
                # Warning: The following two entries can be
                #   EXTREMELY nonsensical!!! Use with caution...
                "is_open": activities[activity]["selectable"],
                "spots": activities[activity]["availability"]
            }

    
    def getCourseList(self):
        return list(self.course_versions)
    

    def getCourse(self):
        return self.course

    
    def getActivities(self):
        return self.activities


    def getSubActivities(self, activity_type):
        acts = self.getActivities()
        return [
            acts[activity]
            for activity in acts
            if acts[activity]["activity"] == activity_type
        ]

    
    def getLectures(self):
        return self.getSubActivities("Lecture")

    
    def getTutorials(self):
        return self.getSubActivities("Tutorial")


    def getPracticals(self):
        return self.getSubActivities("Practical")


    def getWorkshops(self):
        return self.getSubActivities("Workshop")


    def getContacts(self):
        return self.getSubActivities("Contact")


    def getOthers(self):
        acts = self.getActivities()
        return [
            acts[activity]
            for activity in acts
            if (
                acts[activity] not in self.getLectures()
            ) and (
                acts[activity] not in self.getTutorials()
            ) and (
                acts[activity] not in self.getPracticals()
            ) and (
                acts[activity] not in self.getLectures()
            ) and (
                acts[activity] not in self.getWorkshops()
            )
        ]

################################################################################

course_obj = CourseTimetable("CSSE2010", sem_no=2, campus_id=1)
print(course_obj.getCourseList())
