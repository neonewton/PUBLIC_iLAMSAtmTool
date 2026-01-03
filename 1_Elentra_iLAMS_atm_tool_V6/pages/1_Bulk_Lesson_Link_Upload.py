# pages/1_Elentra_Link_Upload.py

import streamlit as st
import pandas as pd

from core.backend_1_Lesson_Link_Upload import run_elentra_link_upload

st.set_page_config(page_title="LinkUpload",page_icon="🦾")
st.title("iLAMS to Elentra Lesson Link Upload")

st.markdown(
"""
This tool uploads iLAMS lesson links (Monitor & Student) to Elentra events in bulk.

**Prerequisite:** 
- Python packages are installed
- Chrome & Chrome Webdriver are downloaded  
- Logged into iLAMS Admin via SSO
""")

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
    st.markdown("🌟Must match count of Lesson titles, Lesson IDs and Event IDs.🌟")

    lams_lesson_titles_raw = st.text_area(
        "Lesson Title(s)",
        help="Enter one per line or comma-separated.e.g. FOM TBL01 DDMMYY 2025Y1",
        value="(RPA test)FM_MiniQuiz_WomanHealth_DDMMYY\n(RPA test)FM_MiniQuiz_WomanHealth_DDMMYY",
    )
    
    lams_lesson_ids_raw = st.text_area(
        "LAMS Lesson ID(s)",
        help="Enter one per line or comma-separated. e.g. 40357",
        value="37655\n37655",
    )

    elentra_event_ids_raw = st.text_area(
        "Elentra Event ID(s)",
        help="Enter one per line or comma-separated. e.g. 1696",
        value="1696\n1696",
    )

    st.markdown("---")

    upload_monitor = st.checkbox("Upload Monitor URL", value=True)
    st.caption("Monitor Base URL : https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID=")

    upload_student = st.checkbox("Upload Student URL", value=True)
    st.caption("Student Base URL : https://ilams.lamsinternational.com/lams/home/learner.do?lessonID=")

    st.markdown("Elentra URL")
    st.caption("Elentra Base URL : https://ntu.elentra.cloud/events?id=")
    st.markdown("---")

    # -------------------------------
    # Buttons inside the same form
    # -------------------------------
    col_run, col_stop = st.columns(2)
    with col_run:
        submitted = st.form_submit_button("▶ Run Upload",type="primary",width="stretch")
    with col_stop:
        stopped = st.form_submit_button("⛔ Stop Upload",type="secondary",width="stretch")

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

        progress_bar = st.progress(0.0)

        # Log callback
        def log_callback(entry):
            if isinstance(entry, dict):
                collected_logs.append(entry)
            else:
                collected_logs.append({
                    "time": "",
                    "module": "ElentraUpload",
                    "level": "INFO",
                    "message": str(entry),
                })

        # Progress callback
        def progress_callback(current, total):
            if total > 0:
                progress_bar.progress(min(current / total, 1.0))

        # Run Selenium automation
        logs = run_elentra_link_upload(
            lams_lesson_titles_raw = lams_lesson_titles_raw,
            lams_lesson_ids_raw = lams_lesson_ids_raw,
            elentra_event_ids_raw = elentra_event_ids_raw,
            upload_student = upload_student,
            upload_monitor = upload_monitor,
            log_callback = log_callback,
            progress_callback = progress_callback,
        )

        st.session_state["elentra_logs"] = collected_logs
        st.session_state["upload_running"] = False

        st.success("Elentra upload run completed. See logs below.")


# ---------------------------------------------------------
# LOG DISPLAY (outside form: persists across reruns)
# ---------------------------------------------------------
if st.session_state["elentra_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["elentra_logs"])
    st.dataframe(df_logs, width='stretch')
