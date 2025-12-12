# pages/4_iLAMS_Search_Users.py

import streamlit as st
import pandas as pd
from io import BytesIO

from core.search_users import run_user_search

st.title("iLAMS Bulk Search Users")

st.markdown(
    """
Upload a CSV of users and search them in iLAMS via Selenium.

**Prerequisite:** Chrome is running with remote debugging enabled and logged into LAMS/iLAMS.
"""
)

if "search_logs" not in st.session_state:
    st.session_state["search_logs"] = []
if "search_df" not in st.session_state:
    st.session_state["search_df"] = None

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

include_second_row = st.checkbox("Include second result row (Row2), if found", value=True)

df_input = None
search_col = None

if uploaded_file:
    df_input = pd.read_csv(uploaded_file)
    st.subheader("Input Preview")
    st.dataframe(df_input.head(), use_container_width=True)

    columns = df_input.columns.tolist()
    if columns:
        search_col = st.selectbox("Column to use for search", columns, index=0)

if st.button("Run Search"):
    if df_input is None or search_col is None:
        st.error("Please upload a CSV and select a search column.")
    else:
        search_values = df_input[search_col].astype(str).tolist()
        progress_bar = st.progress(0.0)
        collected_logs = []

        def log_callback(entry):
            collected_logs.append(entry)

        def progress_callback(current, total):
            if total > 0:
                progress_bar.progress(min(current / total, 1.0))

        result = run_user_search(
            search_values=search_values,
            include_second_row=include_second_row,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        st.session_state["search_logs"] = collected_logs + result["logs"]
        st.session_state["search_df"] = result["dataframe"]

        st.success("User search completed.")

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
        file_name="search_results.csv",
        mime="text/csv",
    )

if st.session_state["search_logs"]:
    st.subheader("Logs")
    df_logs = pd.DataFrame(st.session_state["search_logs"])
    st.dataframe(df_logs, use_container_width=True)
