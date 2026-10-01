from backend.employee import Employee, InvalidEmployeeData, WorkMode
from backend.enums import EmploymentType


class PartTimeEmployee(Employee):
    def __init__(
        self,
        employee_id: str,
        name: str,
        department: str,
        job_title: str,
        hourly_rate: float,
        hours_worked: float = 0,
        work_mode: WorkMode = WorkMode.ONSITE,
    ):
        super().__init__(employee_id, name, department, job_title, work_mode)
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked

    @property
    def hourly_rate(self) -> float:
        return self.__hourly_rate

    @hourly_rate.setter
    def hourly_rate(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"Hourly Rate Should be integer or float, not {type(value).__name__}"
            )
        if value <= 0:
            raise InvalidEmployeeData("hourly rate should be greater than zero!")
        self.__hourly_rate = float(value)

    @property
    def hours_worked(self) -> float:
        return self.__hours_worked

    @hours_worked.setter
    def hours_worked(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"Hours Worked Should Be Integer OR Float, not {type(value).__name__}"
            )
        if value < 0:
            raise InvalidEmployeeData("hours worked should not be negative!")
        self.__hours_worked = float(value)

    def calculate_gross_pay(self) -> float:
        """Calculate total salary \n
        Formula = (hourly rate x hours worked) + (allowance => if Remote)"""
        allowance = (
            self.remote_profile.calculate_allowance()
            if self.remote_profile is not None
            else 0
        )
        return float((self.hourly_rate * self.hours_worked) + allowance)

    # return static value = Part-Time
    @property
    def employment_type(self) -> str:
        return EmploymentType.PART_TIME.value

    def update_rate(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise InvalidEmployeeData(
                f"Hours can't updated because Amount should be [Integer OR Float], not {type(amount).__name__}"
            )
        if amount < 0:
            raise InvalidEmployeeData("Hours rate Should not be negative!!")
        self.hourly_rate = float(amount)

    def update_hours(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise InvalidEmployeeData(
                f"Hours can't updated because Amount should be [Integer OR Float], not {type(amount).__name__}"
            )
        if amount < 0:
            raise InvalidEmployeeData("Hours Should not be negative!!")
        self.hours_worked = float(amount)

    def get_details(self) -> dict:
        y = {
            "hourly_rate": self.hourly_rate,
            "hours_worked": self.hours_worked,
            "total_salary": self.calculate_gross_pay(),
        }
        x = super().get_details()
        x.update(y)
        return x

    def __str__(self) -> str:
        return (
            f"{super().__str__()}\n"
            f"Hourly Rate: {self.hourly_rate:.1f}\n"
            f"Hours Worked: {self.hours_worked:.1f}\n"
            f"Total Salary: {self.calculate_gross_pay():.2f}"
        )
