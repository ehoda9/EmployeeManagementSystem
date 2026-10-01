from enum import Enum, unique


@unique
class EmploymentType(Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"


@unique
class WorkMode(Enum):
    ONSITE = "On-Site"
    HYBRID = "Hybrid"
    REMOTE = "Remote"


@unique
class EmployeeStatus(Enum):
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    TERMINATED = "Terminated"
