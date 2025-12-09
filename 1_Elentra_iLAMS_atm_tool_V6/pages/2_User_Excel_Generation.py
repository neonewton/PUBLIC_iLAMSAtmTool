# pages/2_User_Excel_Generation.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.excel_generation import generate_user_excel

st.title("Feature 2 – User Excel Generation")

st.markdown(
    """
Paste email / user data below and generate an Excel template.

Each line can be:
- `Name Surname <email@domain>`  
- `Name Surname - email@domain`  
- `email@domain`
"""
)

if "excel_gen_logs" not in st.session_state:
    st.session_state["excel_gen_logs"] = []
if "excel_gen_df" not in st.session_state:
    st.session_state["excel_gen_df"] = None

with st.form("excel_gen_form"):
    mode = st.radio("Mode", ["student", "staff"], index=0)
    course_name = st.text_input("Course Name / Identifier", "")
    raw_text = st.text_area("Paste email / user text here", height=250)

    submitted = st.form_submit_button("Generate")

if submitted:
    if not raw_text.strip():
        st.error("Please paste some input text.")
    else:
        progress_bar = st.progress(0.0)
        collected_logs = []

        def log_callback(entry):
            collected_logs.append(entry)

        def progress_callback(current, total):
            if total > 0:
                progress_bar.progress(min(current / total, 1.0))

        # We will save to in-memory BytesIO instead of disk; but we still need a path for logging.
        output_path = "users_output.xlsx"

        result = generate_user_excel(
            raw_text=raw_text,
            mode=mode,
            course_name=course_name,
            output_path=output_path,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        st.session_state["excel_gen_logs"] = collected_logs + result["logs"]
        st.session_state["excel_gen_df"] = result["dataframe"]

        st.success(f"Generated {result['rows']} rows. You can preview or download below.")

if st.session_state["excel_gen_df"] is not None:
    df = st.session_state["excel_gen_df"]
    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)

    # Offer download as Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Excel",
        data=buffer,
        file_name="users_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if st.session_state["excel_gen_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["excel_gen_logs"])
    st.dataframe(df_logs, use_container_width=True)
