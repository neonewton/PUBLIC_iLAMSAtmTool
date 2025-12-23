# Home.py

import streamlit as st
import pandas as pd

from core.config import get_config, set_config
from core.selenium_utils import check_selenium_environment
from core.selenium_utils import launch_chrome_with_debug

st.set_page_config(
    page_title="AutoToolConfig",
    page_icon="🦾",
    layout="centered",
)

st.title("Elentra & iLAMS Automation Tool Configuration")
st.caption("Version 6.0.0")

st.markdown(
    """
This app groups several automation tools used for Elentra and iLAMS:
Use the sidebar to access each feature:

- **iLAMS to Elentra URL Link Upload**  
- **User Excel Generation**  
- **User Excel Combination**  
- **iLAMS Search Users**  
- **iLAMS Bulk Courses Archive**

Use this page to run **pre-checks** before performing any Selenium task.

"""
)

st.markdown("---")

config = get_config()

st.subheader("Environment Configuration")

st.markdown(
    "Ensure you are logged into Chrome and have downloaded the Chrome WebDriver before executing.<br>"
    "Download here: <https://googlechromelabs.github.io/chrome-for-testing/>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
with col1:
    driver_path = st.text_input(
        "Chromedriver Path",
        value=config.driver_path,
    )
    debugger_address = st.text_input(
        "Debugger Address (host:port)",
        value=config.debugger_address,
    )

with col2:
    lams_base_url = st.text_input(
        "LAMS Base URL",
        value=config.lams_base_url or "",
        help="Example: https://ilams.lamsinternational.com/lams/index.do",
    )
    elentra_base_url = st.text_input(
        "Elentra Base URL",
        value=config.elentra_base_url or "",
        help="Example: https://ntu.elentra.cloud/",
    )

if st.button("Save Config"):
    set_config(
        driver_path=driver_path,
        debugger_address=debugger_address,
        lams_base_url=lams_base_url or None,
        elentra_base_url=elentra_base_url or None,
    )
    st.success("Configuration saved for this session.")




st.markdown("---")

st.subheader("Run Pre-checks")

if st.button("Run Pre-configuration checks"):
    st.write("Starting Selenium Pre-checks...")

    # 1️⃣ Try launching Chrome first (retry up to 3 times)
    chrome_ok = launch_chrome_with_debug(port=9222, retries=3)

    if not chrome_ok:
        st.error("❌ Unable to launch Chrome with remote debugging after 3 attempts.")
        st.session_state["precheck_ok"] = False
        st.session_state["precheck_logs"] = [{
            "timestamp": "",
            "feature": "PreChecks",
            "level": "ERROR",
            "message": "Chrome launch failed after 3 attempts."
        }]
    else:
        st.success("Chrome debugging session launched successfully.")

        # 2️⃣ Proceed with your existing environment checks
        cfg = get_config()
        ok, logs = check_selenium_environment(cfg)

        st.session_state["precheck_ok"] = ok
        st.session_state["precheck_logs"] = logs

        if ok:
            st.success("Pre-checks passed.")
        else:
            st.error("Pre-checks failed. Check logs below.")


status = st.session_state.get("precheck_ok", None)
logs = st.session_state.get("precheck_logs", [])

if status is None:
    st.info("Run pre-checks to see environment status.")
else:
    if status:
        st.success("Pre-checks passed.")
    else:
        st.error("Pre-checks failed. See details below.")

if logs:
    df_logs = pd.DataFrame(logs)
    st.subheader("Pre-check Logs")
    st.dataframe(df_logs, use_container_width=True)

st.markdown("---")
