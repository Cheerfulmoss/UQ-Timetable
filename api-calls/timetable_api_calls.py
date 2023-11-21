"""
Written: not me, asking how to credit orignal author now 
Edited: Alexander Burow

License: GPL3
"""

import requests
import logging
import datetime as dt
from enum import Enum

################################################################################

## CONSTANTS
TIMETABLE_API_URL = "https://timetable.my.uq.edu.au/odd/rest/timetable/subjects"
DATETIME_FORMAT = "%H:%M"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TTableInputs:
    class EnumBase(Enum):
        def __str__(self):
            return self.value

    class Semester(EnumBase):
        ALL = "ALL"
        S1 = "S1"
        S2 = "S2"
        S3 = "S3"

    class Campus(EnumBase):
        ALL = "ALL"
        STLUC = "STLUC"
        HERST = "HERST"
        GATTN = "GATTN"

    class Form(EnumBase):
        IN = "IN"
        EX = "EX"

    class ActivityTypes(EnumBase):
        LEC = "Lecture"
        DEL = "Delayed"
        PRAC = "Practical"
        TUT = "Tutorial"
        CON = "Contact"
        WKSHP = "Workshop"


class CourseTimetable:
    def __init__(self, course: str,
                 semester: TTableInputs.Semester = TTableInputs.Semester.ALL,
                 campus_id: TTableInputs.Campus = TTableInputs.Campus.ALL,
                 form_type: TTableInputs.Form = TTableInputs.Form.IN) -> None:
        """Initialises a course object, with the given parameters.

        :param course: The course ID, e.g. "CSSE2010".
        :type course: str

        :param semester: The semester to select.
        :type semester: TTableInputs.Semester

        :param campus_id: The campus to select.
        :type campus_id: TTableInputs.Campus

        :param form_type: Whether to select the internal or external version
            of the course.
        :type form_type: TTableInputs.Form

        :rtype: None
        """
        self._input_validation(semester=semester, campus_id=campus_id,
                               form_type=form_type)

        self.course_versions = self.request_course(course, semester, campus_id)
        course_id = f"{course}_{semester}_{campus_id}_{form_type}"

        if course_id in self.course_versions:
            self.course = self.course_versions[course_id]

        elif not self.course_versions:
            err_msg = "API call returned empty. Invalid combination entered!"
            logger.error(err_msg)
            raise ValueError(err_msg)

        else:
            logger.warning("Request parameters were too ambiguous. So, "
                           "first option was selected.")
            self.course = self.course_versions[list(self.course_versions)[0]]
            for version in self.course_versions:
                if version.split("_")[-1] == form_type.value:
                    self.course = self.course_versions[version]
                    break

        self.activities = {}
        self.set_activities()

    @staticmethod
    def _input_validation(
            semester: TTableInputs.Semester = None,
            campus_id: TTableInputs.Campus = None,
            form_type: TTableInputs.Form = None,
            activity_type: TTableInputs.ActivityTypes = None) -> None:
        """Raises a ValueError if any of the given inputs are not valid.

        :param semester: The semester for which you want to view the courses.
        :type semester: TTableInputs.Semester

        :param campus_id: The campus for the course.
        :type campus_id: TTableInputs.Campus

        :param form_type: Whether it is internal or external.
        :type form_type: TTableInputs.Form

        :param activity_type: Activity is Lecture, tutorial, contact, etc
        :type activity_type: TTableInputs.ActivityTypes

        :rtype: None
        """
        errors = []

        if (not isinstance(semester, TTableInputs.Semester) and
                semester is not None):
            errors.append(f"Invalid {f'{semester=}'.split('=')[0]}:"
                          f" {semester}. "
                          f"Valid options are "
                          f"{list(TTableInputs.Semester.__members__.values())}")
        if (not isinstance(campus_id, TTableInputs.Campus) and
                campus_id is not None):
            errors.append(f"Invalid {f'{campus_id=}'.split('=')[0]}:"
                          f" {campus_id}. "
                          f"Valid options are "
                          f"{list(TTableInputs.Campus.__members__.values())}")
        if (not isinstance(form_type, TTableInputs.Form) and
                form_type is not None):
            errors.append(f"Invalid {f'{form_type=}'.split('=')[0]}:"
                          f" {form_type}. "
                          f"Valid options are "
                          f"{list(TTableInputs.Form.__members__.values())}")
        if (not isinstance(activity_type, TTableInputs.ActivityTypes) and
                activity_type is not None):
            errors.append(f"Invalid {f'{activity_type=}'.split('=')[0]}: "
                          f"{activity_type}. Valid options are "
                          f"{list(TTableInputs.ActivityTypes.__members__.values())}")
        if errors:
            err_msg = f"Input validation error/s: {' | '.join(errors)}"
            logger.error(err_msg)
            raise ValueError(err_msg)

    @staticmethod
    def request_course(course: str,
                       semester: TTableInputs.Semester = TTableInputs.Semester.ALL,
                       campus_id: TTableInputs.Campus = TTableInputs.Campus.ALL
                       ) -> dict:
        """Makes a request to timetable.my.uq.edu.au with given parameters.

        :param course: The course ID, e.g. "CSSE2010".
        :type course: str

        :param semester: The semester to select.
        :type semester: TTableInputs.Semester

        :param campus_id: The campus to select.
        :type campus_id: TTableInputs.Campus

        :return: A dictionary containing the timetable information for the
            specified course.
        :rtype: dict
        """
        data = {
            "search-term": course,
            "semester": semester.value,
            "campus": campus_id.value,
            "faculty": "ALL",
            "type": "ALL",
            "days": [1, 2, 3, 4, 5, 6, 0],
            "start-time": "00:00",
            "end-time": "23:59"
        }
        return requests.post(TIMETABLE_API_URL, data=data).json()

    def set_activities(self) -> None:
        """Filters returned activities for information we care about.

        This will probably have to change in the future to be a situation
        where it actually filters nothing but for now there's stuff from the
        api call that we don't need.

        :rtype: None
        """
        self.activities.clear()

        for activity, activity_info in self.course["activities"].items():
            activity_code = (
                f"{activity_info.get('activity_group_code')} "
                f"{activity_info.get('activity_code')}")
            start_time = dt.datetime.strptime(
                activity_info.get("start_time"),
                DATETIME_FORMAT
            )
            end_time = start_time + dt.timedelta(
                minutes=int(activity_info.get("duration"))
            )

            self.activities[activity_code] = {
                "activity_code": activity_code,
                "activity": activity_info.get("activity_type"),
                "day": activity_info.get("day_of_week"),
                "location": activity_info.get("location"),
                "start_time": start_time.strftime(DATETIME_FORMAT),
                "end_time": end_time.strftime(DATETIME_FORMAT),
                "schedule": activity_info.get("activitiesDays"),
                "colour": activity_info.get("color"),
                "department": activity_info.get("department"),
                # Warning: The following two entries can be
                #   EXTREMELY nonsensical!!! Use with caution...
                "is_open": activity_info.get("selectable"),
                "spots": activity_info.get("availability")
            }

    def get_course_list(self) -> list[str]:
        return list(self.course_versions)

    def get_course(self) -> str:
        return self.course

    def get_activities(self) -> dict:
        """Activities refers to Lectures, Tutorials, etc."""
        return self.activities

    def filter_activities(self,
                          activity_types: list[TTableInputs.ActivityTypes] |
                                          TTableInputs.ActivityTypes
                          ) -> dict[TTableInputs.ActivityTypes, list]:
        """Filters activities for only the given activity.

        Activities refers to Lectures, Tutorials, etc.

        :param activity_types: What activity to filter for.
        :type activity_types: list[TTableInputs.ActivityTypes] or
            TTableInputs.ActivityTypes

        :return: Returns a list of all activities which meet the filter
            criteria.
        :rtype: dict[TTableInputs.ActivityTypes, list]
        """
        if not isinstance(activity_types, list):
            activity_types = [activity_types]

        # I don't like iterating through the list twice but I don't think it
        # effects performance, and it's "safer".
        for activity in activity_types:
            self._input_validation(activity_type=activity)

        acts = self.get_activities()

        return {activity_type: [
            acts[activity]
            for activity in acts
            if acts[activity]["activity"] == activity_type.value
        ] for activity_type in activity_types}

    def get_lectures(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.LEC).get(
            TTableInputs.ActivityTypes.LEC)

    def get_tutorials(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.TUT).get(
            TTableInputs.ActivityTypes.TUT)

    def get_practicals(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.PRAC).get(
            TTableInputs.ActivityTypes.PRAC)

    def get_workshops(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.WKSHP).get(
            TTableInputs.ActivityTypes.WKSHP)

    def get_contacts(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.CON).get(
            TTableInputs.ActivityTypes.CON)

    def get_delayed(self) -> list[dict]:
        return self.filter_activities(
            TTableInputs.ActivityTypes.DEL).get(
            TTableInputs.ActivityTypes.DEL)

    def get_uncategorised(self) -> list[dict]:
        acts = self.get_activities()

        return [
            acts[activity]
            for activity in acts
            if (
                       acts[activity] not in self.get_lectures()
               ) and (
                       acts[activity] not in self.get_tutorials()
               ) and (
                       acts[activity] not in self.get_practicals()
               ) and (
                       acts[activity] not in self.get_contacts()
               ) and (
                       acts[activity] not in self.get_workshops()
               ) and (
                       acts[activity] not in self.get_delayed()
               )
        ]


################################################################################
if __name__ == "__main__":
    course_obj = CourseTimetable("MATH1071",
                                 semester=TTableInputs.Semester.S1,
                                 campus_id=TTableInputs.Campus.STLUC)
    print(course_obj.get_course_list())
    print(course_obj.get_activities())
    print(course_obj.get_uncategorised())
