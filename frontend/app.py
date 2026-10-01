import webbrowser

import customtkinter as ctk
from PIL import Image

from employee_manager import EmployeeManager
from frontend.resource import resource_path
from frontend.views.dashboard_view import DashboardView
from frontend.views.employees_view import EmployeesView
from frontend.views.settings_view import SettingsView

GITHUB_URL = "https://github.com/ehoda9"
APP_VERSION = "1.0.0"
AUTHOR = "Mahmoud Mohamed"


def Theme(name):
    return ctk.ThemeManager.theme["Houda"][name]


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


class EmployeeApp(ctk.CTk):
    def __init__(
        self,
        title: str,
        geometry: tuple[int, int],
        resizable: bool,
        icon: str,
        appearance_mode: str,
        theme: str,
        show_splash: bool = False,
    ):
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme(theme)

        super().__init__()
        self.title(title)

        # store global employees data
        self.employees = []

        width, height = geometry
        self.width = width
        self.height = height
        self.resizable(resizable, resizable)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width // 2) - (self.width // 2))
        y = int((screen_height // 2) - (self.height // 2))

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.iconbitmap(icon)

        self.show_splash = show_splash
        self.current_view = None
        self.ui_initialized = False

        if self.show_splash:
            self.withdraw()
            self._build_splash_screen(screen_width, screen_height)
        else:
            self._initialize_main_ui()
            self.switch_view("dashboard")

    def _build_splash_screen(self, screen_width, screen_height):
        self.splash = ctk.CTkToplevel(self)
        self.splash.overrideredirect(True)

        w, h = 480, 280
        sx = int((screen_width // 2) - (w // 2))
        sy = int((screen_height // 2) - (h // 2))

        self.splash.geometry(f"{w}x{h}+{sx}+{sy}")
        self.splash.attributes("-topmost", True)
        self.splash.attributes("-alpha", 1.0)

        self.splash_frame = ctk.CTkFrame(
            self.splash,
            width=w,
            height=h,
            border_width=4,
            border_color=Theme("border"),
            corner_radius=0,
        )
        self.splash_frame.pack(fill="both", expand=True)
        self.splash_frame.pack_propagate(False)

        try:
            splash_logo = ctk.CTkImage(
                light_image=Image.open(resource_path("frontend/icon/icon.png")),
                dark_image=Image.open(resource_path("frontend/icon/icon.png")),
                size=(70, 70),
            )
            logo_label = ctk.CTkLabel(self.splash_frame, image=splash_logo, text="")
            logo_label.place(relx=0.53, rely=0.20, anchor="center")
        except FileNotFoundError:
            pass

        self.title_label = ctk.CTkLabel(
            self.splash_frame,
            text="Employees Management System",
            font=(GetFontFamily(), 20, "bold"),
        )
        self.title_label.pack(pady=(50, 30))

        self.launch_btn = ctk.CTkButton(
            self.splash_frame,
            text="Get started",
            font=(GetFontFamily(), 16, "bold"),
            width=160,
            height=40,
            corner_radius=8,
            command=self.start_program,
        )
        self.launch_btn.pack(pady=(10, 10))

        version_label = ctk.CTkLabel(
            self.splash_frame,
            text=f"Version {APP_VERSION}",
            font=(GetFontFamily(), 11),
            text_color=Theme("muted"),
        )

        splash_author_label = ctk.CTkLabel(
            self.splash_frame,
            text=f"2026 @ {AUTHOR}",
            font=(GetFontFamily(), 11),
            text_color=Theme("muted"),
            cursor="hand2",
        )
        splash_author_label.bind("<Button-1>", lambda e: self.open_github_profile())

        version_label.place(x=390, y=250, anchor="w")
        splash_author_label.place(x=20, y=250, anchor="w")

        self.progress_bar = None
        self.loading_label = None
        self.dots_count = 0
        self.current_status = "Loading GUI"

    def _initialize_main_ui(self):
        if self.ui_initialized:
            return

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(
            self, width=240, corner_radius=0, fg_color=Theme("sidebar")
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        self.header_frame = ctk.CTkFrame(
            self.sidebar_frame, fg_color="transparent", border_width=0
        )
        self.header_frame.grid(row=0, column=0, padx=15, pady=(20, 30), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        try:
            self.icon_dashboard = ctk.CTkImage(
                Image.open(resource_path("frontend/icon/dashboard.png")), size=(20, 20)
            )
            self.icon_employees = ctk.CTkImage(
                Image.open(resource_path("frontend/icon/employees.png")), size=(20, 20)
            )
            self.icon_settings = ctk.CTkImage(
                Image.open(resource_path("frontend/icon/settings.png")), size=(20, 20)
            )
            self.icon_mode = ctk.CTkImage(
                light_image=Image.open(resource_path("frontend/icon/sun.png")),
                dark_image=Image.open(resource_path("frontend/icon/moon.png")),
                size=(20, 20),
            )
        except FileNotFoundError:
            self.icon_dashboard = None
            self.icon_employees = None
            self.icon_settings = None
            self.icon_mode = None

        self.btn_theme = ctk.CTkButton(
            self.header_frame,
            text="",
            image=self.icon_mode,
            width=36,
            height=36,
            corner_radius=18,
            border_width=1,
            border_color=Theme("border"),
            fg_color=("#162134", "#16252B"),
            anchor="center",
            command=self.toggle_appearance_mode,
        )
        self.btn_theme.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="EMS",
            font=ctk.CTkFont(family=GetFontFamily(), size=22, weight="bold"),
        )
        self.logo_label.grid(row=0, column=1, sticky="w")

        self.menu_frame = ctk.CTkFrame(
            self.sidebar_frame, fg_color="transparent", border_width=0
        )
        self.menu_frame.grid(row=1, column=0, padx=10, sticky="new")
        self.menu_frame.grid_columnconfigure(0, weight=1)

        self.btn_dash = ctk.CTkButton(
            self.menu_frame,
            text="Dashboard",
            image=self.icon_dashboard,
            compound="left",
            anchor="w",
            height=38,
            corner_radius=6,
            fg_color="transparent",
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            font=(GetFontFamily(), 13),
            cursor="hand2",
            command=lambda: self.switch_view("dashboard"),
        )
        self.btn_dash.grid(row=0, column=0, pady=2, sticky="ew")

        self.btn_emp = ctk.CTkButton(
            self.menu_frame,
            text="Employees",
            image=self.icon_employees,
            compound="left",
            anchor="w",
            height=38,
            corner_radius=6,
            fg_color="transparent",
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            font=(GetFontFamily(), 13),
            cursor="hand2",
            command=lambda: self.switch_view("employees"),
        )
        self.btn_emp.grid(row=1, column=0, pady=2, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.menu_frame,
            text="Settings",
            image=self.icon_settings,
            compound="left",
            anchor="w",
            height=38,
            corner_radius=6,
            fg_color="transparent",
            text_color=Theme("text"),
            hover_color=Theme("hover"),
            font=(GetFontFamily(), 13),
            cursor="hand2",
            command=lambda: self.switch_view("settings"),
        )
        self.btn_settings.grid(row=2, column=0, pady=2, sticky="ew")

        self.footer_frame = ctk.CTkFrame(
            self.sidebar_frame, fg_color="transparent", border_width=0
        )
        self.footer_frame.grid(row=3, column=0, padx=15, pady=15, sticky="sw")

        self.author_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"2026 @ {AUTHOR}",
            font=(GetFontFamily(), 11),
            text_color=("#4F4F4F", "#DEDEDE"),
            cursor="hand2",
        )
        self.author_label.bind("<Button-1>", lambda e: self.open_github_profile())
        self.author_label.pack(anchor="w")

        self.version_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"version {APP_VERSION}",
            font=(GetFontFamily(), 11),
            text_color=Theme("muted"),
        )
        self.version_label.pack(anchor="w")

        self.container_frame = ctk.CTkFrame(
            self, fg_color="transparent", border_width=0
        )
        self.container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.ui_initialized = True

    def switch_view(self, view):
        if self.current_view is not None:
            self.current_view.destroy()
        if view == "dashboard":
            self.current_view = DashboardView(self.container_frame)
        elif view == "employees":
            self.current_view = EmployeesView(self.container_frame)

        elif view == "settings":
            self.current_view = SettingsView(self.container_frame)

        if self.current_view is not None:
            self.title(f"Employees Management System | {view.capitalize()}")
            self.current_view.pack(fill="both", expand=True)

    def open_github_profile(self):
        webbrowser.open(GITHUB_URL)

    def toggle_appearance_mode(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def start_program(self):
        hover_light, hover_dark = Theme("accent_hover")
        self.btn_steps = [
            hover_light if ctk.get_appearance_mode() == "Light" else hover_dark,
            "#0E635C",
            "#0D524C",
            "#0B413D",
            "#143133",
            "#13292E",
            "#14252B",
            (
                Theme("surface")[1]
                if ctk.get_appearance_mode() == "Dark"
                else Theme("surface")[0]
            ),
        ]
        self.text_steps = [
            "#D6ECE8",
            "#B4DBD4",
            "#8DBFB7",
            "#66A399",
            "#43847A",
            "#24645C",
            (
                Theme("surface")[1]
                if ctk.get_appearance_mode() == "Dark"
                else Theme("surface")[0]
            ),
            (
                Theme("surface")[1]
                if ctk.get_appearance_mode() == "Dark"
                else Theme("surface")[0]
            ),
        ]
        self.fade_step(0)

    def fade_step(self, step):
        if self.launch_btn and self.launch_btn.winfo_exists():
            if step < len(self.btn_steps):
                self.launch_btn.configure(
                    fg_color=self.btn_steps[step],
                    text_color=self.text_steps[step],
                )
                self.after(30, lambda: self.fade_step(step + 1))
            else:
                self.launch_btn.destroy()
                self.show_loading_elements()

    def show_loading_elements(self):
        self.loading_label = ctk.CTkLabel(
            self.splash_frame,
            text=self.current_status,
            font=(GetFontFamily(), 13),
        )
        self.loading_frame_pady = 20
        self.loading_label.pack(pady=(self.loading_frame_pady, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self.splash_frame,
            width=320,
            height=6,
            progress_color=Theme("accent"),
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.animate_loading_text()
        self.update_splash_progress(0)

    def animate_loading_text(self):
        if self.loading_label and self.loading_label.winfo_exists():
            self.dots_count = (self.dots_count + 1) % 4
            dots = ". " * self.dots_count
            self.loading_label.configure(text=f"{self.current_status} {dots}")
            self.after(200, self.animate_loading_text)

    def update_splash_progress(self, value):
        if self.progress_bar is not None and value <= 1.0:
            self.progress_bar.set(value)

            if value < 0.40:
                self.current_status = "Loading GUI"
            elif value < 0.80:
                self.current_status = "Loading employees data"
                if not self.ui_initialized:
                    self._initialize_main_ui()
                    self.switch_view("dashboard")
            elif value < 0.90:
                self.current_status = "Starting"
            else:
                self.current_status = "Complete"

            self.after(20, lambda: self.update_splash_progress(value + 0.02))
        else:
            self.deiconify()
            self.update_idletasks()
            self.fade_away()

    def fade_away(self):
        if self.splash and self.splash.winfo_exists():
            current_alpha = self.splash.attributes("-alpha")
            if current_alpha > 0:
                current_alpha -= 0.15
                self.splash.attributes("-alpha", current_alpha)
                self.after(25, self.fade_away)
            else:
                self.splash.destroy()

    def update_employees_list(self):
        my_emps = EmployeeManager.get_all_employee()

        self.employees = [
            {
                "id": e.employee_id,
                "name": e.name,
                "job_title": e.job_title,
                "department": e.department,
                "status": e.status.value,
                "work_mode": e.work_mode.value,
                "joined": e.hire_date,
            }
            for e in my_emps
        ]

        return my_emps
