# pages/4_iLAMS_Bulk_Courses_Archive.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.backend_4_Bulk_Courses_Archive import run_bulk_course_archive

st.set_page_config(page_title="BulkArchive",page_icon="🦾")
st.title("iLAMS Bulk Courses Archive")

st.markdown(
    """
**Context:**  
For Annual Preparation, we will need to archive the courses so that the 
Data Analytics's Power BI can read the data from the daily iLAMS-bk's data dump 
via Denodo and Snowflake

**Warning:** This tool will archive multiple courses in iLAMS.

**Prerequisite:** 
- Python packages are installed
- Chrome & Chrome Webdriver are downloaded  
- Logged into iLAMS Admin via SSO

"""
)

if "archive_logs" not in st.session_state:
    st.session_state["archive_logs"] = []
if "archive_df" not in st.session_state:
    st.session_state["archive_df"] = None

excluded_text = st.text_area(
    "Excluded Course IDs (comma-separated)",
    value="104, 509, 610, 629, 630, 631, 632, 633, 634, 635, 636, 637",
)

dry_run = st.checkbox("Dry-run (simulate only, no changes saved)", value=True)
max_courses = st.number_input(
    "Max courses to process",
    min_value=1,
    max_value=2000,
    value=5,
    help="Safety cap to avoid accidentally processing too many courses at once.",
)

col1, col2, col3 = st.columns(3)

with col1:
    run_clicked = st.button("▶ Run / Resume")

with col2:
    pause_clicked = st.button("⏸ Pause")

with col3:
    stop_clicked = st.button("⛔ Stop")

if "archive_running" not in st.session_state:
    st.session_state.archive_running = False

if "archive_pause" not in st.session_state:
    st.session_state.archive_pause = False

if "archive_stop" not in st.session_state:
    st.session_state.archive_stop = False

if run_clicked:
    st.session_state.archive_running = True
    st.session_state.archive_pause = False
    st.session_state.archive_stop = False

if pause_clicked:
    st.session_state.archive_pause = True

if stop_clicked:
    st.session_state.archive_stop = True
    st.session_state.archive_running = False


if st.session_state.archive_running:
    st.success("▶ RUNNING")
    progress_bar = st.progress(0.0)
    collected_logs = []

    def log_callback(entry):
        collected_logs.append(entry)

    def progress_callback(current, total):
        if total > 0:
            progress_bar.progress(min(current / total, 1.0))

    result = run_bulk_course_archive(
        excluded_ids = [x.strip() for x in excluded_text.split(",") if x.strip()],
        dry_run=dry_run,
        max_courses=max_courses,
        log_callback=log_callback,
        progress_callback=progress_callback,
        pause_flag=lambda: st.session_state.archive_pause,
        stop_flag=lambda: st.session_state.archive_stop,
    )

    st.session_state.archive_logs.extend(collected_logs + result["logs"])
    st.session_state.archive_df = result["dataframe"]

    if st.session_state.archive_stop:
        st.warning("⛔ Bulk archive stopped by user.")
    elif st.session_state.archive_pause:
        st.info("⏸ Bulk archive paused.")
        st.warning("⏸ PAUSED")
    else:
        st.success("✅ Bulk Courses Archive completed.")

if st.session_state["archive_df"] is not None:
    df = st.session_state["archive_df"]
    st.subheader("Affected Courses Preview")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Audit CSV",
        data=buffer,
        file_name="bulk_archive_audit.csv",
        mime="text/csv",
    )

if st.session_state["archive_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["archive_logs"])
    st.dataframe(df_logs, use_container_width=True)
