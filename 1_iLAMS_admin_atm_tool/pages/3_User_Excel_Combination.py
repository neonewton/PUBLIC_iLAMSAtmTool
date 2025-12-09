# pages/3_User_Excel_Combination.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.excel_combine import combine_excels

st.title("Feature 3 – User Excel Combination")

st.markdown(
    """
Upload multiple Excel files and combine them into one consolidated sheet.
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

output_filename = st.text_input("Output file name", "combined_output.xlsx")

if st.button("Combine"):
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
