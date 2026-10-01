import re
from tkinter import messagebox
from typing import Any, cast

import customtkinter as ctk

from backend.exceptions import EmployeeError
from employee_manager import EmployeeManager


def Theme(name):
    return ctk.ThemeManager.theme["Houda"][name]


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


class UpdateEmployee(ctk.CTkToplevel):
    def __init__(self, parent, emp_id: str, callback):
        super().__init__(parent)
        self.refresh = callback
        self.emp_id = emp_id

        try:
            self.employee = EmployeeManager.get_employee(emp_id)
        except EmployeeError as e:
            messagebox.showerror(
                "Error", f"Could not load employee: {e}", parent=parent
            )
            self.destroy()
            return

        self.width = 520
        self.height = 480
        self.title("Update Employee")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width // 2) - (self.width // 2))
        y = int((screen_height // 2) - (self.height // 2))
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.transient(parent)

        self.active_border_color = Theme("accent")
        self.normal_border_color = Theme("border")
        self.error_border_color = Theme("danger")

        self.vcmd_alphanumeric = (
            self.register(self._validate_alphanumeric_input),
            "%P",
        )

        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            border_width=5,
            border_color=Theme("border"),
            fg_color=Theme("surface"),
        )
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text="Update Employee",
            font=(GetFontFamily(), 18, "bold"),
            text_color=Theme("text"),
        ).pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container, fg_color="transparent"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

        self.widgets = self._build_form(self.scroll_frame)

        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

        ctk.CTkButton(
            footer_frame,
            text="Cancel",
            fg_color="transparent",
            hover_color=Theme("hover"),
            text_color=Theme("text"),
            width=80,
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            footer_frame,
            text="Save Changes",
            font=(GetFontFamily(), 12, "bold"),
            fg_color=Theme("accent"),
            hover_color=Theme("accent_hover"),
            text_color=Theme("accent_ink"),
            width=130,
            command=self.validate_and_submit,
        ).pack(side="right")

        self._populate_data()

    def _build_form(self, parent):
        widgets = {}

        widgets["emp_id"] = self._create_input_field(
            parent,
            "Employee ID",
            prefix_text="E",
            strict_alphanumeric=True,
        )
        widgets["emp_id"]["entry"].configure(state="disabled")

        widgets["name"] = self._create_input_field(
            parent,
            "Full Name *",
            placeholder="e.g. Mahmoud Mohamed",
            strict_alphanumeric=True,
        )

        row_dept_job = ctk.CTkFrame(parent, fg_color="transparent")
        row_dept_job.pack(fill="x", pady=5)
        row_dept_job.columnconfigure((0, 1), weight=1, uniform="sub_group")

        widgets["dept"] = self._create_input_field(
            row_dept_job,
            "Department *",
            placeholder="e.g. IT",
            grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
            strict_alphanumeric=True,
        )
        widgets["job_title"] = self._create_input_field(
            row_dept_job,
            "Job Title *",
            placeholder="e.g. Software Engineer",
            grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
            strict_alphanumeric=True,
        )

        row_financial = ctk.CTkFrame(parent, fg_color="transparent")
        row_financial.pack(fill="x", pady=5)
        row_financial.columnconfigure((0, 1), weight=1, uniform="sub_group")

        widgets["salary"] = self._create_input_field(
            row_financial,
            "Monthly Salary *",
            placeholder="0.00",
            grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
        )
        widgets["bonus"] = self._create_input_field(
            row_financial,
            "Bonus",
            placeholder="0.00",
            default_val="0",
            grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
        )

        widgets["hourly_rate"] = self._create_input_field(
            row_financial,
            "Hourly Rate *",
            placeholder="0.00",
            grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
        )
        widgets["hours_worked"] = self._create_input_field(
            row_financial,
            "Hours Worked",
            placeholder="0",
            default_val="0",
            grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
        )

        return widgets

    def _populate_data(self):
        emp = self.employee
        w = self.widgets

        raw_id = emp.employee_id.lstrip("E")
        w["emp_id"]["entry"].configure(state="normal")
        w["emp_id"]["entry"].insert(0, raw_id)
        w["emp_id"]["entry"].configure(state="disabled")

        w["name"]["entry"].insert(0, emp.name)
        w["dept"]["entry"].insert(0, emp.department)
        w["job_title"]["entry"].insert(0, emp.job_title)

        self.is_full_time = hasattr(emp, "monthly_salary")

        if self.is_full_time:
            w["salary"]["entry"].insert(0, str(getattr(emp, "monthly_salary", 0)))
            w["bonus"]["entry"].insert(0, str(getattr(emp, "bonus", 0)))
            w["hourly_rate"]["container"].grid_remove()
            w["hours_worked"]["container"].grid_remove()
        else:
            w["hourly_rate"]["entry"].insert(0, str(getattr(emp, "hourly_rate", 0)))
            w["hours_worked"]["entry"].insert(0, str(getattr(emp, "hours_worked", 0)))
            w["salary"]["container"].grid_remove()
            w["bonus"]["container"].grid_remove()

    def _create_input_field(
        self,
        parent,
        label_text,
        placeholder="",
        default_val="",
        grid_args=None,
        prefix_text=None,
        strict_alphanumeric=False,
    ):
        container = ctk.CTkFrame(parent, fg_color="transparent")

        if grid_args:
            container.grid(**grid_args)
        else:
            container.pack(fill="x", pady=3)

        container.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text=label_text,
            font=(GetFontFamily(), 12),
            text_color=Theme("text"),
        ).grid(row=0, column=0, sticky="w", pady=(2, 2))

        entry_parent = container
        if prefix_text:
            entry_parent = ctk.CTkFrame(container, fg_color="transparent")
            entry_parent.grid(row=1, column=0, sticky="ew")
            entry_parent.columnconfigure(1, weight=1)

            ctk.CTkLabel(
                entry_parent,
                text=prefix_text,
                font=(GetFontFamily(), 13, "bold"),
                text_color=Theme("muted"),
                fg_color=Theme("raised"),
                corner_radius=6,
                width=35,
                height=28,
            ).grid(row=0, column=0, padx=(0, 5), sticky="w")

        entry_kwargs: dict[str, Any] = {"placeholder_text": placeholder}
        if strict_alphanumeric:
            entry_kwargs["validate"] = "key"
            entry_kwargs["validatecommand"] = cast(Any, self.vcmd_alphanumeric)

        entry = ctk.CTkEntry(entry_parent, **entry_kwargs)
        if default_val:
            entry.insert(0, default_val)

        if prefix_text:
            entry.grid(row=0, column=1, sticky="ew")
        else:
            entry.grid(row=1, column=0, sticky="ew")

        err_lbl = ctk.CTkLabel(
            container,
            text="",
            text_color=Theme("danger"),
            font=(GetFontFamily(), 10),
        )

        entry.bind("<FocusIn>", lambda e: self._on_focus_in(entry, err_lbl))
        entry.bind("<FocusOut>", lambda e: self._on_focus_out(entry, err_lbl))

        return {"container": container, "entry": entry, "err_lbl": err_lbl}

    def _validate_alphanumeric_input(self, text_after_change):
        if text_after_change == "":
            return True
        return bool(re.match(r"^[a-zA-Z0-9\u0600-\u06FF\s]*$", text_after_change))

    def _on_focus_in(self, entry, err_lbl):
        if not err_lbl.winfo_ismapped():
            entry.configure(border_color=self.active_border_color)

    def _on_focus_out(self, entry, err_lbl):
        if not err_lbl.winfo_ismapped():
            entry.configure(border_color=self.normal_border_color)

    def _clear_validation_errors(self):
        for w in self.widgets.values():
            if isinstance(w, dict) and "entry" in w:
                w["entry"].configure(border_color=self.normal_border_color)
                w["err_lbl"].grid_forget()

    def _set_field_error(self, field_dict, message):
        field_dict["entry"].configure(border_color=self.error_border_color)
        field_dict["err_lbl"].configure(text=message)
        field_dict["err_lbl"].grid(row=2, column=0, sticky="w", pady=(1, 0))

    def validate_and_submit(self):
        self._clear_validation_errors()
        has_error = False
        w = self.widgets

        for field_key in ["name", "dept", "job_title"]:
            if not w[field_key]["entry"].get().strip():
                self._set_field_error(w[field_key], "This field is required *")
                has_error = True

        numeric_fields = []
        if self.is_full_time:
            numeric_fields.extend([("salary", True), ("bonus", False)])
        else:
            numeric_fields.extend([("hourly_rate", True), ("hours_worked", False)])

        for field_key, is_req in numeric_fields:
            raw_val = w[field_key]["entry"].get().strip()
            if not raw_val:
                if is_req:
                    self._set_field_error(w[field_key], "This field is required *")
                    has_error = True
            else:
                try:
                    if float(raw_val) < 0:
                        self._set_field_error(w[field_key], "Must be positive >= 0")
                        has_error = True
                except ValueError:
                    self._set_field_error(w[field_key], "Must be a valid number")
                    has_error = True

        if has_error:
            return

        update_data = {
            "name": w["name"]["entry"].get().strip(),
            "department": w["dept"]["entry"].get().strip(),
            "job_title": w["job_title"]["entry"].get().strip(),
        }

        if self.is_full_time:
            update_data["monthly_salary"] = float(w["salary"]["entry"].get().strip())
            update_data["bonus"] = float(w["bonus"]["entry"].get().strip())
        else:
            update_data["hourly_rate"] = float(w["hourly_rate"]["entry"].get().strip())
            update_data["hours_worked"] = float(
                w["hours_worked"]["entry"].get().strip()
            )

        try:
            EmployeeManager.update_employee(self.employee.employee_id, **update_data)
            messagebox.showinfo(
                "Success", "Employee updated successfully!", parent=self
            )
            self.refresh()
            self.destroy()
        except EmployeeError as e:
            messagebox.showerror(
                "Error", f"Failed to update employee: {e}", parent=self
            )
