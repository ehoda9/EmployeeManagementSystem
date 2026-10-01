import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # type: ignore
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path: str) -> str:
    return os.path.join(BASE_DIR, relative_path)
