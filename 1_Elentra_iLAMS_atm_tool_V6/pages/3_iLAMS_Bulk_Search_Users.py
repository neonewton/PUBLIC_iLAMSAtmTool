import streamlit as st
import pandas as pd
from io import BytesIO
import re

from core.backend_main import run_user_search

st.title("iLAMS Bulk Search Users")

st.markdown(
    """
**Context:**  
Clinical Affairs Team (CA Team) pastes CE names or NTU email addresses
to automate user search in iLAMS Admin.
"""
)

st.markdown(
    """
**Prerequisite:**  
- Chrome is already open  
- Logged into iLAMS  
- Remote debugging enabled (`--remote-debugging-port=9222`)
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
with st.form("ce_user_search_form"):
    raw_text = st.text_area(
        "Paste CE name(s) or NTU email address(es) (one per line)",
        height=250,
        placeholder="e.g.\nTan Ah Kow\nlimweijie@ntu.edu.sg"
    )

    include_second_row = st.checkbox(
        "Include second result row (Row2) if found",
        value=True
    )

    submitted = st.form_submit_button("Run Bulk User Search")

# -------------------------
# On submit
# -------------------------
if submitted:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    if not lines:
        st.error("Please paste at least one name or email address.")
    else:
        validated_inputs = []
        invalid_inputs = []

        for item in lines:
            if "@" in item:
                if re.fullmatch(r"[A-Za-z0-9._%+-]+@ntu\.edu\.sg", item, re.IGNORECASE):
                    validated_inputs.append(item)
                else:
                    invalid_inputs.append(item)
            else:
                validated_inputs.append(item)

        if invalid_inputs:
            st.warning(
                "The following entries are invalid and will be skipped:\n\n"
                + "\n".join(f"- {x}" for x in invalid_inputs)
            )

        if not validated_inputs:
            st.error("No valid names or NTU email addresses found.")
        else:
            progress_bar = st.progress(0.0)
            collected_logs = []

            def log_callback(entry):
                collected_logs.append(entry)

            def progress_callback(current, total):
                if total > 0:
                    progress_bar.progress(min(current / total, 1.0))

            result = run_user_search(
                search_values=validated_inputs,
                include_second_row=include_second_row,
                log_callback=log_callback,
                progress_callback=progress_callback,
            )

            st.session_state["search_logs"] = collected_logs + result["logs"]
            st.session_state["search_df"] = result["dataframe"]

            st.success("User search completed.")

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

