from abc import ABC, abstractmethod
from datetime import date

from backend.enums import EmployeeStatus, WorkMode
from backend.exceptions import InvalidEmployeeData, InvalidStateTransition
from backend.remote_work_profile import RemoteWorkProfile


# Parent class for all other child
class Employee(ABC):
    """
    Top parent Class That inherited from all other employees subclasses.
    Abstracted and encapsulated well :)
    this class define which features and methods should other subclass have
    Big Baba :D
    """

    def __init__(
        self,
        employee_id: str,
        name: str,
        department: str,
        job_title: str,
        work_mode: WorkMode = WorkMode.ONSITE,
    ):

        # Data validation before initialize
        if not isinstance(employee_id, str):
            raise InvalidEmployeeData(
                f"employee id, Should be String not {type(employee_id).__name__}, Example: 'E001'"
            )

        if not employee_id or not employee_id.strip():
            raise InvalidEmployeeData("employee id should not be empty!")

        if not isinstance(work_mode, WorkMode):
            raise InvalidEmployeeData(
                f"employee work mode, Should be WorkMode(EnumType) not {type(work_mode).__name__}, Example: WorkMode.ONSITE"
            )

        self.__employee_id = employee_id.strip().upper()
        self.__work_mode = work_mode
        self.__hire_date = date.today()  # noqa
        self.__status = EmployeeStatus.ACTIVE
        self.__remote_profile = None

        self.name = name
        self.department = department
        self.job_title = job_title

    # getters
    @property
    def employee_id(self) -> str:
        return self.__employee_id

    @property
    def work_mode(self) -> WorkMode:
        return self.__work_mode

    @property
    def status(self) -> EmployeeStatus:
        return self.__status

    @property
    def hire_date(self) -> date:
        return self.__hire_date

    @property
    def remote_profile(self) -> RemoteWorkProfile | None:
        return self.__remote_profile

    # Getters + Setters
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise InvalidEmployeeData(
                f"employee name, Should be String not {type(value).__name__}, Example: 'Mahmoud'"
            )

        if not value or not value.strip():
            raise InvalidEmployeeData("employee name should not be empty!")
        self.__name = value.strip().title()

    @property
    def department(self) -> str:
        return self.__department

    @department.setter
    def department(self, value):
        if not isinstance(value, str):
            raise InvalidEmployeeData(
                f"employee department, Should be String not {type(value).__name__}, Example: 'finance'"
            )

        if not value or not value.strip():
            raise InvalidEmployeeData("employee department should not be empty!")
        self.__department = value.strip().title()

    @property
    def job_title(self) -> str:
        return self.__job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise InvalidEmployeeData(
                f"employee job title, Should be String not {type(value).__name__}, Example: 'AI Engineer'"
            )

        if not value or not value.strip():
            raise InvalidEmployeeData("employee job title should not be empty!")
        self.__job_title = value.strip().title()

    # abstracted methods
    @abstractmethod
    def calculate_gross_pay(self) -> float:
        pass

    # abstract property
    @property
    @abstractmethod
    def employment_type(self) -> str:
        pass

    # instance methods
    # Take a Profile for remote employee
    def attach_remote_profile(self, profile: RemoteWorkProfile):
        if self.work_mode != WorkMode.REMOTE:
            raise InvalidEmployeeData(
                f"the employee should be Remote, not {self.work_mode.value}"
            )
        if not isinstance(profile, RemoteWorkProfile):
            raise InvalidEmployeeData("profile must be a RemoteWorkProfile instance")

        self.__remote_profile = profile

    # change employee status to On leave
    def put_on_leave(self):
        if self.status == EmployeeStatus.ON_LEAVE:
            raise InvalidStateTransition(self.status.value, self.status.value)
        self.__status = EmployeeStatus.ON_LEAVE

    # return to Active if status is on leave
    def return_from_leave(self):
        if self.status != EmployeeStatus.ON_LEAVE:
            raise InvalidStateTransition(
                self.status.value, EmployeeStatus.ON_LEAVE.value
            )
        self.__status = EmployeeStatus.ACTIVE

    # employee Terminated and can't be return fired :)
    def terminate(self):
        if self.status == EmployeeStatus.TERMINATED:
            raise InvalidStateTransition(self.status.value, self.status.value)
        self.__status = EmployeeStatus.TERMINATED

    # return a good dict to show it at GUI
    def get_details(self) -> dict:
        return {
            "id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "job_title": self.job_title,
            "hire_date": self.hire_date,
            "status": self.status.value,
            "work_mode": self.work_mode.value,
            "remote_location": self.remote_profile.location
            if self.remote_profile
            else None,
            "remote_allowance": self.remote_profile.calculate_allowance()
            if self.remote_profile
            else 0.0,
        }

    # for testing and debugging :)
    def __str__(self) -> str:
        return (
            f"ID: {self.employee_id}\n"
            f"Name: {self.name}\n"
            f"Department: {self.department}\n"
            f"Job Title: {self.job_title}\n"
            f"Hire Date: {self.hire_date}\n"
            f"Status: {self.status.value}\n"
            f"Work Mode: {self.work_mode.value}\n"
            f"remote_location: {self.remote_profile.location if self.remote_profile else None}\n"
            f"remote_allowance: {f'{self.remote_profile.calculate_allowance():.2f}' if self.remote_profile else f'{0:.2f}'}"
        )
