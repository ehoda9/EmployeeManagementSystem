import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backend.enums import EmployeeStatus
from backend.exceptions import EmployeeError
from employee_manager import EmployeeManager
from frontend.views.components.create import CreateEmployee
from frontend.views.components.update import UpdateEmployee
from frontend.views.components.view import ViewEmployee


def Theme(name):
    return ctk.ThemeManager.theme["Houda"][name]


def get_current_color(color_value):
    if isinstance(color_value, (tuple, list)):
        mode = ctk.get_appearance_mode()
        return color_value[1] if mode.lower() == "dark" else color_value[0]
    return color_value


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


STATUS_TABS = ["All", "Active", "On Leave", "Terminated"]

FILTER_FIELDS = [
    ("department", "Department"),
    ("status", "Status"),
    ("work_mode", "Work Mode"),
    ("job_title", "Job Title"),
]

AVATAR_COLORS = {
    "Active": "#10B981",
    "On Leave": "#F59E0B",
    "Terminated": "#EF4444",
}


class EmployeesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", border_width=0)
        self.active_tab = "All"
        self.active_filter_fields: set[str] = set()
        self.app = self.winfo_toplevel()

        self._build_header()
        self._build_card()
        self._build_toolbar()
        self._build_filter_panel()
        self._build_column_headers()
        self._build_table_area()

        self.render_rows()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left, text="Employees", font=(GetFontFamily(), 24, "bold"), anchor="w"
        ).pack(anchor="w")
        depts = len({e["department"] for e in self.app.employees})  # type: ignore

        self.subtitle_lbl = ctk.CTkLabel(
            left,
            text=f"{len(self.app.employees)} people across {depts} departments",  # type: ignore
            font=(GetFontFamily(), 13),
            text_color=Theme("muted"),
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            right, placeholder_text="Search employees...", width=280, height=36
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.render_rows())

        ctk.CTkButton(
            right,
            text="+  Add employee",
            font=(GetFontFamily(), 13, "bold"),
            fg_color=Theme("accent"),
            hover_color=Theme("accent_hover"),
            text_color=Theme("accent_ink"),
            height=36,
            command=self.open_create_employee_modal,
        ).pack(side="left")

    def _build_card(self):
        self.card = ctk.CTkFrame(self, corner_radius=14, border_width=2)
        self.card.pack(fill="both", expand=True)

    def _build_toolbar(self):
        self.toolbar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=15, pady=15)

        tabs_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        tabs_frame.pack(side="left")

        self.tab_buttons = {}
        for name in STATUS_TABS:
            btn = ctk.CTkButton(
                tabs_frame,
                text=name,
                width=76,
                height=30,
                corner_radius=8,
                font=(GetFontFamily(), 12, "bold"),
                fg_color=Theme("surface")
                if name == self.active_tab
                else Theme("raised"),
                text_color=Theme("text"),
                hover_color=Theme("hover"),
                command=lambda n=name: self.set_tab(n),
            )
            btn.pack(side="left", padx=(0, 6))
            self.tab_buttons[name] = btn

        ctk.CTkButton(
            self.toolbar,
            text="Search Filters",
            width=90,
            height=30,
            corner_radius=8,
            fg_color=Theme("raised"),
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            command=self.toggle_filter_panel,
        ).pack(side="left", padx=(10, 0))

        self.count_lbl = ctk.CTkLabel(
            self.toolbar, text="", font=(GetFontFamily(), 12), text_color=Theme("muted")
        )
        self.count_lbl.pack(side="right")

    def _build_filter_panel(self):
        self.filter_panel = ctk.CTkFrame(
            self.card, fg_color=Theme("raised"), corner_radius=10
        )

        inner = ctk.CTkFrame(self.filter_panel, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            inner, text="Search within:", font=(GetFontFamily(), 12, "bold")
        ).pack(side="left", padx=(0, 12))

        self.filter_vars: dict[str, ctk.BooleanVar] = {}
        for key, label in FILTER_FIELDS:
            var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                inner,
                text=label,
                variable=var,
                font=(GetFontFamily(), 12),
                command=self.on_filter_change,
            ).pack(side="left", padx=8)
            self.filter_vars[key] = var

        ctk.CTkButton(
            inner,
            text="Reset",
            width=70,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=Theme("border"),
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            command=self.reset_filters,
        ).pack(side="right")

    def toggle_filter_panel(self):
        if self.filter_panel.winfo_ismapped():
            self.filter_panel.pack_forget()
        else:
            self.filter_panel.pack(fill="x", padx=15, pady=(0, 15), after=self.toolbar)

    def on_filter_change(self):
        self.active_filter_fields = {
            key for key, var in self.filter_vars.items() if var.get()
        }
        self.render_rows()

    def reset_filters(self):
        for var in self.filter_vars.values():
            var.set(False)
        self.active_filter_fields = set()
        self.render_rows()

    def _build_column_headers(self):
        row = ctk.CTkFrame(self.card, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(5, 8))

        for text, width in (
            ("Name", 220),
            ("Department", 110),
            ("Status", 100),
            ("Joined", 100),
        ):
            ctk.CTkLabel(
                row,
                text=text,
                font=(GetFontFamily(), 12, "bold"),
                text_color=Theme("muted"),
                width=width,
                anchor="w",
            ).pack(side="left")

        ctk.CTkLabel(
            row,
            text="Actions",
            font=(GetFontFamily(), 12, "bold"),
            text_color=Theme("muted"),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(self.card, height=1, fg_color=Theme("border")).pack(
            fill="x", padx=15
        )

    def _build_table_area(self):
        self.table_scroll = ctk.CTkScrollableFrame(
            self.card, fg_color="transparent", height=420
        )
        self.table_scroll.pack(fill="both", expand=True, padx=5, pady=(5, 15))

    def set_tab(self, name):
        self.active_tab = name
        for tab_name, btn in self.tab_buttons.items():
            btn.configure(
                fg_color=Theme("surface") if tab_name == name else Theme("raised")
            )
        self.render_rows()

    def _matches_search(self, emp, query):
        query = query.strip().lower()
        if not query:
            return True
        if not self.active_filter_fields:
            return query in emp["name"].lower()
        return any(
            query in str(emp.get(field, "")).lower()
            for field in self.active_filter_fields
        )

    def render_rows(self):
        for child in self.table_scroll.winfo_children():
            child.destroy()

        query = self.search_entry.get()
        filtered = []
        for e in self.app.employees:  # type: ignore
            status_val = (
                e["status"].value if hasattr(e["status"], "value") else str(e["status"])
            )
            if (
                self.active_tab == "All" or status_val == self.active_tab
            ) and self._matches_search(e, query):
                filtered.append(e)

        self.count_lbl.configure(text=f"{len(filtered)} employees")

        for emp in filtered:
            self._build_row(emp)

    def _build_row(self, emp):
        row = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        row.pack(fill="x", pady=6)

        name_col = ctk.CTkFrame(row, fg_color="transparent", width=220, height=44)
        name_col.pack(side="left")
        name_col.pack_propagate(False)

        status_str = (
            emp["status"].value
            if hasattr(emp["status"], "value")
            else str(emp["status"])
        )

        initials = "".join(part[0] for part in emp["name"].split()[:2]).upper()
        avatar = ctk.CTkLabel(
            name_col,
            text=initials,
            width=38,
            height=38,
            corner_radius=19,
            fg_color=AVATAR_COLORS.get(status_str, Theme("accent")),
            text_color="#FFFFFF",
            font=(GetFontFamily(), 13, "bold"),
        )
        avatar.pack(side="left", padx=(0, 12))

        text_col = ctk.CTkFrame(name_col, fg_color="transparent")
        text_col.pack(side="left", anchor="w")
        ctk.CTkLabel(
            text_col, text=emp["name"], font=(GetFontFamily(), 13, "bold"), anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_col,
            text=emp["job_title"],
            font=(GetFontFamily(), 12),
            text_color=Theme("muted"),
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            row,
            text=emp["department"],
            font=(GetFontFamily(), 13),
            width=110,
            anchor="w",
        ).pack(side="left")

        pill_colors = {
            "Active": (Theme("success_soft"), Theme("success")),
            "On Leave": (Theme("warning_soft"), Theme("warning")),
            "Terminated": (Theme("danger_soft"), Theme("danger")),
        }
        bg, fg = pill_colors.get(status_str, (Theme("raised"), Theme("text")))

        status_col = ctk.CTkFrame(row, fg_color="transparent", width=90, height=44)
        status_col.pack(side="left")
        status_col.pack_propagate(False)
        ctk.CTkLabel(
            status_col,
            text=status_str,
            font=(GetFontFamily(), 11, "bold"),
            fg_color=bg,
            text_color=fg,
            corner_radius=0,
            width=80,
            height=26,
        ).pack(side="left")

        ctk.CTkLabel(
            row,
            text=emp["joined"],
            font=(GetFontFamily(), 12),
            text_color=Theme("muted"),
            width=95,
            anchor="w",
        ).pack(side="left")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            actions,
            text="View",
            width=54,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=Theme("border"),
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            command=lambda: self.open_view_employee_modal(emp["id"]),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions,
            text="Edit",
            width=54,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=Theme("border"),
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            command=lambda: self.open_update_employee_modal(emp["id"]),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions,
            text="Delete",
            width=60,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=Theme("danger"),
            text_color=Theme("danger"),
            hover_color=Theme("danger_soft"),
            command=lambda: self.delete_employee(emp["id"]),
        ).pack(side="left", padx=2)

        self._bind_context_menu_recursive(row, emp["id"])

    def _bind_context_menu_recursive(self, widget, emp_id):
        widget.bind(
            "<Button-3>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
        )
        widget.bind(
            "<Button-2>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
        )

        if hasattr(widget, "_canvas") and widget._canvas:
            widget._canvas.bind(
                "<Button-3>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
            )
            widget._canvas.bind(
                "<Button-2>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
            )

        if hasattr(widget, "_label") and widget._label:
            widget._label.bind(
                "<Button-3>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
            )
            widget._label.bind(
                "<Button-2>", lambda e, e_id=emp_id: self._show_context_menu(e, e_id)
            )

        for child in widget.winfo_children():
            self._bind_context_menu_recursive(child, emp_id)

    def _show_context_menu(self, event, emp_id):
        bg_color = get_current_color(Theme("raised"))
        text_color = get_current_color(Theme("text"))
        hover_color = get_current_color(Theme("hover"))

        menu = tk.Menu(
            self,
            tearoff=0,
            bg=bg_color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            bd=1,
            font=(GetFontFamily(), 11),
        )
        x = EmployeeManager.get_employee(emp_id)
        if x.status == EmployeeStatus.ACTIVE:
            menu.add_command(
                label="On-Leave",
                command=lambda: self.change_employee_status(emp_id, "leave"),
            )
        elif x.status == EmployeeStatus.ON_LEAVE:
            menu.add_command(
                label="Active",
                command=lambda: self.change_employee_status(emp_id, "back"),
            )
        menu.add_separator()
        menu.add_command(
            label="Terminate",
            command=lambda: self.change_employee_status(emp_id, "terminate"),
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def change_employee_status(self, eid, status: str):
        x = EmployeeManager.get_employee(eid)
        try:
            if status == "leave":
                x.put_on_leave()
            elif status == "back":
                x.return_from_leave()
            elif status == "terminate":
                x.terminate()
            self.refresh()
        except EmployeeError as e:
            messagebox.showerror(title="Error", message=f"{e}", parent=self)

    def delete_employee(self, id):
        EmployeeManager.delete_employee(id)
        self.refresh()

    def open_view_employee_modal(self, emp_id):
        modal = ViewEmployee(self, emp_id)
        modal.grab_set()

    def open_update_employee_modal(self, emp_id):
        modal = UpdateEmployee(self, emp_id, self.refresh)
        modal.grab_set()

    def open_create_employee_modal(self):
        modal = CreateEmployee(self, self.refresh)
        modal.grab_set()

    def refresh(self):
        self.app.update_employees_list()  # type: ignore
        depts = len({e["department"] for e in self.app.employees})  # type: ignore
        self.subtitle_lbl.configure(
            text=f"{len(self.app.employees)} people across {depts} departments",  # type: ignore
        )
        self.render_rows()
