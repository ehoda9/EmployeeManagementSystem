class EmployeeError(Exception):
    """Parent class for all exceptions errors for Backend And GUI frontend"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EmployeeNotFound(EmployeeError):
    """Raise Error when employee not found in system"""

    def __init__(self, employee_id: str):
        super().__init__(f"Error: Employee with ID '{employee_id}' was not found")


class DuplicateEmployeeId(EmployeeError):
    """Raise Error when employee [ID] is exists"""

    def __init__(self, employee_id: str):
        super().__init__(f"Error: The employee ID '{employee_id}' already exists")


class InvalidEmployeeData(EmployeeError):
    """Raise Error when trying to add invalid data or Validation"""


class InvalidStateTransition(EmployeeError):
    """Raise Error when trying to transition Employee status to Wrong state"""

    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Error: Cannot transition employee status from '{current_status}' to '{target_status}'"
        )
