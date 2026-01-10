# core/config.py

import os 
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import os

# def default_driver_path() -> str:
#     if os.name == "nt":  # Windows
#         return r"C:\WebDrivers\chromedriver-win64\chromedriver.exe"
#     else:  # macOS or Linux
#         return os.path.expanduser(
#             "~/WebDrivers/chromedriver-mac-arm64/chromedriver"
#         )

def default_driver_path() -> str:

    # Absolute path to this file (config.py / selenium_utils.py)
    base_dir = Path(__file__).resolve().parent.parent

    # If this file is inside /core, go one level up to project root
    project_root = base_dir.parent

    if os.name == "nt":  # Windows
        driver_path = project_root / "WebDrivers" / "chromedriver-win64" / "chromedriver.exe"
    else:  # macOS / Linux
        driver_path = project_root / "WebDrivers" / "chromedriver-mac-arm64" / "chromedriver"

    return str(driver_path)


@dataclass
class SeleniumConfig:
    driver_path: str = default_driver_path()
    debugger_address: str = "127.0.0.1:9222"
    lams_base_url: Optional[str] = "https://ilams.lamsinternational.com/lams/index.do"
    elentra_base_url: Optional[str] = "https://ntu.elentra.cloud/"

_config: SeleniumConfig = SeleniumConfig()

def get_config() -> SeleniumConfig:
    return _config

def set_config(
    driver_path: Optional[str] = None,
    debugger_address: Optional[str] = None,
    lams_base_url: Optional[str] = None,
    elentra_base_url: Optional[str] = None,
) -> SeleniumConfig:
    global _config
    if driver_path is not None:
        _config.driver_path = driver_path
    if debugger_address is not None:
        _config.debugger_address = debugger_address
    if lams_base_url is not None:
        _config.lams_base_url = lams_base_url
    if elentra_base_url is not None:
        _config.elentra_base_url = elentra_base_url
        
    return _config
