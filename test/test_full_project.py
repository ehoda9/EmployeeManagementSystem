import os
import sys
import unittest
from datetime import date

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.employee import Employee
from backend.employee_operations import EmployeeOperations
from backend.enums import EmployeeStatus, EmploymentType, WorkMode
from backend.exceptions import (
    DuplicateEmployeeId,
    EmployeeNotFound,
    InvalidEmployeeData,
    InvalidStateTransition,
)
from backend.full_time_employee import FullTimeEmployee
from backend.part_time_employee import PartTimeEmployee
from backend.remote_work_profile import RemoteWorkProfile
from backend.tax_calculator import TaxCalculator
from employee_manager import EmployeeManager


# ======================================================================
class TestEnums(unittest.TestCase):
    def test_employment_type_members(self):
        self.assertEqual(EmploymentType.FULL_TIME.value, "Full-Time")
        self.assertEqual(EmploymentType.PART_TIME.value, "Part-Time")

    def test_work_mode_members(self):
        self.assertEqual(WorkMode.ONSITE.value, "On-Site")
        self.assertEqual(WorkMode.HYBRID.value, "Hybrid")
        self.assertEqual(WorkMode.REMOTE.value, "Remote")

    def test_employee_status_members(self):
        self.assertEqual(EmployeeStatus.ACTIVE.value, "Active")
        self.assertEqual(EmployeeStatus.ON_LEAVE.value, "On Leave")
        self.assertEqual(EmployeeStatus.TERMINATED.value, "Terminated")


# ======================================================================
class TestExceptions(unittest.TestCase):
    def test_all_are_exceptions(self):
        for exc in (
            EmployeeNotFound,
            DuplicateEmployeeId,
            InvalidEmployeeData,
            InvalidStateTransition,
        ):
            self.assertTrue(issubclass(exc, Exception))

    def test_raise_and_catch(self):
        with self.assertRaises(InvalidEmployeeData):
            raise InvalidEmployeeData("x")


# ======================================================================
class TestRemoteWorkProfile(unittest.TestCase):
    def test_valid_creation_and_normalization(self):
        p = RemoteWorkProfile("  cairo  ", 200, 300)
        self.assertEqual(p.location, "Cairo")
        self.assertEqual(p.internet_allowance, 200.0)
        self.assertEqual(p.equipment_allowance, 300.0)

    def test_defaults(self):
        p = RemoteWorkProfile("Cairo")
        self.assertEqual(p.internet_allowance, 0.0)
        self.assertEqual(p.equipment_allowance, 0.0)

    def test_location_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile("   ")

    def test_location_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile(123)

    def test_internet_allowance_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile("Cairo", internet_allowance=-1)

    def test_internet_allowance_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile("Cairo", internet_allowance="200")

    def test_equipment_allowance_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile("Cairo", equipment_allowance=-1)

    def test_equipment_allowance_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            RemoteWorkProfile("Cairo", equipment_allowance="300")

    def test_calculate_allowance(self):
        p = RemoteWorkProfile("Cairo", 200, 300)
        self.assertEqual(p.calculate_allowance(), 500.0)

    def test_change_location(self):
        p = RemoteWorkProfile("Cairo")
        p.change_location("Giza")
        self.assertEqual(p.location, "Giza")

    def test_change_location_empty_raises(self):
        p = RemoteWorkProfile("Cairo")
        with self.assertRaises(InvalidEmployeeData):
            p.change_location("   ")


# ======================================================================
class TestEmployeeAbstract(unittest.TestCase):
    def test_cannot_instantiate_directly(self):
        with self.assertRaises(TypeError):
            Employee("E1", "Ahmed", "IT", "Dev")


# ======================================================================
class TestFullTimeEmployee(unittest.TestCase):
    def make(self, **kw):
        defaults = dict(
            employee_id="e001",
            name="ahmed ali",
            department="it",
            job_title="developer",
            monthly_salary=8000,
            bonus=0,
        )
        defaults.update(kw)
        return FullTimeEmployee(**defaults)

    def test_field_normalization(self):
        e = self.make()
        self.assertEqual(e.employee_id, "E001")
        self.assertEqual(e.name, "Ahmed Ali")
        self.assertEqual(e.department, "It")
        self.assertEqual(e.job_title, "Developer")

    def test_defaults(self):
        e = self.make()
        self.assertEqual(e.work_mode, WorkMode.ONSITE)
        self.assertEqual(e.status, EmployeeStatus.ACTIVE)
        self.assertEqual(e.hire_date, date.today())
        self.assertIsNone(e.remote_profile)
        self.assertEqual(e.bonus, 0.0)

    def test_employee_id_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(employee_id="   ")

    def test_employee_id_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(employee_id=123)

    def test_name_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(name="")

    def test_name_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(name=123)

    def test_department_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(department="")

    def test_job_title_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(job_title="")

    def test_work_mode_wrong_type_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(work_mode="Remote")

    def test_monthly_salary_zero_or_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(monthly_salary=0)
        with self.assertRaises(InvalidEmployeeData):
            self.make(monthly_salary=-500)

    def test_monthly_salary_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(monthly_salary="8000")

    def test_bonus_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(bonus=-1)

    def test_bonus_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(bonus="100")

    def test_calculate_gross_pay_no_remote(self):
        e = self.make(monthly_salary=8000, bonus=500)
        self.assertEqual(e.calculate_gross_pay(), 8500.0)

    def test_employment_type(self):
        self.assertEqual(self.make().employment_type, "Full-Time")

    def test_add_bonus(self):
        e = self.make(bonus=100)
        e.add_bonus(50)
        self.assertEqual(e.bonus, 150.0)

    def test_add_bonus_negative_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.add_bonus(-10)

    def test_add_bonus_non_numeric_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.add_bonus("10")

    def test_apply_raise(self):
        e = self.make(monthly_salary=10000)
        e.apply_raise(10)  # 10%
        self.assertAlmostEqual(e.monthly_salary, 11000.0)

    def test_apply_raise_negative_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.apply_raise(-5)

    def test_apply_raise_non_numeric_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.apply_raise("10")

    def test_attach_remote_profile_rejects_onsite(self):
        e = self.make(work_mode=WorkMode.ONSITE)
        p = RemoteWorkProfile("Cairo", 200, 300)
        with self.assertRaises(InvalidEmployeeData):
            e.attach_remote_profile(p)

    def test_attach_remote_profile_rejects_non_profile(self):
        e = self.make(work_mode=WorkMode.REMOTE)
        with self.assertRaises(InvalidEmployeeData):
            e.attach_remote_profile("not a profile")

    def test_attach_remote_profile_success_and_gross_pay(self):
        e = self.make(work_mode=WorkMode.REMOTE, monthly_salary=8000, bonus=500)
        p = RemoteWorkProfile("Cairo", 200, 300)
        e.attach_remote_profile(p)
        self.assertIs(e.remote_profile, p)
        self.assertEqual(e.calculate_gross_pay(), 9000.0)

    def test_lifecycle_transitions_valid(self):
        e = self.make()
        e.put_on_leave()
        self.assertEqual(e.status, EmployeeStatus.ON_LEAVE)
        e.return_from_leave()
        self.assertEqual(e.status, EmployeeStatus.ACTIVE)
        e.terminate()
        self.assertEqual(e.status, EmployeeStatus.TERMINATED)

    def test_put_on_leave_twice_raises(self):
        e = self.make()
        e.put_on_leave()
        with self.assertRaises(InvalidStateTransition):
            e.put_on_leave()

    def test_return_from_leave_when_not_on_leave_raises(self):
        e = self.make()
        with self.assertRaises(InvalidStateTransition):
            e.return_from_leave()

    def test_terminate_twice_raises(self):
        e = self.make()
        e.terminate()
        with self.assertRaises(InvalidStateTransition):
            e.terminate()

    def test_get_details_shape_no_remote(self):
        e = self.make(monthly_salary=8000, bonus=500)
        d = e.get_details()
        self.assertEqual(d["id"], "E001")
        self.assertIsNone(d["remote_location"])
        self.assertEqual(d["remote_allowance"], 0.0)
        self.assertEqual(d["monthly_salary"], 8000.0)
        self.assertEqual(d["bonus"], 500.0)
        self.assertEqual(d["total_salary"], 8500.0)

    def test_get_details_shape_with_remote(self):
        e = self.make(work_mode=WorkMode.REMOTE)
        e.attach_remote_profile(RemoteWorkProfile("Cairo", 200, 300))
        d = e.get_details()
        self.assertEqual(d["remote_location"], "Cairo")
        self.assertEqual(d["remote_allowance"], 500.0)

    def test_str_does_not_crash(self):
        e = self.make()
        s = str(e)
        self.assertIn("E001", s)
        self.assertIn("Full-Time" if False else "8000.00", s)  # monthly salary present


# ======================================================================
class TestPartTimeEmployee(unittest.TestCase):
    def make(self, **kw):
        defaults = dict(
            employee_id="e900",
            name="sara mostafa",
            department="hr",
            job_title="manager",
            hourly_rate=50,
            hours_worked=0,
        )
        defaults.update(kw)
        return PartTimeEmployee(**defaults)

    def test_defaults(self):
        e = self.make()
        self.assertEqual(e.hours_worked, 0.0)
        self.assertEqual(e.work_mode, WorkMode.ONSITE)

    def test_hourly_rate_zero_or_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(hourly_rate=0)
        with self.assertRaises(InvalidEmployeeData):
            self.make(hourly_rate=-10)

    def test_hourly_rate_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(hourly_rate="50")

    def test_hours_worked_negative_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(hours_worked=-1)

    def test_hours_worked_non_numeric_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            self.make(hours_worked="10")

    def test_calculate_gross_pay_no_remote(self):
        e = self.make(hourly_rate=50, hours_worked=80)
        self.assertEqual(e.calculate_gross_pay(), 4000.0)

    def test_calculate_gross_pay_with_remote(self):
        e = self.make(hourly_rate=50, hours_worked=80, work_mode=WorkMode.REMOTE)
        e.attach_remote_profile(RemoteWorkProfile("Cairo", 100, 150))
        self.assertEqual(e.calculate_gross_pay(), 4250.0)

    def test_employment_type(self):
        self.assertEqual(self.make().employment_type, "Part-Time")

    def test_update_hours(self):
        e = self.make(hours_worked=10)
        e.update_hours(40)
        self.assertEqual(e.hours_worked, 40.0)

    def test_update_hours_negative_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.update_hours(-5)

    def test_update_rate(self):
        e = self.make(hourly_rate=50)
        e.update_rate(75)
        self.assertEqual(e.hourly_rate, 75.0)

    def test_update_rate_negative_raises(self):
        e = self.make()
        with self.assertRaises(InvalidEmployeeData):
            e.update_rate(-5)

    def test_get_details_shape(self):
        e = self.make(hourly_rate=50, hours_worked=80)
        d = e.get_details()
        self.assertEqual(d["hourly_rate"], 50.0)
        self.assertEqual(d["hours_worked"], 80.0)
        self.assertEqual(d["total_salary"], 4000.0)


# ======================================================================
class TestTaxCalculator(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(TaxCalculator.calculate_tax(0), 0.0)

    def test_boundary_5000(self):
        self.assertEqual(TaxCalculator.calculate_tax(5000), 0.0)

    def test_just_above_5000(self):
        self.assertAlmostEqual(TaxCalculator.calculate_tax(5000.01), 500.001)

    def test_boundary_15000(self):
        self.assertAlmostEqual(TaxCalculator.calculate_tax(15000), 1500.0)

    def test_just_above_15000(self):
        self.assertAlmostEqual(TaxCalculator.calculate_tax(15000.01), 2250.0015)

    def test_high_value(self):
        self.assertAlmostEqual(TaxCalculator.calculate_tax(20000), 3000.0)

    def test_net_pay(self):
        self.assertAlmostEqual(TaxCalculator.calculate_net_pay(9000), 8100.0)
        self.assertAlmostEqual(TaxCalculator.calculate_net_pay(4000), 4000.0)


# ======================================================================
class TestEmployeeOperations(unittest.TestCase):
    def setUp(self):
        EmployeeOperations._employees.clear()

    def _emp(self, eid="E1", **kw):
        defaults = dict(
            employee_id=eid,
            name="Ahmed",
            department="IT",
            job_title="Dev",
            monthly_salary=8000,
        )
        defaults.update(kw)
        return FullTimeEmployee(**defaults)

    def test_add_and_get(self):
        e = self._emp()
        EmployeeOperations.add(e)
        self.assertIs(EmployeeOperations.get("e1"), e)  # lower-case id should normalize

    def test_add_non_employee_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.add("not an employee")

    def test_add_duplicate_raises(self):
        EmployeeOperations.add(self._emp("E1"))
        with self.assertRaises(DuplicateEmployeeId):
            EmployeeOperations.add(self._emp("E1"))

    def test_get_missing_raises(self):
        with self.assertRaises(EmployeeNotFound):
            EmployeeOperations.get("NOPE")

    def test_get_empty_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.get("   ")

    def test_get_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.get(123)

    def test_get_all_empty(self):
        self.assertEqual(EmployeeOperations.get_all(), [])

    def test_get_all_populated(self):
        EmployeeOperations.add(self._emp("E1"))
        EmployeeOperations.add(self._emp("E2"))
        self.assertEqual(len(EmployeeOperations.get_all()), 2)

    def test_update_valid_field(self):
        EmployeeOperations.add(self._emp("E1"))
        EmployeeOperations.update("E1", name="Mahmoud")
        self.assertEqual(EmployeeOperations.get("E1").name, "Mahmoud")

    def test_update_positional_guard_raises(self):
        EmployeeOperations.add(self._emp("E1"))
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.update("E1", "some_positional_value")

    def test_update_no_kwargs_raises(self):
        EmployeeOperations.add(self._emp("E1"))
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.update("E1")

    def test_update_nonexistent_property_raises(self):
        EmployeeOperations.add(self._emp("E1"))
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.update("E1", salery=9000)

    def test_update_getter_only_property_raises(self):
        EmployeeOperations.add(self._emp("E1"))
        # 'status' has a getter but no setter on Employee -> update() must reject it
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.update("E1", status=EmployeeStatus.ON_LEAVE)

    def test_update_missing_employee_raises(self):
        with self.assertRaises(EmployeeNotFound):
            EmployeeOperations.update("NOPE", name="X")

    def test_delete(self):
        EmployeeOperations.add(self._emp("E1"))
        EmployeeOperations.delete("E1")
        with self.assertRaises(EmployeeNotFound):
            EmployeeOperations.get("E1")

    def test_delete_missing_raises(self):
        with self.assertRaises(EmployeeNotFound):
            EmployeeOperations.delete("NOPE")

    def test_exists(self):
        EmployeeOperations.add(self._emp("E1"))
        self.assertTrue(EmployeeOperations.exists("E1"))
        self.assertFalse(EmployeeOperations.exists("E2"))

    def test_exists_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.exists(123)

    def test_search_empty_keyword_returns_all_sorted_by_name(self):
        EmployeeOperations.add(self._emp("E1", name="Zaid"))
        EmployeeOperations.add(self._emp("E2", name="Ahmed"))
        result = EmployeeOperations.search("")
        self.assertEqual([e.name for e in result], ["Ahmed", "Zaid"])

    def test_search_matches_name_department_jobtitle(self):
        EmployeeOperations.add(
            self._emp(
                "E1", name="Ahmed", department="Data Science", job_title="AI Engineer"
            )
        )
        EmployeeOperations.add(
            self._emp("E2", name="Sara", department="HR", job_title="Manager")
        )
        result = EmployeeOperations.search("data")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, "E1")

    def test_search_relevance_ordering(self):
        EmployeeOperations.add(
            self._emp(
                "E1", name="Mahmoud", department="Marketing", job_title="Specialist"
            )
        )
        EmployeeOperations.add(
            self._emp("E2", name="Ahmed Mahmoud", department="IT", job_title="Dev")
        )
        result = EmployeeOperations.search("mahmoud")
        # E1's name STARTS WITH "mahmoud" -> should rank first
        self.assertEqual(result[0].employee_id, "E1")

    def test_search_non_str_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.search(123)

    def test_filter_by_department(self):
        EmployeeOperations.add(self._emp("E1", department="IT"))
        EmployeeOperations.add(self._emp("E2", department="HR"))
        result = EmployeeOperations.filter_by(department="it")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, "E1")

    def test_filter_by_status_enum_unwrap(self):
        e1 = self._emp("E1")
        e1.put_on_leave()
        EmployeeOperations.add(e1)
        EmployeeOperations.add(self._emp("E2"))
        result = EmployeeOperations.filter_by(status="on leave")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, "E1")

    def test_filter_by_work_mode_enum_unwrap(self):
        e1 = self._emp("E1", work_mode=WorkMode.REMOTE)
        EmployeeOperations.add(e1)
        EmployeeOperations.add(self._emp("E2", work_mode=WorkMode.ONSITE))
        result = EmployeeOperations.filter_by(work_mode="remote")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, "E1")

    def test_filter_by_positional_guard_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.filter_by("IT")

    def test_filter_by_non_str_value_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.filter_by(department=123)

    def test_filter_by_empty_string_value_raises(self):
        with self.assertRaises(InvalidEmployeeData):
            EmployeeOperations.filter_by(department="   ")

    def test_filter_by_no_filters_returns_all(self):
        EmployeeOperations.add(self._emp("E1"))
        EmployeeOperations.add(self._emp("E2"))
        self.assertEqual(len(EmployeeOperations.filter_by()), 2)

    def test_len_and_str(self):
        EmployeeOperations.add(self._emp("E1"))
        EmployeeOperations.add(self._emp("E2"))
        self.assertEqual(len(EmployeeOperations), 2)
        s = str(EmployeeOperations)
        self.assertIn("E1", s)
        self.assertIn("E2", s)


# ======================================================================
class TestEmployeeManager(unittest.TestCase):
    def setUp(self):
        EmployeeOperations._employees.clear()

    def test_create_full_time_stores_in_operations(self):
        emp = EmployeeManager.create_full_time_employee(
            "E1", "Ahmed", "IT", "Dev", 8000
        )
        self.assertTrue(EmployeeOperations.exists("E1"))
        self.assertIsInstance(emp, FullTimeEmployee)

    def test_create_full_time_with_remote_data(self):
        emp = EmployeeManager.create_full_time_employee(
            "E1",
            "Ahmed",
            "IT",
            "Dev",
            8000,
            work_mode=WorkMode.REMOTE,
            remote_data={
                "location": "Cairo",
                "internet_allowance": 200,
                "equipment_allowance": 300,
            },
        )
        self.assertIsNotNone(emp.remote_profile)
        self.assertEqual(emp.calculate_gross_pay(), 8500.0)

    def test_create_full_time_with_empty_remote_data_dict(self):
        emp = EmployeeManager.create_full_time_employee(
            "E1", "Ahmed", "IT", "Dev", 8000, remote_data={}
        )
        self.assertIsNone(emp.remote_profile)
        self.assertTrue(EmployeeOperations.exists("E1"))

    def test_create_part_time_stores_in_operations(self):
        emp = EmployeeManager.create_part_time_employee(
            "E2", "Sara", "HR", "Manager", 50, 80
        )
        self.assertTrue(EmployeeOperations.exists("E2"))
        self.assertEqual(emp.calculate_gross_pay(), 4000.0)

    def test_get_employee_and_get_all(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.create_part_time_employee("E2", "Sara", "HR", "Manager", 50, 80)
        self.assertEqual(EmployeeManager.get_employee("E1").name, "Ahmed")
        self.assertEqual(len(EmployeeManager.get_all_employee()), 2)

    def test_update_employee_kwargs_unpacking(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.update_employee("E1", name="Mahmoud")
        self.assertEqual(EmployeeManager.get_employee("E1").name, "Mahmoud")

    def test_terminate_employee(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.terminate_employee("E1")
        self.assertEqual(
            EmployeeManager.get_employee("E1").status, EmployeeStatus.TERMINATED
        )

    def test_delete_employee(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.delete_employee("E1")
        self.assertFalse(EmployeeOperations.exists("E1"))

    def test_search_employee(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.create_full_time_employee("E2", "Sara", "HR", "Manager", 9000)
        result = EmployeeManager.search_employee("ahmed")
        self.assertEqual(len(result), 1)

    def test_filter_employees(self):
        EmployeeManager.create_full_time_employee("E1", "Ahmed", "IT", "Dev", 8000)
        EmployeeManager.create_full_time_employee("E2", "Sara", "HR", "Manager", 9000)
        result = EmployeeManager.filter_employees(department="IT")
        self.assertEqual(len(result), 1)

    def test_generate_payment_full_time(self):
        EmployeeManager.create_full_time_employee(
            "E1", "Ahmed", "IT", "Dev", 8000, bonus=500
        )
        payslip = EmployeeManager.generate_payment("E1")
        self.assertEqual(payslip["gross_pay"], 8500.0)
        self.assertAlmostEqual(payslip["tax"], 850.0)
        self.assertAlmostEqual(payslip["net_pay"], 7650.0)

    def test_generate_payment_part_time_low_income_zero_tax(self):
        EmployeeManager.create_part_time_employee("E2", "Sara", "HR", "Manager", 50, 80)
        payslip = EmployeeManager.generate_payment("E2")
        self.assertEqual(payslip["gross_pay"], 4000.0)
        self.assertEqual(payslip["tax"], 0.0)
        self.assertEqual(payslip["net_pay"], 4000.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
