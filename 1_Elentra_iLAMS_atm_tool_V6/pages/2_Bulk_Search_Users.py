import streamlit as st
import pandas as pd
from io import BytesIO
import re


from core.backend_2_Bulk_Search_Users import run_user_search

st.set_page_config(page_title="BulkSearch",page_icon="🦾")
st.title("iLAMS Bulk Search Users")

st.markdown(
    """
**Context:**  
Clinical Affairs Team (CA Team) pastes CE names or NTU email addresses
to automate user search in iLAMS Admin.

Upload a list of users to automate the search in iLAMS admin.

**Prerequisite:** 
- Python packages are installed
- Chrome & Chrome Webdriver are downloaded  
- Logged into iLAMS Admin via SSO
"""
)

# -------------------------
# Session state
# -------------------------
if "search_logs" not in st.session_state:
    st.session_state["search_logs"] = []
if "search_df" not in st.session_state:
    st.session_state["search_df"] = None

# -------------------------
# Input form
# -------------------------
st.subheader("Input")

raw_text = st.text_area(
    "Paste CE name(s) or email address(es) (one per line)",
    height=250,
    value="e.g.\nlkc-dl-lams (TTSH)\ntimothy.koh@ntu.edu.sg"
)

# -------------------------
# On submit
# -------------------------
col1, col2 = st.columns(2)

with col1:
    run_clicked = st.button("▶ Run / Resume",type="primary",width="stretch")

with col2:
    stop_clicked = st.button("⛔ Stop",type="secondary",width="stretch")

if "usersearch_running" not in st.session_state:
    st.session_state.usersearch_running = False

if "usersearch_stop" not in st.session_state:
    st.session_state.usersearch_stop = False

if run_clicked:
    st.session_state.usersearch_running = True
    st.session_state.usersearch_stop = False

if stop_clicked:
    st.session_state.usersearch_stop = True
    st.session_state.usersearch_running = False

if st.session_state.usersearch_running:
    st.success("▶ RUNNING")

    progress_bar = st.progress(0.0)
    collected_logs = []

    def log_callback(entry):
        collected_logs.append(entry)

    def progress_callback(current, total):
        if total > 0:
            progress_bar.progress(min(current / total, 1.0))

    # Split pasted text into lines
    search_values = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    result = run_user_search(
        search_values=search_values,   # ✅ now a LIST
        log_callback=log_callback,
        progress_callback=progress_callback,
        stop_flag=lambda: st.session_state.usersearch_stop,
    )


    st.session_state.search_logs.extend(collected_logs + result["logs"])
    st.session_state.search_df = result["dataframe"]

    if st.session_state.usersearch_stop:
        st.warning("⛔ User search stopped by user.")
    else:
        st.success("✅ User search completed.")

    st.session_state.usersearch_running = False


# -------------------------
# Results
# -------------------------
if st.session_state["search_df"] is not None:
    df = st.session_state["search_df"]

    st.subheader("Search Results Preview")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Results CSV",
        data=buffer,
        file_name="ilams_user_search_results.csv",
        mime="text/csv",
    )

# -------------------------
# Logs
# -------------------------
if st.session_state["search_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["search_logs"])
    st.dataframe(df_logs, use_container_width=True)

