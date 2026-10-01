import webbrowser

import customtkinter as ctk


def GetFontFamily():
    return ctk.ThemeManager.theme["CTkFont"]["family"]


APP_VERSION = "1.0.0"


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            corner_radius=0,
            border_width=0,
        )

        self.columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(20, 15), sticky="w")

        title = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=(GetFontFamily(), 24, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Adjust how the app looks.",
            font=(GetFontFamily(), 13),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        appearance_card = ctk.CTkFrame(
            self,
            border_width=1,
            corner_radius=12,
        )
        appearance_card.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="nw")

        app_title = ctk.CTkLabel(
            appearance_card,
            text="Appearance",
            font=(GetFontFamily(), 16, "bold"),
        )
        app_title.pack(anchor="w", padx=20, pady=(15, 4))

        app_desc = ctk.CTkLabel(
            appearance_card,
            text="Choose a light or dark interface, or follow your system.",
            font=(GetFontFamily(), 12),
        )
        app_desc.pack(anchor="w", padx=20, pady=(0, 12))

        self.theme_segmented = ctk.CTkSegmentedButton(
            appearance_card,
            values=["Light", "Dark", "System"],
            selected_color="#1E2C35",
            selected_hover_color="#273844",
            unselected_color="#121D24",
            unselected_hover_color="#1A2730",
            text_color="#FFFFFF",
            font=(GetFontFamily(), 12),
            corner_radius=8,
            height=32,
            command=self.change_appearance_mode,
        )
        self.theme_segmented.set("Dark")
        self.theme_segmented.pack(anchor="w", padx=20, pady=(0, 15))

        about_card = ctk.CTkFrame(
            self,
            fg_color="#111B22",
            border_color="#1E2C35",
            border_width=1,
            corner_radius=12,
        )
        about_card.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="nw")

        about_title = ctk.CTkLabel(
            about_card,
            text="About Me",
            font=(GetFontFamily(), 16, "bold"),
            text_color="#FFFFFF",
        )
        about_title.pack(anchor="w", padx=20, pady=(15, 4))

        about_desc = ctk.CTkLabel(
            about_card,
            text=f"Employees Management System, version {APP_VERSION}",
            font=(GetFontFamily(), 12),
            text_color="#8B9A9E",
        )
        about_desc.pack(anchor="w", padx=20, pady=(0, 10))

        built_by = ctk.CTkLabel(
            about_card,
            text="Crafted with ♥ by Mahmoud Mohamed | Expert Python Developer",
            font=(GetFontFamily(), 13, "bold"),
            text_color="#10B981",
            cursor="hand2",
        )

        built_by.bind(
            "<Button-1>", lambda x: webbrowser.open("https://github.com/ehoda9")
        )

        built_by.pack(anchor="w", padx=20, pady=(0, 15))

    def change_appearance_mode(self, value):
        if value == "Light":
            ctk.set_appearance_mode("Light")
        elif value == "Dark":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("System")
