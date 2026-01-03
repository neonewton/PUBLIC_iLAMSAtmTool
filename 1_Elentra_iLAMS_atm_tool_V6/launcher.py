import subprocess
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

APP = resource_path(
    os.path.join("1_Elentra_iLAMS_atm_tool_V6", "app.py")
)

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    APP
])
