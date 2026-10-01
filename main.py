from frontend.app import EmployeeApp
from frontend.resource import resource_path

if __name__ == "__main__":
    app = EmployeeApp(
        title="Employees Management System",
        geometry=(1000, 600),
        resizable=False,
        icon=resource_path("frontend/icon/icon.ico"),
        appearance_mode="Dark",
        theme=resource_path("frontend/houda_theme.json"),
        show_splash=True,
    )
    app.mainloop()
