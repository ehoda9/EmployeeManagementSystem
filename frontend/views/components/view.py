import customtkinter as ctk

from backend.tax_calculator import TaxCalculator
from employee_manager import EmployeeManager
from frontend.resource import resource_path


def Theme(name):
    return ctk.ThemeManager.theme["Houda"][name]


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


AVATAR_COLORS = {
    "Active": "#10B981",
    "On leave": "#F59E0B",
    "Terminated": "#EF4444",
}

PILL_COLOR_KEYS = {
    "Active": ("success_soft", "success"),
    "On leave": ("warning_soft", "warning"),
    "Terminated": ("danger_soft", "danger"),
}


class ViewEmployee(ctk.CTkToplevel):
    def __init__(self, parent, emp_id):
        self.emp = EmployeeManager.get_employee(emp_id)
        emp = self.emp.get_details()
        super().__init__(parent)
        self.width = 520
        self.height = 680

        self.title(f"View Employee | {emp['name']}")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width // 2) - (self.width // 2))
        y = int((screen_height // 2) - (self.height // 2))

        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.iconbitmap(resource_path("frontend/icon/employee.ico"))
        self.transient(parent)

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
            text="View Employee Full Data",
            font=(GetFontFamily(), 18, "bold"),
            text_color=Theme("text"),
        )
        title_label.pack(side="left")

        body = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        self._build_identity(body, emp)

        self._section_divider(body, "Employment Details:")
        self._info_row(body, "Department", emp["department"])
        self._info_row(body, "Employment Type", self.emp.employment_type)
        self._info_row(body, "Work Mode", emp["work_mode"])
        self._info_row(body, "Status", emp["status"], pill=True)
        self._info_row(body, "Hire Date", emp["hire_date"])

        self._section_divider(body, "Bills:")
        if self.emp.employment_type == "Full-Time":
            self._info_row(body, "Monthly Salary", emp["monthly_salary"])
            self._info_row(body, "Bonus", emp["bonus"])
        else:
            self._info_row(body, "Hourly Rate", emp["hourly_rate"])
            self._info_row(body, "Hours Worked", emp["hours_worked"])

        if emp["work_mode"] == "Remote":
            self._section_divider(body, "Remote Profile :")
            self._info_row(body, "Location", emp["remote_location"])
            self._info_row(
                body,
                "Internet Allowance",
                self.emp.remote_profile.internet_allowance,  # type: ignore
            )
            self._info_row(
                body,
                "Equipment Allowance",
                self.emp.remote_profile.equipment_allowance,  # type: ignore
            )
            self._info_row(
                body, "Total Remote Allowance", emp["remote_allowance"], highlight=True
            )
        self._section_divider(body, "Tax")
        gross = self.emp.calculate_gross_pay()
        self._info_row(body, "Gross Pay", gross)
        self._info_row(
            body,
            "Tax",
            f"{TaxCalculator.calculate_tax(gross):.2f}",
        )
        self._info_row(
            body, "Net Pay", TaxCalculator.calculate_net_pay(gross), highlight=True
        )

        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

        close_btn = ctk.CTkButton(
            footer_frame,
            text="Close",
            font=(GetFontFamily(), 12, "bold"),
            fg_color=Theme("accent"),
            hover_color=Theme("accent_hover"),
            text_color=Theme("accent_ink"),
            width=100,
            command=self.destroy,
        )
        close_btn.pack(side="right")

    def _build_identity(self, parent, emp):
        identity = ctk.CTkFrame(parent, fg_color="transparent")
        identity.pack(fill="x", pady=(5, 10))

        initials = "".join(part[0] for part in emp["name"].split()[:2]).upper()
        avatar = ctk.CTkLabel(
            identity,
            text=initials,
            width=56,
            height=56,
            corner_radius=28,
            fg_color=AVATAR_COLORS.get(emp["status"], Theme("accent")),
            text_color="#FFFFFF",
            font=(GetFontFamily(), 18, "bold"),
        )
        avatar.pack(side="left", padx=(0, 15))

        text_col = ctk.CTkFrame(identity, fg_color="transparent")
        text_col.pack(side="left", anchor="w")

        ctk.CTkLabel(
            text_col, text=emp["name"], font=(GetFontFamily(), 18, "bold"), anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_col,
            text=emp["job_title"],
            font=(GetFontFamily(), 13),
            text_color=Theme("muted"),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            text_col,
            text=f"ID: {emp['id']}",
            font=(GetFontFamily(), 11),
            text_color=Theme("faint"),
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

    def _section_divider(self, parent, text):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(14, 6))
        ctk.CTkLabel(
            wrap,
            text=text,
            font=(GetFontFamily(), 12, "bold"),
            text_color=Theme("muted"),
        ).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=Theme("border")).pack(
            fill="x", pady=(4, 0)
        )

    def _info_row(self, parent, label, value, pill=False, highlight=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)

        ctk.CTkLabel(
            row,
            text=label,
            font=(GetFontFamily(), 13),
            text_color=Theme("muted"),
            width=160,
            anchor="w",
        ).pack(side="left")

        if pill:
            bg_key, fg_key = PILL_COLOR_KEYS.get(value, ("raised", "text"))
            ctk.CTkLabel(
                row,
                text=value,
                font=(GetFontFamily(), 11, "bold"),
                fg_color=Theme(bg_key),
                text_color=Theme(fg_key),
                corner_radius=6,
                width=90,
                height=24,
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                row,
                text=str(value),
                font=(
                    GetFontFamily(),
                    15 if highlight else 13,
                    "bold" if highlight else "normal",
                ),
                text_color=Theme("accent") if highlight else Theme("text"),
                anchor="w",
            ).pack(side="left")
