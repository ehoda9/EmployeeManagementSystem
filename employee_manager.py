from backend.employee import Employee
from backend.employee_operations import EmployeeOperations
from backend.enums import WorkMode
from backend.full_time_employee import FullTimeEmployee
from backend.part_time_employee import PartTimeEmployee
from backend.remote_work_profile import RemoteWorkProfile
from backend.tax_calculator import TaxCalculator


class EmployeeManager:
    """this is  link between the Back end and the frontEnd GUI"""

    #############################
    # create a full time employee
    @staticmethod
    def create_full_time_employee(
        employee_id: str,
        name: str,
        department: str,
        job_title: str,
        monthly_salary: float,
        bonus: float = 0,
        work_mode: WorkMode = WorkMode.ONSITE,
        remote_data: dict | None = None,
    ) -> FullTimeEmployee:

        emp = FullTimeEmployee(
            employee_id, name, department, job_title, monthly_salary, bonus, work_mode
        )
        if isinstance(remote_data, dict) and remote_data:
            profile = RemoteWorkProfile(**remote_data)
            emp.attach_remote_profile(profile)
        EmployeeOperations.add(emp)
        return emp

    #############################
    # create a part time employee
    @staticmethod
    def create_part_time_employee(
        employee_id: str,
        name: str,
        department: str,
        job_title: str,
        hourly_rate: float,
        hours_worked: float = 0,
        work_mode: WorkMode = WorkMode.ONSITE,
        remote_data: dict | None = None,
    ) -> PartTimeEmployee:

        emp = PartTimeEmployee(
            employee_id,
            name,
            department,
            job_title,
            hourly_rate,
            hours_worked,
            work_mode,
        )
        if isinstance(remote_data, dict) and remote_data:
            profile = RemoteWorkProfile(**remote_data)
            emp.attach_remote_profile(profile)
        EmployeeOperations.add(emp)
        return emp

    #############################
    # get employee Data by ID
    @staticmethod
    def get_employee(employee_id: str) -> Employee:

        return EmployeeOperations.get(employee_id)

    #############################
    # get all employee Data
    @staticmethod
    def get_all_employee() -> list[Employee]:

        return EmployeeOperations.get_all()

    #############################
    # update employee Data by ID
    @staticmethod
    def update_employee(employee_id: str, **data) -> None:
        EmployeeOperations.update(employee_id, **data)

    @staticmethod
    def terminate_employee(employee_id: str) -> None:
        EmployeeOperations.get(employee_id).terminate()

    @staticmethod
    def delete_employee(employee_id: str) -> None:
        EmployeeOperations.delete(employee_id)

    ####################
    # search employee by name
    @staticmethod
    def search_employee(keyword: str) -> list[Employee]:
        return EmployeeOperations.search(keyword)

    @staticmethod
    def filter_employees(
        department: str | None = None,
        status: str | None = None,
        work_mode: WorkMode | None = None,
        job_title: str | None = None,
    ) -> list[Employee]:
        return EmployeeOperations.filter_by(
            department=department,
            status=status,
            work_mode=work_mode,
            job_title=job_title,
        )

    ##################
    # Generate the final salary
    @staticmethod
    def generate_payment(employee_id: str) -> dict:
        emp = EmployeeOperations.get(employee_id)
        gross = emp.calculate_gross_pay()
        tax = TaxCalculator.calculate_tax(gross)
        net_pay = TaxCalculator.calculate_net_pay(gross)
        return {
            "employee_id": employee_id,
            "name": emp.name,
            "gross_pay": gross,
            "tax": tax,
            "net_pay": net_pay,
        }
