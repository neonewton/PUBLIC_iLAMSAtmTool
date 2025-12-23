import re
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
)

# =========================
# Template paths
# Put your .xls templates here (recommended):
#   <project_root>/templates/lams_users_template.xls
#   <project_root>/templates/lams_roles_template.xls
# =========================

# =========================
# HARD-CODED LAMS SCHEMAS
# =========================

USERS_COLUMNS = [
    "* login",
    "* password",
    "title",
    "* first_name",
    "* last_name",
    "authentication_method_id",
    "* email",
    "theme_id",
    "locale_id",
    "address_1",
    "address_2",
    "address_3",
    "city",
    "state",
    "postcode",
    "country",
    "day_phone",
    "evening_phone",
    "mobile_phone",
    "time_zone",
]

ROLES_COLUMNS = [
    "* login",
    "* organisation",
    "* roles",
    "* add to lessons [yes/no]",
]


# Required email domains

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z0-9\-]+$")

DEFAULT_PASSWORD = "Nanyang!23"
DEFAULT_COUNTRY = "Australia"
DEFAULT_ADD_TO_LESSONS = "yes"
DEFAULT_STUDENT_ROLE = "learner"

STAFF_ALLOWED_ROLES = ["monitor", "author", "course manager"]


@dataclass
class GeneratedPackage:
    """Represents a ZIP package (bytes) + preview/audit tables + logs."""
    zip_bytes: bytes
    zip_filename: str
    audit_df: pd.DataFrame
    logs: List[Dict]


def _now_yyyymmdd() -> str:
    return datetime.now().strftime("%Y%m%d")


def _clean_lines(raw: str) -> List[str]:
    return [x.strip() for x in (raw or "").splitlines() if x.strip()]


def _extract_email(line: str) -> str:
    """
    Accepts:
      - plain email
      - "Name <email@...>"
    Returns email or "".
    """
    line = line.strip()
    m = re.search(r"([a-zA-Z0-9_.+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z0-9\-]+)", line)
    return m.group(1).strip() if m else ""


def _validate_email(email: str, mode: str) -> Tuple[bool, str]:
    if not email:
        return False, "Email is empty."

    if not EMAIL_REGEX.match(email):
        return False, "Email format invalid."

    if mode == "staff":
        if not email.endswith("@ntu.edu.sg"):
            return False, "Staff email must end with @ntu.edu.sg."

    elif mode == "student":
        if not email.endswith("@e.ntu.edu.sg"):
            return False, "Student email must end with @e.ntu.edu.sg."

    else:
        return False, f"Unknown validation mode: {mode}"

    return True, ""



def _username_from_email(email: str) -> str:
    return email.split("@")[0].strip()


def _make_roles_df(rows: list[dict]) -> pd.DataFrame:
    formatted = []
    for r in rows:
        formatted.append({
            "* login": r["login"],
            "* organisation": r["organisation"],
            "* roles": r["roles"],
            "* add to lessons [yes/no]": "yes",
        })

    return pd.DataFrame(formatted, columns=ROLES_COLUMNS)


def _make_users_df(emails: list[str], full_name: str) -> pd.DataFrame:
    rows = []
    for email in emails:
        rows.append({
            "* login": email,
            "* password": "Nanyang!23",
            "title": "",
            "* first_name": full_name,
            "* last_name": ".",
            "authentication_method_id": "",
            "* email": email,
            "theme_id": "",
            "locale_id": "",
            "address_1": "",
            "address_2": "",
            "address_3": "",
            "city": "",
            "state": "",
            "postcode": "",
            "country": "Australia",
            "day_phone": "",
            "evening_phone": "",
            "mobile_phone": "",
            "time_zone": "",
        })

    return pd.DataFrame(rows, columns=USERS_COLUMNS)


def _df_to_xls_bytes(df: pd.DataFrame) -> bytes:
    """
    Create an Excel file in-memory.
    We output .xlsx (more reliable in python), but name can still be .xls if you insist.
    If you truly need .xls, we can switch to xlwt, but .xlsx is safer.
    """
    bio = BytesIO()
    df.to_excel(bio, index=False)
    bio.seek(0)
    return bio.read()


def _write_zip_structure(files: List[Tuple[str, bytes]]) -> bytes:
    """
    files: list of (zip_path, file_bytes)
    """
    import zipfile

    bio = BytesIO()
    with zipfile.ZipFile(bio, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for zip_path, b in files:
            zf.writestr(zip_path, b)
    bio.seek(0)
    return bio.read()


# =========================================================
# Public API (called by Streamlit page)
# =========================================================

def generate_staff_package(
    department_name: str,
    full_name: str,
    raw_emails: str,
    raw_course_ids: str,
    selected_roles: List[str],
    generate_new_users: bool,
    generate_course_map: bool,
    generate_combined_course_map: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> GeneratedPackage:
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("StaffExcelGen", msg, level)
        logs.append(entry)
        log_callback(entry)

    dept = (department_name or "").strip()
    if not dept:
        raise ValueError("Department Name is required.")

    full_name = (full_name or "").strip()
    if not full_name:
        raise ValueError("Full Name of user is required.")

    emails_raw = _clean_lines(raw_emails)
    emails = []
    email_errors = []
    for line in emails_raw:
        e = _extract_email(line)
        ok, reason = _validate_email(e, mode="staff")
        if ok:
            emails.append(e)
        else:
            email_errors.append(f"{line} -> {reason}")

    if not emails:
        raise ValueError("No valid staff email addresses found.")

    course_ids = [x.strip() for x in _clean_lines(raw_course_ids)]
    if not course_ids and (generate_course_map or generate_combined_course_map):
        raise ValueError("Course ID is required for course mapping outputs.")

    roles = [r.strip().lower() for r in (selected_roles or []) if r.strip()]
    invalid_roles = [r for r in roles if r not in STAFF_ALLOWED_ROLES]
    if invalid_roles:
        raise ValueError(f"Invalid staff roles: {invalid_roles}. Allowed: {STAFF_ALLOWED_ROLES}")

    if (generate_course_map or generate_combined_course_map) and not roles:
        raise ValueError("Please select at least one Staff role for course mapping.")

    ymd = _now_yyyymmdd()
    n_users = len(emails)

    parent = f"StaffCEs_{dept}_{ymd}_{n_users}users"
    files: List[Tuple[str, bytes]] = []

    audit_rows: List[Dict[str, str]] = []

    total_steps = max(n_users, 1)
    progress_callback(0, total_steps)

    # 1) New users per email (1_NewCreationList)
    if generate_new_users:
        for idx, email in enumerate(emails, start=1):
            progress_callback(idx, total_steps)
            username = _username_from_email(email)

            df_users = _make_users_df([email], full_name)
            xls_bytes = _df_to_xls_bytes(df_users)

            zip_path = f"{parent}/1_NewCreationList/NewUsers_{dept}_{username}_{ymd}.xlsx"
            files.append((zip_path, xls_bytes))

            audit_rows.append({
                "type": "staff_new_users",
                "email": email,
                "username": username,
                "department": dept,
                "file": zip_path,
            })

        log(f"Generated {n_users} Staff New Users files.", "info")

    # 2) Course mapping per email (2_IndivUsers)
    if generate_course_map:
        for idx, email in enumerate(emails, start=1):
            progress_callback(idx, total_steps)
            username = _username_from_email(email)

            rows = []
            for cid in course_ids:
                for role in roles:
                    rows.append({"login": email, "organisation": cid, "roles": role})

            df_roles = _make_roles_df(rows)
            xls_bytes = _df_to_xls_bytes(df_roles)

            zip_path = f"{parent}/2_IndivUsers/CourseMap_{dept}_{username}_{ymd}.xlsx"
            files.append((zip_path, xls_bytes))

            audit_rows.append({
                "type": "staff_course_map_individual",
                "email": email,
                "username": username,
                "department": dept,
                "courses": ", ".join(course_ids),
                "roles": ", ".join(roles),
                "file": zip_path,
            })

        log(f"Generated {n_users} Staff Individual CourseMap files.", "info")

    # 3) Combined course mapping for all emails (3_CombiUsers)
    if generate_combined_course_map:
        combined_rows = []
        for email in emails:
            for cid in course_ids:
                for role in roles:
                    combined_rows.append({"login": email, "organisation": cid, "roles": role})

        df_roles = _make_roles_df(combined_rows)
        xls_bytes = _df_to_xls_bytes(df_roles)

        zip_path = f"{parent}/3_CombiUsers/CourseMap_Combined_{dept}_{ymd}_{n_users}users.xlsx"
        files.append((zip_path, xls_bytes))

        audit_rows.append({
            "type": "staff_course_map_combined",
            "emails": n_users,
            "department": dept,
            "courses": ", ".join(course_ids),
            "roles": ", ".join(roles),
            "file": zip_path,
        })

        log("Generated Staff Combined CourseMap file.", "info")

    if email_errors:
        for e in email_errors[:20]:
            log(f"Skipped invalid email: {e}", "warn")
        if len(email_errors) > 20:
            log(f"...and {len(email_errors) - 20} more invalid emails.", "warn")

    if not files:
        log("No outputs selected (no files generated).", "warn")

    zip_bytes = _write_zip_structure(files)
    zip_filename = f"{parent}.zip"
    audit_df = pd.DataFrame(audit_rows)

    return GeneratedPackage(zip_bytes=zip_bytes, zip_filename=zip_filename, audit_df=audit_df, logs=logs)


def generate_student_package(
    cohort_name: str,
    full_name: str,
    raw_emails: str,
    raw_course_ids: str,
    is_y1: bool,
    generate_y1_new_users: bool,
    generate_course_map: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> GeneratedPackage:
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("StudentExcelGen", msg, level)
        logs.append(entry)
        log_callback(entry)

    cohort = (cohort_name or "").strip()
    if not cohort:
        raise ValueError("Cohort Name is required.")

    full_name = (full_name or "").strip()
    if not full_name:
        raise ValueError("Full Name of user is required.")

    emails_raw = _clean_lines(raw_emails)
    emails = []
    email_errors = []
    for line in emails_raw:
        e = _extract_email(line)
        ok, reason = _validate_email(e, mode="student")
        if ok:
            emails.append(e)
        else:
            email_errors.append(f"{line} -> {reason}")

    if not emails:
        raise ValueError("No valid student email addresses found.")

    course_ids = [x.strip() for x in _clean_lines(raw_course_ids)]
    if not course_ids and generate_course_map:
        raise ValueError("Course ID is required for Course Mapping output.")

    ymd = _now_yyyymmdd()
    n_courses = len(course_ids) if course_ids else 0
    n_students = len(emails)

    parent = f"Student_{cohort}_{ymd}_{n_courses}courses"
    files: List[Tuple[str, bytes]] = []
    audit_rows: List[Dict[str, str]] = []

    total_steps = max(n_courses if generate_course_map else 1, 1)
    progress_callback(0, total_steps)

    # 1) Y1 new users combined (1_NewCreationList)
    if is_y1 and generate_y1_new_users:
        df_users = _make_users_df(emails, full_name)
        xls_bytes = _df_to_xls_bytes(df_users)

        zip_path = f"{parent}/1_NewCreationList/NewUsers_Combined_{cohort}_{ymd}_{n_students}students.xlsx"
        files.append((zip_path, xls_bytes))

        audit_rows.append({
            "type": "student_new_users_combined",
            "cohort": cohort,
            "students": n_students,
            "file": zip_path,
        })

        log("Generated Y1 Combined New Users file.", "info")
    elif generate_y1_new_users and not is_y1:
        log("Y1 New Users requested but cohort is not Y1. No new users file generated.", "warn")

    # 2) Course mapping per course ID (2_IndivStudents)
    # many emails -> single course ID, role=learner
    if generate_course_map:
        for idx, cid in enumerate(course_ids, start=1):
            progress_callback(idx, total_steps)

            rows = [{"login": email, "organisation": cid, "roles": DEFAULT_STUDENT_ROLE} for email in emails]
            df_roles = _make_roles_df(rows)
            xls_bytes = _df_to_xls_bytes(df_roles)

            zip_path = f"{parent}/2_IndivStudents/CourseMap_{cohort}_{cid}_{ymd}_{n_students}students.xlsx"
            files.append((zip_path, xls_bytes))

            audit_rows.append({
                "type": "student_course_map",
                "cohort": cohort,
                "course_id": cid,
                "students": n_students,
                "role": DEFAULT_STUDENT_ROLE,
                "file": zip_path,
            })

        log(f"Generated {n_courses} Student CourseMap files.", "info")

    if email_errors:
        for e in email_errors[:20]:
            log(f"Skipped invalid email: {e}", "warn")
        if len(email_errors) > 20:
            log(f"...and {len(email_errors) - 20} more invalid emails.", "warn")

    if not files:
        log("No outputs selected (no files generated).", "warn")

    zip_bytes = _write_zip_structure(files)
    zip_filename = f"{parent}.zip"
    audit_df = pd.DataFrame(audit_rows)

    return GeneratedPackage(zip_bytes=zip_bytes, zip_filename=zip_filename, audit_df=audit_df, logs=logs)


# # Keep your combine function (still useful)
# def combine_excels(
#     sources: List[BytesIO],
#     output_path: str,
#     log_callback: LogCallback = default_log_callback,
#     progress_callback: ProgressCallback = default_progress_callback,
# ) -> Dict:
#     logs: List[Dict] = []

#     def log(msg: str, level: str = "info"):
#         entry = make_log_entry("ExcelCombine", msg, level)
#         logs.append(entry)
#         log_callback(entry)

#     if not sources:
#         log("No Excel sources provided to combine.", "warn")
#         return {"rows": 0, "excel_path": output_path, "dataframe": pd.DataFrame(), "logs": logs}

#     frames = []
#     total = len(sources)

#     for i, src in enumerate(sources, start=1):
#         progress_callback(i, total)
#         try:
#             df = pd.read_excel(src)
#             df["__SourceIndex"] = i
#             frames.append(df)
#             log(f"Read Excel {i}/{total} – rows: {len(df)}", "info")
#         except Exception as e:
#             log(f"Failed to read Excel {i}/{total}: {e}", "error")

#     combined_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

#     try:
#         combined_df.to_excel(output_path, index=False)
#         log(f"Combined Excel saved to: {output_path}", "info")
#     except Exception as e:
#         log(f"Failed to save combined Excel to {output_path}: {e}", "error")

#     return {"rows": len(combined_df), "excel_path": output_path, "dataframe": combined_df, "logs": logs}
