from backend.exceptions import InvalidEmployeeData


class RemoteWorkProfile:
    def __init__(
        self,
        location: str,
        internet_allowance: float = 0,
        equipment_allowance: float = 0,
    ):
        self.location = location
        self.internet_allowance = internet_allowance
        self.equipment_allowance = equipment_allowance

    # location encapsulation
    @property
    def location(self) -> str:
        return self.__location

    @location.setter
    def location(self, value: str) -> None:

        if not isinstance(value, str):
            raise InvalidEmployeeData(
                f"Location should be string, not {type(value).__name__}"
            )

        if not value or not value.strip():
            raise InvalidEmployeeData("Location should not be empty!!")
        self.__location = value.strip().title()

    # internet allowance encapsulation
    @property
    def internet_allowance(self) -> float:
        return self.__internet_allowance

    @internet_allowance.setter
    def internet_allowance(self, value: float) -> None:

        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"internet allowance should be Float or integer, not {type(value).__name__}"
            )

        if value < 0:
            raise InvalidEmployeeData("internet allowance should not be negative ")
        self.__internet_allowance = float(value)

    # equipment allowance encapsulation
    @property
    def equipment_allowance(self):
        return self.__equipment_allowance

    @equipment_allowance.setter
    def equipment_allowance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise InvalidEmployeeData(
                f"equipment allowance should be Float or integer, not {type(value).__name__}"
            )

        if value < 0:
            raise InvalidEmployeeData("equipment allowance should not be negative ")
        self.__equipment_allowance = float(value)

    # Instance methods
    def calculate_allowance(self) -> float:
        """This function return allowance for remote employees
        before added to the gross pay and return float value"""
        return self.__internet_allowance + self.__equipment_allowance

    def change_location(self, value: str) -> None:
        """Change from where the employee work from"""
        self.location = value
