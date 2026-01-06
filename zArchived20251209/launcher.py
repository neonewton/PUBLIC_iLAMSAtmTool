import sys
import subprocess
import os
import time
from pathlib import Path
import webbrowser
import socket

def wait_for_port(host="127.0.0.1", port=8501, timeout=15):
    """Wait until a TCP port is open"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False

def main():
    # Detect PyInstaller bundle
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    app_path = base_path / "Home.py"

    if not app_path.exists():
        raise FileNotFoundError(f"Home.py not found at {app_path}")

    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"

    # Start Streamlit server
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port=8501",
            "--browser.gatherUsageStats=false",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Wait for Streamlit to be ready
    if not wait_for_port():
        raise RuntimeError("Streamlit server did not start")

    # Open browser (cross-platform)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    main()
