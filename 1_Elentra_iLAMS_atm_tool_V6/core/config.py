# core/config.py

import os 
from dataclasses import dataclass
from typing import Optional

def default_driver_path() -> str:
    if os.name == "nt":   # Windows
        return r"C:\WebDrivers\chromedriver-win64\chromedriver.exe"
    else:                 # macOS or Linux
        return r"/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"

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
