from backend.employee import Employee, InvalidEmployeeData, WorkMode
from backend.enums import EmploymentType


class FullTimeEmployee(Employee):
    def __init__(
        self,
        employee_id: str,
        name: str,
        department: str,
        job_title: str,
        monthly_salary: float,
        bonus: float = 0,
        work_mode: WorkMode = WorkMode.ONSITE,
    ):
        super().__init__(employee_id, name, department, job_title, work_mode)
        self.monthly_salary = monthly_salary
        self.bonus = bonus

    @property
    def monthly_salary(self) -> float:
        return self.__monthly_salary

    @monthly_salary.setter
    def monthly_salary(self, value: float) -> None:

        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"Monthly salary, Should be Integer OR Float not {type(value).__name__}"
            )

        if value <= 0:
            raise InvalidEmployeeData("Monthly salary Should be greater than $0")
        self.__monthly_salary = float(value)

    @property
    def bonus(self) -> float:
        return self.__bonus

    @bonus.setter
    def bonus(self, value: float) -> None:

        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"Bonus, Should be Integer OR Float not {type(value).__name__}"
            )

        if value < 0:
            raise InvalidEmployeeData("Bonus should not be negative!")
        self.__bonus = float(value)

    def calculate_gross_pay(self) -> float:
        """Calculate total salary \n
        Formula = monthly_salary + bonus + (allowance => if Remote)"""
        allowance = (
            self.remote_profile.calculate_allowance()
            if self.remote_profile is not None
            else 0
        )
        return float(self.monthly_salary + self.bonus + allowance)

    # return static value = Full-Time
    @property
    def employment_type(self) -> str:
        return EmploymentType.FULL_TIME.value

    def add_bonus(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise InvalidEmployeeData(
                f"Bonus not Added, Should be Integer OR Float not {type(amount).__name__}"
            )
        if amount < 0:
            raise InvalidEmployeeData("Bonus Should not be negative!!")
        self.bonus = self.bonus + float(amount)

    def apply_raise(self, percentage: float) -> None:
        if not isinstance(percentage, (int, float)):
            raise InvalidEmployeeData(
                f"salary raise percentage not Added, Should be Integer OR Float not {type(percentage).__name__}"
            )
        if percentage < 0:
            raise InvalidEmployeeData("Salary raise percentage can't be negative!! ")
        self.monthly_salary += self.monthly_salary * (percentage / 100)

    def get_details(self) -> dict:
        y = {
            "monthly_salary": self.monthly_salary,
            "bonus": self.bonus,
            "total_salary": self.calculate_gross_pay(),
        }
        x = super().get_details()
        x.update(y)
        return x

    def __str__(self) -> str:
        return (
            f"{super().__str__()}\n"
            f"Monthly Salary: {self.monthly_salary:.2f}\n"
            f"Bonus: {self.bonus:.2f}\n"
            f"Total Salary: {self.calculate_gross_pay():.2f}"
        )
