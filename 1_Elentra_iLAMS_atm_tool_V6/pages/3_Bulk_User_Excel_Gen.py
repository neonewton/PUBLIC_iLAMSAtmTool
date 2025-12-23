import streamlit as st
import pandas as pd

from core.backend_3_Bulk_User_Excel_Gen import (
    generate_staff_package,
    generate_student_package,
)

st.set_page_config(page_title="User Excel Generator", page_icon="🦾")
st.title("iLAMS User & Course Mapping Generator")

# -----------------------------
# Session state
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "Staff"
if "pkg" not in st.session_state:
    st.session_state.pkg = None

# -----------------------------
# Mode selection
# -----------------------------
c1, c2 = st.columns(2)
if c1.button("🧑‍🏫 Staff", type="primary" if st.session_state.mode == "Staff" else "secondary"):
    st.session_state.mode = "Staff"
if c2.button("🧑‍🎓 Student", type="primary" if st.session_state.mode == "Student" else "secondary"):
    st.session_state.mode = "Student"

mode = st.session_state.mode
st.markdown("---")

# -----------------------------
# Defaults (important)
# -----------------------------
department = ""
cohort = ""
full_name = ""
raw_emails = ""
raw_course_ids = ""
roles = ["monitor"]
is_y1 = True

# -----------------------------
# Inputs (OUTSIDE form)
# -----------------------------
if mode == "Staff":
    department = st.text_input("Department Name")
    full_name = st.text_input("Full Name of User")
    raw_emails = st.text_area("Staff Email Addresses (one per line)")
    raw_course_ids = st.text_area("Course IDs (one per line)")
    roles = st.multiselect(
        "Roles",
        ["monitor", "author", "course manager"],
        default=["monitor"],
    )

else:
    cohort = st.text_input("Cohort Name")
    full_name = st.text_input("Full Name of User")
    raw_emails = st.text_area("Student Email Addresses (one per line)")
    raw_course_ids = st.text_area("Course IDs (one per line)")
    is_y1 = st.checkbox("Y1 Cohort", value=True)
    st.text_input("Roles", value="learner", disabled=True)

# -----------------------------
# Actions (ONE form)
# -----------------------------
with st.form("actions"):
    gen_course_map = st.form_submit_button("Generate Course Mapping XLS", type="primary")
    gen_new_users = st.form_submit_button("Generate New Users XLS", type="primary")

# -----------------------------
# Execute
# -----------------------------
if gen_course_map or gen_new_users:
    if mode == "Staff":
        st.session_state.pkg = generate_staff_package(
            department_name=department,
            full_name=full_name,
            raw_emails=raw_emails,
            raw_course_ids=raw_course_ids,
            selected_roles=roles,
            generate_new_users=gen_new_users,
            generate_course_map=gen_course_map,
            generate_combined_course_map=False,
        )
    else:
        st.session_state.pkg = generate_student_package(
            cohort_name=cohort,
            full_name=full_name,
            raw_emails=raw_emails,
            raw_course_ids=raw_course_ids,
            is_y1=is_y1,
            generate_y1_new_users=gen_new_users,
            generate_course_map=gen_course_map,
        )

# -----------------------------
# Output
# -----------------------------
pkg = st.session_state.pkg
if pkg:
    st.success("Package generated")
    st.download_button(
        "⬇️ Download ZIP",
        data=pkg.zip_bytes,
        file_name=pkg.zip_filename,
        mime="application/zip",
    )
    st.dataframe(pkg.audit_df, use_container_width=True)
    st.dataframe(pd.DataFrame(pkg.logs), use_container_width=True)
