# pages/1_Elentra_Link_Upload.py

import streamlit as st
import pandas as pd

from core.backend_main import run_elentra_link_upload

st.title("iLAMS to Elentra Lesson Link Upload")

st.markdown(
    """
Automated iLAMS-to-Elentra Link Upload

**Prerequisite:** Chrome is running with remote debugging enabled and logged into Elentra.
"""
)

# --- Safe defaults ---
if "elentra_logs" not in st.session_state:
    st.session_state["elentra_logs"] = []
if "upload_running" not in st.session_state:
    st.session_state["upload_running"] = False
if "stop_requested" not in st.session_state:
    st.session_state["stop_requested"] = False



# ---------------------------------------------------------
# 🧾 MAIN FORM (all inputs + both buttons live inside)
# ---------------------------------------------------------
with st.form("elentra_upload_form"):

    # -------------------------------
    # Input fields
    # -------------------------------
    lams_lesson_title = st.text_input("Lesson Title", "(RPA test)FM_MiniQuiz_WomanHealth_DDMMYY")
    lams_lesson_id = st.text_input("LAMS Lesson ID", "37655")
    elentra_event_id = st.text_input("Elentra Event ID", "1696")

    upload_monitor = st.checkbox("Upload Monitor URL", value=True)
    st.caption("Monitor Base URL : https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID=")

    upload_student = st.checkbox("Upload Student URL", value=True)
    st.caption("Student Base URL : https://ilams.lamsinternational.com/lams/home/learner.do?lessonID=")

    # -------------------------------
    # Buttons inside the same form
    # -------------------------------
    col_run, col_stop = st.columns(2)
    with col_run:
        submitted = st.form_submit_button("Run Upload")
    with col_stop:
        stopped = st.form_submit_button("Stop Upload")

        if stopped:
            st.session_state["upload_running"] = False
            st.session_state["stop_requested"] = True
            st.warning("Stop requested. Selenium will halt at the next safe checkpoint.")


    # -------------------------------------------------
    # STOP BUTTON HANDLING (does not trigger upload)
    # -------------------------------------------------
    if stopped:
        st.session_state["upload_running"] = False
        st.session_state["stop_requested"] = True
        st.warning("Stop requested. Selenium will halt at the next safe checkpoint.")


    # -------------------------------------------------
    # RUN BUTTON HANDLING (the actual automation)
    # -------------------------------------------------
    if submitted:
        st.session_state["elentra_logs"] = []
        st.session_state["upload_running"] = True
        st.session_state["stop_requested"] = False    # reset stop flag
        collected_logs = []

        if not elentra_event_id or not lams_lesson_id:
            st.error("Please fill in both Event ID and LAMS Lesson ID.")
            st.session_state["upload_running"] = False
            

        else:
            progress_bar = st.progress(0.0)

            # Log callback
            def log_callback(entry):
                collected_logs.append(entry)

            # Progress callback
            def progress_callback(current, total):
                if total > 0:
                    progress_bar.progress(min(current / total, 1.0))

            # Run Selenium automation
            logs = run_elentra_link_upload(
                lams_lesson_title=lams_lesson_title,
                elentra_event_id=elentra_event_id,
                lams_lesson_id=lams_lesson_id,
                upload_student=upload_student,
                upload_monitor=upload_monitor,
                log_callback=log_callback,
                progress_callback=progress_callback,
            )

            collected_logs.extend(logs)
            st.session_state["elentra_logs"] = collected_logs
            st.session_state["upload_running"] = False

            st.success("Elentra upload run completed. See logs below.")


# ---------------------------------------------------------
# LOG DISPLAY (outside form: persists across reruns)
# ---------------------------------------------------------
if st.session_state["elentra_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["elentra_logs"])
    st.dataframe(df_logs, use_container_width=True)
