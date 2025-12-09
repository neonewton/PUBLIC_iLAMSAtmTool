# pages/1_Elentra_Link_Upload.py

import streamlit as st
import pandas as pd

from core.elentra_link_upload import run_elentra_link_upload

st.title("Feature 1 – Elentra Link Upload")

st.markdown(
    """
Attach the appropriate iLAMS links to an Elentra Event.

**Prerequisite:** Chrome is running with remote debugging enabled and logged into Elentra.
"""
)

if "elentra_logs" not in st.session_state:
    st.session_state["elentra_logs"] = []

with st.form("elentra_upload_form"):
    event_id = st.text_input("Elentra Event ID", "")
    lams_lesson_id = st.text_input("LAMS Lesson ID", "")
    st.caption("Lesson ID is used to construct Admin/Staff/Student/Monitor URLs based on LAMS base URL.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        upload_admin = st.checkbox("Admin URL", value=True)
    with col2:
        upload_staff = st.checkbox("Staff URL", value=True)
    with col3:
        upload_student = st.checkbox("Student URL", value=True)
    with col4:
        upload_monitor = st.checkbox("Monitor URL", value=False)

    submitted = st.form_submit_button("Run Upload")

if submitted:
    if not event_id or not lams_lesson_id:
        st.error("Please fill in both Event ID and LAMS Lesson ID.")
    else:
        progress_bar = st.progress(0.0)
        collected_logs = []

        def log_callback(entry):
            collected_logs.append(entry)

        def progress_callback(current, total):
            if total > 0:
                progress_bar.progress(min(current / total, 1.0))

        logs = run_elentra_link_upload(
            event_id=event_id,
            lams_lesson_id=lams_lesson_id,
            upload_admin=upload_admin,
            upload_staff=upload_staff,
            upload_student=upload_student,
            upload_monitor=upload_monitor,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )
        collected_logs.extend(logs)
        st.session_state["elentra_logs"] = collected_logs
        st.success("Elentra upload run completed. See logs below.")

if st.session_state["elentra_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["elentra_logs"])
    st.dataframe(df_logs, use_container_width=True)
