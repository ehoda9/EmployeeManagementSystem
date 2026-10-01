from backend.employee import Employee
from backend.enums import EmployeeStatus, WorkMode
from backend.exceptions import (
    DuplicateEmployeeId,
    EmployeeNotFound,
    InvalidEmployeeData,
)


# Metaclass
class EMC(type):
    """
    - just inject the [dict] inside
    \n- the class itself before it builded in memory
    \n- so the our dic storage [_employees] now part of the class itself
    \n- not created after the class !
    \n- without needed to create new object
    """

    _employees: dict[str, Employee]

    def __new__(mcs, name, bases, attrs):
        attrs["_employees"] = {}
        return super().__new__(mcs, name, bases, attrs)

    def __len__(self) -> int:
        return len(self._employees)

    # for testing show data beautiful in terminal
    def __str__(self) -> str:
        top = "- Quick HouDa Testing Lookup  -\n"
        header = f"-{'ID':^13} | {'Name':^13}\n"
        separator = "-" * len(header) + "\n"

        msg = separator + top + separator + header + separator

        if not self._employees:
            return "Employee Storage is empty."

        sorted_dict = sorted(self._employees.values(), key=lambda e: e.employee_id)
        for emp in sorted_dict:
            msg += f"- {emp.employee_id:^12} | {emp.name:^13}-\n"
        return msg + separator


class EmployeeOperations(metaclass=EMC):
    """
    [![Clickable image](https://avatars.githubusercontent.com/u/102419319?v=4&s=80)](https://github.com/ehoda9)

    ## MetaClass is `EMC` for this class

    > The MetaClass init this class with built-in modified methods:
    * Like `len(EmployeeOperations)` => returns count of `_employee` dict
    * Like `__str__` to print direct organized data `print(EmployeeOperations)`
    * Injects `_employees` dict inside the Class itself as part of class `while it is created in memory`

    - [x] This class is for all operations for Employees
    * Employee Operations are:
      - `add`, `get`, `get_all`, `update`, `delete`, `exists`, `search`, `filter_by`
    """

    # add new employee object to the storage [dict]
    @classmethod
    def add(cls, employee: Employee) -> None:

        if not isinstance(employee, Employee):
            raise InvalidEmployeeData(
                "This is not Correct Employee object !! try type(obj)"
            )

        if employee.employee_id in cls._employees:
            raise DuplicateEmployeeId(employee.employee_id)
        cls._employees[employee.employee_id] = employee

    # get employee by ID
    @classmethod
    def get(cls, employee_id: str) -> Employee:
        """
         > Get employee instance by ID
        * Args:
            - employee_id (str)
        * Returns:
            - Employee: as object
        """
        if not isinstance(employee_id, str):
            raise InvalidEmployeeData("Employee ID is not string value!!")

        eid = employee_id.strip().upper()
        if not employee_id or not eid:
            raise InvalidEmployeeData("Employee ID can't be empty!!")

        if eid not in cls._employees:
            raise EmployeeNotFound(eid)
        return cls._employees[eid]

    # print a list that contain Employees

    @classmethod
    def get_all(cls) -> list[Employee]:
        """This function get all employees that created in `List` and return `empty list` if no employees
        \n * `bool(get_all)`
        \n  - `TRUE` = `found employees` and `FALSE` = `list is empty`"""
        return list(cls._employees.values())

    @classmethod
    def update(cls, employee_id: str, *guard, **args) -> None:
        """
        #### Update employee properties dynamically with automatic validation[`key.SETTER`] :)

        * Available Keys by Employee Type:
            1. Common Keys (All Employees):
                `- name (str)`
                `- department (str)`
                -` job_title (str)`

            2. FullTimeEmployee Keys:
                - `monthly_salary (int | float)`
                - `bonus (int | float)`

            3. PartTimeEmployee Keys:
                - `hourly_rate (int | float)`
                - `hours_worked (int | float)`

        * Usage Example:
            >>> EmployeeOperations.update("E001", name="Mahmoud Mohamed")
            \n
            >>> EmployeeOperations.update("E002", hourly_rate=100)
        """
        if guard:
            raise InvalidEmployeeData(
                "You must provide updates as key='value' (example [name='Mahmoud']"
            )
        emp = cls.get(employee_id)
        if not args:
            raise InvalidEmployeeData(
                "add at least one attribute to modify! example : name='mahmoud'"
            )

        remote_keys = {"location", "internet_allowance", "equipment_allowance"}

        for key, value in args.items():
            if key in remote_keys:
                if emp.remote_profile is None:
                    raise InvalidEmployeeData(
                        f"Cannot update '{key}'. This employee does not have a Remote Work Profile!"
                    )
                target = emp.remote_profile
            else:
                target = emp

            my_property = getattr(type(target), key, None)

            if not isinstance(my_property, property):
                raise InvalidEmployeeData(
                    f"'{key}' is not an property on {type(target).__name__}, check [ help(EmployeeOperations.update) ]"
                )
                # check if this property has SETTER
            if my_property.fset is None:
                raise InvalidEmployeeData(
                    f"'{key}' property has not set attribute in {type(target).__name__}, check [ help(EmployeeOperations.update) ]"
                )
            setattr(target, key, value)

    @classmethod
    def delete(cls, employee_id: str) -> None:
        """Delete employee by id this function take `string` argument[`"employee_id"`], but return `None`"""
        del cls._employees[cls.get(employee_id).employee_id]

    @classmethod
    def exists(cls, employee_id: str) -> bool:

        if not isinstance(employee_id, str):
            raise InvalidEmployeeData("Employee ID is not string value!!")

        if not employee_id or not (eid := employee_id.strip().upper()):
            raise InvalidEmployeeData("Employee ID can't be empty!")

        return eid in cls._employees

    @classmethod
    def search(cls, keyword: str) -> list[Employee]:
        if not isinstance(keyword, str):
            raise InvalidEmployeeData(
                f"Error: Search Keyword should be string not [{type(keyword).__name__}]"
            )
        if not keyword or not keyword.strip():
            return sorted(cls._employees.values(), key=lambda e: e.name.lower())
        key = keyword.lower().strip()

        # sorting logic algorithm :D
        # if true,false => 0,1
        # if 2 values have same value go compare next one (0,mona,department,job_title) = (0,mahmoud,department,job_title)
        logic = lambda x: (
            not (
                x.name.lower().startswith(key)
                or x.department.lower().startswith(key)
                or x.job_title.lower().startswith(key)
            ),
            x.name.lower(),
            x.department.lower(),
            x.job_title.lower(),
        )
        return sorted(
            [
                emp
                for emp in cls._employees.values()
                if key in emp.name.lower()
                or key in emp.department.lower()
                or key in emp.job_title.lower()
            ],
            key=logic,
        )

    @classmethod
    def filter_by(
        cls, *guard, department=None, status=None, work_mode=None, job_title=None
    ) -> list[Employee]:
        if guard:
            raise InvalidEmployeeData(
                "Error:\nArguments should be Key=Value Format example:\n(department='HR',status='On Site',work_mode='Hybrid',job_title='Senior AI Engineer')"
            )

        # no spaghetti :D conditions
        user_preference = {
            "department": department,
            "status": status,
            "work_mode": work_mode,
            "job_title": job_title,
        }

        for key, value in user_preference.items():
            if value is not None:
                if key in {"status", "work_mode"} and not isinstance(
                    value, (str, EmployeeStatus, WorkMode)
                ):
                    raise InvalidEmployeeData(
                        f"'{key}' should be a string or Enum type for [status,work_mode]!"
                    )
                elif key in {"department", "job_title"} and not isinstance(value, str):
                    raise InvalidEmployeeData(f"'{key}' should be a string value!")

            if value is not None and isinstance(value, str) and not value.strip():
                raise InvalidEmployeeData(f"'{key}' can't be empty")

        activated_filters = {}
        for key, value in user_preference.items():
            if value is not None:
                if hasattr(value, "value"):  # enum element
                    activated_filters[key] = value.value.lower().strip()
                else:  # element is normal string :D
                    activated_filters[key] = value.lower().strip()

        # print(bool(getattr(next(iter(cls._employees.values())), "hr", None)))
        # print(activated_filters, "\n")

        def check_filters(emp, key):
            attribute_key = getattr(emp, key, None)
            if attribute_key is None:
                return None

            attribute_key = (
                attribute_key.value
                if hasattr(attribute_key, "value")  # because Enum use value
                else attribute_key
            )
            return attribute_key.lower().strip()

        return [
            emp
            for emp in cls._employees.values()
            if all(
                check_filters(emp, key) == value
                for key, value in activated_filters.items()
            )
        ]
