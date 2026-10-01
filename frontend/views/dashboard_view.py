import customtkinter as ctk

from backend.enums import EmployeeStatus
from backend.tax_calculator import TaxCalculator
from frontend.views.components.create import CreateEmployee


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, border_width=1)
        self.tooltip_window = None
        self.app = self.winfo_toplevel()
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="group1")

        title = ctk.CTkLabel(
            self, text="Dashboard Overview", font=(GetFontFamily(), 22, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        self.add_new = ctk.CTkButton(
            self,
            text="+ Add Employee",
            font=(GetFontFamily(), 12, "bold"),
            corner_radius=0,
            command=self.open_create_employee_modal,
        )
        self.add_new.grid(
            row=0,
            column=2,
            columnspan=2,
            padx=20,
            pady=(20, 10),
            sticky="e",
        )

        self.lbl_total = self.create_stat_card(
            0,
            "Total Employees",
            f"{len(self.app.employees)}",  # type: ignore
        )
        self.lbl_active = self.create_stat_card(
            1,
            "Active",
            f"{sum(1 for e in self.app.employees if e['status'] == EmployeeStatus.ACTIVE.value)}",  # type: ignore
        )
        self.lbl_on_leave = self.create_stat_card(
            2,
            "On-Leave",
            f"{sum(1 for e in self.app.employees if e['status'] == EmployeeStatus.ON_LEAVE.value)}",  # type: ignore
        )
        self.lbl_terminated = self.create_stat_card(
            3,
            "Terminated",
            f"{sum(1 for e in self.app.employees if e['status'] == EmployeeStatus.TERMINATED.value)}",  # type: ignore
        )

        #######statistics department
        self.department_statistics = ctk.CTkFrame(self, border_width=2)
        self.department_statistics.grid(
            row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew"
        )

        lbl_department = ctk.CTkLabel(
            self.department_statistics,
            text="Employees by department",
            font=(GetFontFamily(), 14, "bold"),
        )
        lbl_department.pack(pady=(15, 10), padx=15, anchor="w")
        dash_emp = self.app.update_employees_list()  # type: ignore
        employees = self.app.employees  # type: ignore
        dept_counts = {}
        for e in employees:
            dept_counts[e["department"]] = dept_counts.get(e["department"], 0) + 1
        max_count = max(dept_counts.values(), default=1)

        dept_data = {
            name: {"ratio": count / max_count, "count": count}
            for name, count in dept_counts.items()
        }

        self.create_department_chart(self.department_statistics, dept_data)
        #####payroll sections with Taxes
        grosss_total = sum(e.calculate_gross_pay() for e in dash_emp)

        taxx_total = sum(
            TaxCalculator.calculate_tax(e.calculate_gross_pay()) for e in dash_emp
        )
        net_total = grosss_total - taxx_total
        self.lbl_payroll_net, self.lbl_payroll_gross, self.lbl_payroll_tax = (
            self.create_payroll_card(
                row=3,
                net_salary=f"{net_total}",
                gross_salary=f"{grosss_total}",
                tax_val=f"{taxx_total}",
            )
        )

    def create_stat_card(self, col, title, value):
        card = ctk.CTkFrame(self, border_width=2)
        card.grid(row=1, column=col, padx=10, pady=10, sticky="nsew")
        lbl_title = ctk.CTkLabel(card, text=title, font=(GetFontFamily(), 13))
        lbl_title.pack(pady=(15, 5), padx=15, anchor="w")
        lbl_val = ctk.CTkLabel(card, text=value, font=(GetFontFamily(), 26, "bold"))
        lbl_val.pack(pady=(0, 15), padx=15, anchor="w")
        return lbl_val

    def create_department_chart(self, parent_frame, data):
        if hasattr(self, "_chart_container") and self._chart_container.winfo_exists():
            self._chart_container.destroy()

        chart_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        chart_container.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self._chart_container = chart_container
        num_items = len(data)
        for i in range(num_items):
            chart_container.grid_columnconfigure(i, weight=1)

        normal_color = "#1f8a70"
        hover_color = "#28b291"

        for index, (dept_name, dept_info) in enumerate(data.items()):
            col_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
            col_frame.grid(row=0, column=index, sticky="nsew")

            ratio = dept_info["ratio"]
            count = dept_info["count"]

            progress = ctk.CTkProgressBar(
                col_frame,
                orientation="vertical",
                height=150,
                width=24,
                progress_color=normal_color,
                corner_radius=0,
            )
            progress.set(ratio)
            progress.pack(pady=(10, 8), expand=True)

            progress.bind(
                "<Enter>",
                lambda e, p=progress, c=count: self._on_hover_enter(
                    p, hover_color, c, e
                ),
            )
            progress.bind(
                "<Leave>",
                lambda e, p=progress: self._on_hover_leave(p, normal_color),
            )
            progress.bind("<Motion>", self._on_hover_move)

            lbl_name = ctk.CTkLabel(
                col_frame,
                text=dept_name,
                font=(GetFontFamily(), 12),
                text_color="gray70",
            )
            lbl_name.pack(pady=(0, 5))

    def _on_hover_enter(self, progress_widget, hover_color, count, event):
        progress_widget.configure(progress_color=hover_color)

        self._show_tooltip(event, f"{count} Employees")

    def _on_hover_leave(self, progress_widget, normal_color):
        progress_widget.configure(progress_color=normal_color)

        self._hide_tooltip()

    def _on_hover_move(self, event):
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            x = event.x_root + 12
            y = event.y_root + 12
            self.tooltip_window.geometry(f"+{x}+{y}")

    def _show_tooltip(self, event, text):
        self._hide_tooltip()

        self.tooltip_window = ctk.CTkToplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            self.tooltip_window,
            text=text,
            font=(GetFontFamily(), 11, "bold"),
            fg_color=("#2b2b2b", "#1f1f1f"),
            text_color="#ffffff",
            corner_radius=4,
            padx=8,
            pady=4,
        )
        label.pack()

        x = event.x_root + 12
        y = event.y_root + 12
        self.tooltip_window.geometry(f"+{x}+{y}")

    def _hide_tooltip(self):
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def create_payroll_card(self, row, net_salary, gross_salary, tax_val):
        payroll_card = ctk.CTkFrame(self, border_width=2)
        payroll_card.grid(
            row=row, column=0, columnspan=4, padx=10, pady=10, sticky="nsew"
        )

        lbl_title = ctk.CTkLabel(
            payroll_card, text="Monthly payroll", font=(GetFontFamily(), 14, "bold")
        )
        lbl_title.pack(pady=(15, 5), padx=15, anchor="w")

        lbl_net = ctk.CTkLabel(
            payroll_card, text=net_salary, font=(GetFontFamily(), 28, "bold")
        )
        lbl_net.pack(pady=(5, 0), padx=15, anchor="w")

        lbl_sub = ctk.CTkLabel(
            payroll_card,
            text="Net, after tax",
            font=(GetFontFamily(), 12),
            text_color="gray70",
        )
        lbl_sub.pack(pady=(0, 10), padx=15, anchor="w")

        separator = ctk.CTkFrame(payroll_card, height=1, fg_color="gray30")
        separator.pack(fill="x", padx=15, pady=10)

        row_gross = ctk.CTkFrame(payroll_card, fg_color="transparent")
        row_gross.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(
            row_gross, text="Gross", font=(GetFontFamily(), 13), text_color="gray70"
        ).pack(side="left")
        lbl_gross_val = ctk.CTkLabel(
            row_gross, text=gross_salary, font=(GetFontFamily(), 13, "bold")
        )
        lbl_gross_val.pack(side="right")

        row_tax = ctk.CTkFrame(payroll_card, fg_color="transparent")
        row_tax.pack(fill="x", padx=15, pady=(2, 15))
        ctk.CTkLabel(
            row_tax, text="Tax", font=(GetFontFamily(), 13), text_color="gray70"
        ).pack(side="left")
        lbl_tax_val = ctk.CTkLabel(
            row_tax, text=tax_val, font=(GetFontFamily(), 13, "bold")
        )
        lbl_tax_val.pack(side="right")

        return lbl_net, lbl_gross_val, lbl_tax_val

    def refresh(self):
        emp = self.app.update_employees_list()  # type: ignore
        employees = self.app.employees  # type: ignore

        total = len(employees)
        active = sum(1 for e in employees if e["status"] == EmployeeStatus.ACTIVE.value)
        on_leave = sum(
            1 for e in employees if e["status"] == EmployeeStatus.ON_LEAVE.value
        )
        terminated = sum(
            1 for e in employees if e["status"] == EmployeeStatus.TERMINATED.value
        )

        self.lbl_total.configure(text=str(total))
        self.lbl_active.configure(text=str(active))
        self.lbl_on_leave.configure(text=str(on_leave))
        self.lbl_terminated.configure(text=str(terminated))

        dept_counts = {}
        for e in employees:
            dept_counts[e["department"]] = dept_counts.get(e["department"], 0) + 1
        max_count = max(dept_counts.values(), default=1)

        dept_data = {
            name: {"ratio": count / max_count, "count": count}
            for name, count in dept_counts.items()
        }

        self.create_department_chart(self.department_statistics, dept_data)
        # payroll sections
        gross_total = sum(e.calculate_gross_pay() for e in emp)

        tax_total = sum(
            TaxCalculator.calculate_tax(e.calculate_gross_pay()) for e in emp
        )
        net_total = gross_total - tax_total
        self.lbl_payroll_net.configure(text=f"EGP {net_total:.0f}")
        self.lbl_payroll_gross.configure(text=f"{gross_total:.0f}")
        self.lbl_payroll_tax.configure(text=f"{tax_total:.0f}")

    def open_create_employee_modal(self):
        modal = CreateEmployee(self, self.refresh)
        modal.grab_set()
