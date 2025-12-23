import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

from core.backend_3_Bulk_User_Excel_Gen import (
    generate_staff_package,
    generate_student_package,
    combine_excels,
)




# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="BulkUserExcelGen", page_icon="🦾")
st.title("iLAMS Bulk New User and Course Map Excel Generation")

# -------------------------------------------------
# Session state initialisation
# -------------------------------------------------
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "Staff"

if "pkg_zip" not in st.session_state:
    st.session_state.pkg_zip = None
if "pkg_name" not in st.session_state:
    st.session_state.pkg_name = None
if "pkg_audit" not in st.session_state:
    st.session_state.pkg_audit = None
if "pkg_logs" not in st.session_state:
    st.session_state.pkg_logs = []

# -------------------------------------------------
# Output Directory
# -------------------------------------------------

st.subheader("Output Location")

default_output_dir = str(Path.home() / "Downloads" / "iLAMS_Output")

output_dir = st.text_input(
    "Output folder (will be created if not exists)",
    value=default_output_dir,
    help="Local folder where generated ZIP files will be saved",
)

output_path = Path(output_dir)

if output_path.exists() and not output_path.is_dir():
    st.error("Output path exists but is not a directory.")
    st.stop()

# -------------------------------------------------
# Mode selection (OUTSIDE any form)
# -------------------------------------------------
st.subheader("Select User Type")

c1, c2 = st.columns(2)

if c1.button(
    "STAFFS / CEs",
    type="primary" if st.session_state.user_mode == "Staff" else "secondary",
    use_container_width=True,
):
    st.session_state.user_mode = "Staff"

if c2.button(
    "STUDENTS",
    type="primary" if st.session_state.user_mode == "Student" else "secondary",
    use_container_width=True,
):
    st.session_state.user_mode = "Student"

mode = st.session_state.user_mode

st.markdown("---")

# -------------------------------------------------
# Initialise variables (IMPORTANT for Pylance)
# -------------------------------------------------
department_name = ""
cohort_name = ""
full_name = ""
raw_emails = ""
raw_course_ids = ""
roles = []
is_y1 = False

# -------------------------------------------------
# Dynamic inputs (OUTSIDE form)
# -------------------------------------------------
if mode == "Staff":
    st.markdown("### Staff Inputs")

    department_name = st.text_input("Department Name")
    full_name = st.text_input("Full Name of User")
    raw_emails = st.text_area("Staff Email Addresses (one per line)")
    raw_course_ids = st.text_area("Course IDs (one per line)")
    roles = st.multiselect(
        "Roles",
        ["monitor", "author", "course manager"],default=["monitor"]
    )

elif mode == "Student":
    st.markdown("### Student Inputs")

    cohort_name = st.text_input("Cohort Name")
    full_name = st.text_input("Full Name of User")
    raw_emails = st.text_area("Student Email Addresses (one per line)")
    raw_course_ids = st.text_area("Course IDs (one per line)")
    is_y1 = st.checkbox("This is Y1 cohort", value=True)
    st.text_input("Roles", value="learner", disabled=False)

# -------------------------------------------------
# Action buttons (ONE form only)
# -------------------------------------------------
gen_new_users = False
gen_course_map = False
gen_combined_map = False

with st.form("action_form"):
    st.markdown("### Actions")

    gen_course_map = st.form_submit_button(
        "Generate Course Mapping XLS",
        type="primary",
        use_container_width=True,
    )

    if mode == "Staff":
        gen_new_users = st.form_submit_button(
            "Generate New Users XLS",
            type="primary",
            use_container_width=True,
        )
        gen_combined_map = st.form_submit_button(
            "Generate Combined Course Mapping XLS",
            type="primary",
            use_container_width=True,
        )

    if mode == "Student":
        gen_new_users = st.form_submit_button(
            "Generate Y1 Cohort New Users .xls",
            type="primary",
            use_container_width=True,
        )

        gen_combined_map = st.form_submit_button(
            "Generate Combined Course Mapping XLS",
            type="secondary",
            use_container_width=True,
        )

# -------------------------------------------------
# Run actions
# -------------------------------------------------
action_triggered = False
progress_bar = st.progress(0.0)
collected_logs = []

def log_callback(entry):
    collected_logs.append(entry)

def progress_callback(current, total):
    if total > 0:
        progress_bar.progress(min(current / total, 1.0))

try:
    if mode == "Staff" and (gen_new_users or gen_course_map or gen_combined_map):
        action_triggered = True

        pkg = generate_staff_package(
            department_name=department_name,
            full_name=full_name,
            raw_emails=raw_emails,
            raw_course_ids=raw_course_ids,
            selected_roles=roles,
            generate_new_users=gen_new_users,
            generate_course_map=gen_course_map,
            generate_combined_course_map=gen_combined_map,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        st.session_state.pkg_zip = pkg.zip_bytes
        st.session_state.pkg_name = pkg.zip_filename
        st.session_state.pkg_audit = pkg.audit_df
        st.session_state.pkg_logs = pkg.logs

    if mode == "Student" and (gen_new_users or gen_course_map):
        action_triggered = True

        pkg = generate_student_package(
            cohort_name=cohort_name,
            full_name=full_name,
            raw_emails=raw_emails,
            raw_course_ids=raw_course_ids,
            is_y1=is_y1,
            generate_y1_new_users=gen_y1_users,
            generate_course_map=gen_course_map,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        st.session_state.pkg_zip = pkg.zip_bytes
        st.session_state.pkg_name = pkg.zip_filename
        st.session_state.pkg_audit = pkg.audit_df
        st.session_state.pkg_logs = pkg.logs

except Exception as e:
    if action_triggered:
        st.error(str(e))

# -------------------------------------------------
# Outputs
# -------------------------------------------------
if action_triggered and st.session_state.pkg_zip:
    st.success("Generation completed. Download your ZIP below.")

if st.session_state.pkg_zip and st.session_state.pkg_name:
    st.download_button(
        label="Download ZIP Package",
        data=st.session_state.pkg_zip,
        file_name=st.session_state.pkg_name,
        mime="application/zip",
    )

if st.session_state.pkg_audit is not None:
    st.subheader("Audit / Files Generated")
    st.dataframe(st.session_state.pkg_audit, use_container_width=True)

if st.session_state.pkg_logs:
    st.subheader("Logs")
    st.dataframe(pd.DataFrame(st.session_state.pkg_logs), use_container_width=True)

# # -------------------------------------------------
# # Combine Excel utility (unchanged)
# # -------------------------------------------------
# st.markdown("---")
# st.subheader("Combine Excel Files (Optional)")

# uploaded_files = st.file_uploader(
#     "Upload Excel files to combine",
#     type=["xls", "xlsx"],
#     accept_multiple_files=True,
# )

# output_filename = st.text_input("Output file name:", "combined.xlsx")

# if st.button("Combine"):
#     if not uploaded_files:
#         st.error("Please upload at least one Excel file.")
#     else:
#         progress_bar2 = st.progress(0.0)
#         logs2 = []

#         def log_callback2(entry):
#             logs2.append(entry)

#         def progress_callback2(cur, tot):
#             if tot > 0:
#                 progress_bar2.progress(min(cur / tot, 1.0))

#         result = combine_excels(
#             sources=uploaded_files,
#             output_path=output_filename,
#             log_callback=log_callback2,
#             progress_callback=progress_callback2,
#         )

#         st.success(f"Combined rows: {result['rows']}")
#         df = result["dataframe"]
#         st.dataframe(df, use_container_width=True)

#         buffer = BytesIO()
#         df.to_excel(buffer, index=False)
#         buffer.seek(0)

#         st.download_button(
#             "Download Combined Excel",
#             data=buffer,
#             file_name=output_filename,
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )

#         st.subheader("Combine Logs")
#         st.dataframe(pd.DataFrame(result["logs"]), use_container_width=True)
