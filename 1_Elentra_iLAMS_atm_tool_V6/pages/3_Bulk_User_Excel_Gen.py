import streamlit as st
import pandas as pd

from core.backend_3_Bulk_User_Excel_Gen import (
    generate_staff_package,
    generate_student_package,
)

from pathlib import Path


def parse_course_ids(raw: str) -> tuple[list[int], list[str]]:
    valid_ids = []
    invalid_ids = []

    for line in raw.splitlines():
        value = line.strip()
        if not value:
            continue
        if value.isdigit():
            valid_ids.append(int(value))
        else:
            invalid_ids.append(value)

    return valid_ids, invalid_ids


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="BulkExcelGen", page_icon="🦾")
st.title("iLAMS Bulk New User and Course Map Excel Generation")

# -------------------------------------------------
# Session state initialisation
# -------------------------------------------------

if "pkg_zip" not in st.session_state:
    st.session_state.pkg_zip = None
if "pkg_name" not in st.session_state:
    st.session_state.pkg_name = None
if "pkg_audit" not in st.session_state:
    st.session_state.pkg_audit = None
if "pkg_logs" not in st.session_state:
    st.session_state.pkg_logs = []

# -------------------------------------------------
# Mode selection (OUTSIDE any form)
# -------------------------------------------------
st.subheader("Select User Type")

if "user_mode" not in st.session_state:
    st.session_state.user_mode = "Staff"

def set_mode_staff():
    st.session_state.user_mode = "Staff"

def set_mode_student():
    st.session_state.user_mode = "Student"

c1, c2 = st.columns(2)

c1.button(
    "STAFFS / CEs",
    type="primary" if st.session_state.user_mode == "Staff" else "secondary",
    width='stretch',
    on_click=set_mode_staff,
)

c2.button(
    "STUDENTS",
    type="primary" if st.session_state.user_mode == "Student" else "secondary",
    width='stretch',
    on_click=set_mode_student,
)

mode = st.session_state.user_mode

st.markdown("---")

# -------------------------------------------------
# Initialise variables (prevents Pylance undefined warnings)
# -------------------------------------------------
department_name = ""
cohort_name = ""
full_name = ""
raw_emails = ""
raw_course_ids = ""
roles = ["monitor"]  # default for staff

# -------------------------------------------------
# Dynamic inputs (OUTSIDE form so UI updates immediately)
# -------------------------------------------------
if mode == "Staff":
    st.markdown("### Staff Inputs")
    department_name = st.text_input("Department Name",value="DL")
    raw_names = st.text_area("Full Names (one per line, match email order)", help="Each line must correspond to the email in the same row.", value="Nelton Tan \nlkc-dl-lams")
    raw_emails = st.text_area("Staff Email Addresses (one per line)",value="nelton.tan@ntu.edu.sg \nlkc-dl-lams@ntu.edu.sg")
    raw_course_ids = st.text_area(
    "Course IDs (one per line, integers only)",
    help="Each line must be a numeric course ID, e.g. 104",value="104 \n650")
    roles = st.multiselect(
        "Roles",
        ["monitor", "author", "course manager","learner"],
        default=["monitor"],
    )

elif mode == "Student":
    st.markdown("### Student Inputs")
    cohort_name = st.text_input("Cohort Name",value="Cohort2026Y1")
    raw_names = st.text_area("Full Names (one per line, match email order)", help="Each line must correspond to the email in the same row.", value="Nelton Tan Student \nlkc-dl-lams-student")
    raw_emails = st.text_area("Student Email Addresses (one per line)", value="nelton.tan@e.ntu.edu.sg \nlkc-dl-lams-student@e.ntu.edu.sg")
    raw_course_ids = st.text_area(
    "Course IDs (one per line, integers only)",
    help="Each line must be a numeric course ID, e.g. 104", value="104 \n650")
    roles = st.multiselect(
        "Roles",
        ["monitor", "author", "course manager","learner"],
        default=["learner"],
    )

full_names = [x.strip() for x in raw_names.splitlines() if x.strip()]

# -------------------------------------------------
# Action buttons (ONE form only)
# -------------------------------------------------
gen_course_map = False
gen_new_users = False

with st.form("action_form"):
    st.markdown("Actions to Perform")

    if mode == "Staff":
        gen_new_users = st.checkbox(
            "📝 Generate New Users .xls",
            value=False
        )

        gen_course_map = st.checkbox(
            "🗺️ Generate Course Mapping .xls",
            value=True,   # sensible default
        )

    if mode == "Student":
        gen_new_users = st.checkbox(
            "✨ Generate Y1 Cohort New Users .xls",
            value=False
        )
        gen_course_map = st.checkbox(
            "🗺️ Generate Course Mapping .xls",
            value=True,   # sensible default
        )

    run_generation = st.form_submit_button(
        "🔍 Check Package",
        type="primary",
        use_container_width=True,
    )
    
    button_label = (
    "⬇️ Download ZIP Package"
    if st.session_state.pkg_zip
    else "🔍 Generate Package"
    )

collected_logs = []

def log_callback(entry):
    collected_logs.append(entry)

if run_generation:
    try:
        course_ids, invalid_course_ids = parse_course_ids(raw_course_ids)

        if invalid_course_ids:
            st.error(
                "Invalid Course IDs detected (must be integers only):\n"
                + ", ".join(invalid_course_ids)
            )
            st.stop()

        if mode == "Staff" and (gen_new_users or gen_course_map):

            pkg = generate_staff_package(
                department_name=department_name,
                full_names=full_names,
                raw_emails=raw_emails,
                raw_course_ids=raw_course_ids,
                selected_roles=roles,
                generate_new_users=gen_new_users,
                generate_course_map=gen_course_map,
                log_callback=log_callback,
            )

        elif mode == "Student" and (gen_new_users or gen_course_map):

            pkg = generate_student_package(
                cohort_name=cohort_name,
                full_names=full_names,
                raw_emails=raw_emails,
                raw_course_ids=raw_course_ids,
                generate_y1_new_users=gen_new_users,
                generate_course_map=gen_course_map,
                log_callback=log_callback,
            )

        else:
            st.warning("Please select at least one action.")
            st.stop()

        st.session_state.pkg_zip = pkg.zip_bytes
        st.session_state.pkg_name = pkg.zip_filename
        st.session_state.pkg_audit = pkg.audit_df
        st.session_state.pkg_logs = pkg.logs

        st.success("Package generated. Download below.")

    except Exception as e:
        st.error(str(e))

st.markdown("### Download")

if st.session_state.pkg_zip:
    st.download_button(
        "⬇️ Download ZIP Package",
        data=st.session_state.pkg_zip,
        file_name=st.session_state.pkg_name,
        mime="application/zip",
        use_container_width=True,
    )
else:
    st.button(
        "⬇️ Download ZIP Package",
        disabled=True,
        use_container_width=True,
    )

