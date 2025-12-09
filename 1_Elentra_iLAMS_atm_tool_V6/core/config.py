# core/config.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class SeleniumConfig:
    driver_path: str = "C:/path/to/chromedriver.exe"  # TODO: adjust default
    debugger_address: str = "127.0.0.1:9222"
    lams_base_url: Optional[str] = None   # e.g. "https://lams.example.com/lams"
    elentra_base_url: Optional[str] = None  # e.g. "https://elentra.example.com"

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
