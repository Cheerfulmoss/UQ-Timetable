from enum import Enum
import logging
from constants.common import *


logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT)
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

    @classmethod
    def convert(cls, str_in: str) -> (Semester | Campus | Form | ActivityTypes
                                      | None):
        # Yes there is an issue of "ALL" being in two enums, I don't wanna
        # think about it honestly.
        for enum_class in cls.EnumBase.__subclasses__():
            try:
                return enum_class[str_in]
            except KeyError:
                pass

        err_msg = f"Given input cannot be converted, {str_in=}"
        logger.error(err_msg)
        raise ValueError(err_msg)
