import re
from tkinter import messagebox
from typing import Any, cast

import customtkinter as ctk

from backend.enums import EmploymentType, WorkMode
from backend.exceptions import EmployeeError
from employee_manager import EmployeeManager
from frontend.resource import resource_path


def Theme(name):
    return ctk.ThemeManager.theme["Houda"][name]


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


class CreateEmployee(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        self.refresh = callback
        super().__init__(parent)
        self.width = 520
        self.height = 680

        self.title("Add New Employee")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width // 2) - (self.width // 2))
        y = int((screen_height // 2) - (self.height // 2))

        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.iconbitmap(resource_path("frontend/icon/add.ico"))
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

        title_label = ctk.CTkLabel(
            header_frame,
            text="Add New Employee",
            font=(GetFontFamily(), 18, "bold"),
            text_color=Theme("text"),
        )
        title_label.pack(side="left")

        self.tabview = ctk.CTkTabview(
            self.main_container,
            command=self.on_tab_change,
            corner_radius=10,
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

        self.tab_ft_name = EmploymentType.FULL_TIME.value
        self.tab_pt_name = EmploymentType.PART_TIME.value

        self.tab_ft = self.tabview.add(self.tab_ft_name)
        self.tab_pt = self.tabview.add(self.tab_pt_name)

        self.ft_widgets = self.build_form_scrollable(
            self.tab_ft, emp_type=EmploymentType.FULL_TIME
        )
        self.pt_widgets = self.build_form_scrollable(
            self.tab_pt, emp_type=EmploymentType.PART_TIME
        )

        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

        reset_btn = ctk.CTkButton(
            footer_frame,
            text="Reset",
            fg_color="transparent",
            border_width=1,
            border_color=Theme("border"),
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            width=80,
            command=self.reset_current_tab,
        )
        reset_btn.pack(side="left", padx=(0, 10))

        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancel",
            fg_color="transparent",
            hover_color=Theme("hover"),
            text_color=Theme("text"),
            width=80,
            command=self.destroy,
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            footer_frame,
            text="+ Add Employee",
            font=(GetFontFamily(), 12, "bold"),
            fg_color=Theme("accent"),
            hover_color=Theme("accent_hover"),
            text_color=Theme("accent_ink"),
            width=130,
            command=self.validate_and_submit,
        )
        save_btn.pack(side="right")

    def _validate_alphanumeric_input(self, text_after_change):
        if text_after_change == "":
            return True
        pattern = r"^[a-zA-Z0-9\u0600-\u06FF\s]*$"
        return bool(re.match(pattern, text_after_change))

    def _on_focus_in(self, entry_widget, err_lbl):
        if not err_lbl.winfo_ismapped():
            entry_widget.configure(border_color=self.active_border_color)

    def _on_focus_out(self, entry_widget, err_lbl):
        if not err_lbl.winfo_ismapped():
            entry_widget.configure(border_color=self.normal_border_color)

    def build_form_scrollable(self, parent_tab, emp_type: EmploymentType):
        scroll_frame = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        widgets = {}

        widgets["emp_id"] = self.create_input_field(
            scroll_frame,
            "Employee ID *",
            placeholder="001",
            prefix_text="E",
            strict_alphanumeric=True,
        )

        widgets["name"] = self.create_input_field(
            scroll_frame,
            "Full Name *",
            placeholder="e.g. Mahmoud Mohamed",
            strict_alphanumeric=True,
        )

        row_dept_job = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_dept_job.pack(fill="x", pady=5)
        row_dept_job.columnconfigure((0, 1), weight=1, uniform="sub_group")

        widgets["dept"] = self.create_input_field(
            row_dept_job,
            "Department *",
            placeholder="e.g. IT",
            grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
            strict_alphanumeric=True,
        )
        widgets["job_title"] = self.create_input_field(
            row_dept_job,
            "Job Title *",
            placeholder="e.g. Software Engineer",
            grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
            strict_alphanumeric=True,
        )

        row_financial = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_financial.pack(fill="x", pady=5)
        row_financial.columnconfigure((0, 1), weight=1, uniform="sub_group")

        if emp_type == EmploymentType.FULL_TIME:
            widgets["salary"] = self.create_input_field(
                row_financial,
                "Monthly Salary *",
                placeholder="0.00",
                grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
            )
            widgets["bonus"] = self.create_input_field(
                row_financial,
                "Bonus",
                placeholder="0.00",
                default_val="0",
                grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
            )
        else:
            widgets["hourly_rate"] = self.create_input_field(
                row_financial,
                "Hourly Rate *",
                placeholder="0.00",
                grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
            )
            widgets["hours_worked"] = self.create_input_field(
                row_financial,
                "Hours Worked",
                placeholder="0",
                default_val="0",
                grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
            )

        label_mode = ctk.CTkLabel(
            scroll_frame,
            text="Work Mode *",
            font=(GetFontFamily(), 12, "bold"),
            text_color=Theme("text"),
        )
        label_mode.pack(anchor="w", pady=(10, 2))

        widgets["work_mode"] = ctk.CTkOptionMenu(
            scroll_frame,
            values=[mode.value for mode in WorkMode],
            command=lambda val: self.toggle_remote_fields(val, widgets),
        )
        widgets["work_mode"].pack(fill="x", pady=(0, 5))
        widgets["work_mode"].set(WorkMode.ONSITE.value)

        remote_frame = ctk.CTkFrame(
            scroll_frame,
            border_width=1,
            border_color=Theme("border"),
            fg_color=Theme("raised"),
        )
        widgets["remote_frame"] = remote_frame

        remote_title = ctk.CTkLabel(
            remote_frame,
            text="Remote Work Details",
            font=(GetFontFamily(), 12, "bold"),
            text_color=Theme("text"),
        )
        remote_title.pack(anchor="w", padx=10, pady=(10, 5))

        widgets["remote_location"] = self.create_input_field(
            remote_frame,
            "Location *",
            placeholder="e.g. Cairo Egypt",
            in_frame=True,
            strict_alphanumeric=True,
        )

        row_allowances = ctk.CTkFrame(remote_frame, fg_color="transparent")
        row_allowances.pack(fill="x", padx=10, pady=5)
        row_allowances.columnconfigure((0, 1), weight=1, uniform="sub_group2")

        widgets["internet_allowance"] = self.create_input_field(
            row_allowances,
            "Internet Allowance",
            placeholder="0.00",
            default_val="0",
            grid_args={"row": 0, "column": 0, "padx": (0, 5), "sticky": "n"},
            in_frame=True,
        )
        widgets["equipment_allowance"] = self.create_input_field(
            row_allowances,
            "Equipment Allowance",
            placeholder="0.00",
            default_val="0",
            grid_args={"row": 0, "column": 1, "padx": (5, 0), "sticky": "n"},
            in_frame=True,
        )

        return widgets

    def create_input_field(
        self,
        parent,
        label_text,
        placeholder="",
        default_val="",
        grid_args=None,
        in_frame=False,
        prefix_text=None,
        strict_alphanumeric=False,
    ):
        container = ctk.CTkFrame(parent, fg_color="transparent")

        if grid_args:
            container.grid(**grid_args)
        else:
            padding_x = 10 if in_frame else 0
            container.pack(fill="x", pady=3, padx=padding_x)

        container.columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(
            container,
            text=label_text,
            font=(GetFontFamily(), 12),
            text_color=Theme("text"),
        )
        lbl.grid(row=0, column=0, sticky="w", pady=(2, 2))

        entry_parent = container
        if prefix_text:
            entry_parent = ctk.CTkFrame(container, fg_color="transparent")
            entry_parent.grid(row=1, column=0, sticky="ew")
            entry_parent.columnconfigure(1, weight=1)

            prefix_lbl = ctk.CTkLabel(
                entry_parent,
                text=prefix_text,
                font=(GetFontFamily(), 13, "bold"),
                text_color=Theme("muted"),
                fg_color=Theme("raised"),
                corner_radius=6,
                width=35,
                height=28,
            )
            prefix_lbl.grid(row=0, column=0, padx=(0, 5), sticky="w")

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

        entry.bind(
            "<FocusIn>",
            lambda e, widget=entry, err=err_lbl: self._on_focus_in(widget, err),
        )
        entry.bind(
            "<FocusOut>",
            lambda e, widget=entry, err=err_lbl: self._on_focus_out(widget, err),
        )

        return {
            "container": container,
            "entry": entry,
            "err_lbl": err_lbl,
            "default": default_val,
            "prefix": prefix_text,
        }

    def toggle_remote_fields(self, selected_mode, widgets):
        if selected_mode == WorkMode.REMOTE.value:
            widgets["remote_frame"].pack(fill="x", pady=10)
        else:
            widgets["remote_frame"].pack_forget()
            self.clear_validation_errors(widgets)

    def on_tab_change(self):
        self.clear_validation_errors(self.ft_widgets)
        self.clear_validation_errors(self.pt_widgets)

    def clear_validation_errors(self, widgets):
        for w in widgets.values():
            if isinstance(w, dict) and "entry" in w:
                w["entry"].configure(border_color=self.normal_border_color)
                w["err_lbl"].grid_forget()

    def set_field_error(self, field_dict, message):
        field_dict["entry"].configure(border_color=self.error_border_color)
        field_dict["err_lbl"].configure(text=message)
        field_dict["err_lbl"].grid(row=2, column=0, sticky="w", pady=(1, 0))

    def reset_current_tab(self):
        current_tab = self.tabview.get()
        widgets = (
            self.ft_widgets if current_tab == self.tab_ft_name else self.pt_widgets
        )

        self.clear_validation_errors(widgets)

        for key, w in widgets.items():
            if isinstance(w, dict) and "entry" in w:
                w["entry"].delete(0, "end")
                if w["default"]:
                    w["entry"].insert(0, w["default"])
            elif key == "work_mode" and isinstance(w, ctk.CTkOptionMenu):
                w.set(WorkMode.ONSITE.value)
                self.toggle_remote_fields(WorkMode.ONSITE.value, widgets)

    def validate_and_submit(self):
        current_tab = self.tabview.get()
        is_ft = current_tab == self.tab_ft_name
        widgets = self.ft_widgets if is_ft else self.pt_widgets

        self.clear_validation_errors(widgets)
        has_error = False

        required_text_fields = ["emp_id", "name", "dept", "job_title"]
        for field_key in required_text_fields:
            val = widgets[field_key]["entry"].get().strip()
            if not val:
                self.set_field_error(widgets[field_key], "This field is required *")
                has_error = True

        numeric_fields = []
        if is_ft:
            numeric_fields.append(("salary", True, float))
            numeric_fields.append(("bonus", False, float))
        else:
            numeric_fields.append(("hourly_rate", True, float))
            numeric_fields.append(("hours_worked", False, float))

        if widgets["work_mode"].get() == WorkMode.REMOTE.value:
            numeric_fields.append(("internet_allowance", False, float))
            numeric_fields.append(("equipment_allowance", False, float))

            loc_val = widgets["remote_location"]["entry"].get().strip()
            if not loc_val:
                self.set_field_error(
                    widgets["remote_location"], "Location is required *"
                )
                has_error = True

        for field_key, is_req, num_type in numeric_fields:
            raw_val = widgets[field_key]["entry"].get().strip()

            if not raw_val:
                if is_req:
                    self.set_field_error(widgets[field_key], "This field is required *")
                    has_error = True
            else:
                try:
                    parsed_val = num_type(raw_val)
                    if parsed_val < 0:
                        self.set_field_error(
                            widgets[field_key], "Must be positive >= 0"
                        )
                        has_error = True
                except ValueError:
                    self.set_field_error(widgets[field_key], "Must be a valid number")
                    has_error = True

        if has_error:
            return

        ############### BackEnd Operations ##############
        final_emp_id = (
            f"{widgets['emp_id']['prefix']}{widgets['emp_id']['entry'].get().strip()}"
        )
        final_emp_name = widgets["name"]["entry"].get().strip()
        final_emp_department = widgets["dept"]["entry"].get().strip()
        final_emp_job_title = widgets["job_title"]["entry"].get().strip()
        final_emp_work_mode = WorkMode(widgets["work_mode"].get())

        employee_data = {
            "employee_id": final_emp_id,
            "name": final_emp_name,
            "department": final_emp_department,
            "job_title": final_emp_job_title,
            "work_mode": final_emp_work_mode,
            "remote_data": {},
        }

        if is_ft:
            employee_data["monthly_salary"] = float(
                widgets["salary"]["entry"].get().strip()
            )
            employee_data["bonus"] = float(widgets["bonus"]["entry"].get().strip())
        else:
            employee_data["hourly_rate"] = float(
                widgets["hourly_rate"]["entry"].get().strip()
            )
            employee_data["hours_worked"] = float(
                widgets["hours_worked"]["entry"].get().strip()
            )
        if final_emp_work_mode == WorkMode.REMOTE:
            employee_data["remote_data"]["location"] = (
                widgets["remote_location"]["entry"].get().strip()
            )

            employee_data["remote_data"]["internet_allowance"] = float(
                widgets["internet_allowance"]["entry"].get().strip()
            )
            employee_data["remote_data"]["equipment_allowance"] = float(
                widgets["equipment_allowance"]["entry"].get().strip()
            )

        # backend add start
        try:
            if is_ft:
                EmployeeManager.create_full_time_employee(**employee_data)
            else:
                EmployeeManager.create_part_time_employee(**employee_data)
            messagebox.showinfo(
                title="Success", message="Employee added successfully!", parent=self
            )

            self.refresh()
            self.destroy()
        except EmployeeError as e:
            messagebox.showerror(
                title="Error", message=f"Failed to add employee: {e}", parent=self
            )
