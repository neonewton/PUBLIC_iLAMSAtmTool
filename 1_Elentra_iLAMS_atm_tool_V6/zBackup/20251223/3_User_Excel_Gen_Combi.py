# pages/2_User_Excel_Generation.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.backend_3_User_Excel_Gen_Combi import generate_user_excel,combine_excels

st.set_page_config(page_title="ExcelGen&Combi",page_icon="🦾")
st.title("iLAMS User Excel Generation & Combination")

st.subheader("User Excel Generation")

st.markdown(
    """
Paste email address below to generate user Excel sheet(s).

Each line must be:
`staff_username@ntu.edu.sg` or
`student_username@e.ntu.edu.sg`
"""
)

if "excel_gen_logs" not in st.session_state:
    st.session_state["excel_gen_logs"] = []
if "excel_gen_df" not in st.session_state:
    st.session_state["excel_gen_df"] = None

with st.form("excel_gen_form"):
    mode = st.radio("Mode", ["student", "staff"], index=0)
    course_name = st.text_input("Course Name / Identifier", "")
    raw_text = st.text_area("Paste email address(es) here", height=250)

    submitted = st.form_submit_button("Generate Excel Sheets")


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

st.markdown("---")

st.subheader("User Excel Combination")

st.markdown(
    """
Select folder containing the generated Excel Sheets and combine them into one consolidated sheet for ease uploading.
"""
)

if "combine_logs" not in st.session_state:
    st.session_state["combine_logs"] = []
if "combine_df" not in st.session_state:
    st.session_state["combine_df"] = None

uploaded_files = st.file_uploader(
    "Upload Excel files",
    type=["xls", "xlsx"],
    accept_multiple_files=True,
)

output_filename = st.text_input("Output file name:", "YYYYMMDD_HHMMSS_combined.xlsx")

if st.button("Combine Excels Sheet"):
    if not uploaded_files:
        st.error("Please upload at least one Excel file.")
    else:
        progress_bar = st.progress(0.0)
        collected_logs = []

        def log_callback(entry):
            collected_logs.append(entry)

        def progress_callback(current, total):
            if total > 0:
                progress_bar.progress(min(current / total, 1.0))

        # Pass file-like objects directly to core
        sources = [f for f in uploaded_files]

        result = combine_excels(
            sources=sources,
            output_path=output_filename,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        st.session_state["combine_logs"] = collected_logs + result["logs"]
        st.session_state["combine_df"] = result["dataframe"]

        st.success(f"Combination completed. Rows: {result['rows']}")

if st.session_state["combine_df"] is not None:
    df = st.session_state["combine_df"]
    st.subheader("Combined Preview")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Combined Excel",
        data=buffer,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if st.session_state["combine_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["combine_logs"])
    st.dataframe(df_logs, use_container_width=True)