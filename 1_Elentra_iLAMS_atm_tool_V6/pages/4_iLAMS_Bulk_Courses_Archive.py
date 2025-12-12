# pages/5_iLAMS_Bulk_Courses_Archive.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.bulk_course_archive import run_bulk_course_archive

st.title("iLAMS Bulk Courses Archive")

st.markdown(
    """
**Warning:** This tool will archive multiple courses in iLAMS.

**Prerequisite:** Chrome is running with remote debugging enabled and logged into LAMS/iLAMS.
"""
)

if "archive_logs" not in st.session_state:
    st.session_state["archive_logs"] = []
if "archive_df" not in st.session_state:
    st.session_state["archive_df"] = None

excluded_text = st.text_area(
    "Excluded Course IDs (comma-separated)",
    value="",
    help="Example: 104, COURSE_123, 578",
)

dry_run = st.checkbox("Dry-run (simulate only, no changes saved)", value=True)
max_courses = st.number_input(
    "Max courses to process",
    min_value=1,
    max_value=2000,
    value=50,
    help="Safety cap to avoid accidentally processing too many courses at once.",
)

if st.button("Run Bulk Archive"):
    excluded_ids = [x.strip() for x in excluded_text.split(",") if x.strip()]

    progress_bar = st.progress(0.0)
    collected_logs = []

    def log_callback(entry):
        collected_logs.append(entry)

    def progress_callback(current, total):
        if total > 0:
            progress_bar.progress(min(current / total, 1.0))

    result = run_bulk_course_archive(
        excluded_ids=excluded_ids,
        dry_run=dry_run,
        max_courses=max_courses,
        log_callback=log_callback,
        progress_callback=progress_callback,
    )

    st.session_state["archive_logs"] = collected_logs + result["logs"]
    st.session_state["archive_df"] = result["dataframe"]

    st.success("Bulk archive run completed. See affected courses and logs below.")

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
