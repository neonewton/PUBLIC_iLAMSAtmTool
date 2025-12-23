from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List, Callable, Dict, Tuple
import zipfile
import pandas as pd
import re

# -----------------------------
# Constants
# -----------------------------
USERS_COLUMNS = [
    "login", "password", "title", "first_name", "last_name",
    "authentication_method_id", "email", "theme_id", "locale_id",
    "address_1", "address_2", "address_3", "city", "state",
    "postcode", "country", "day_phone", "evening_phone",
    "mobile_phone", "time_zone",
]

ROLES_COLUMNS = [
    "login", "organisation", "roles", "add_to_lessons",
]

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# -----------------------------
# Types
# -----------------------------
LogCallback = Callable[[Dict], None]
ProgressCallback = Callable[[int, int], None]


@dataclass
class GeneratedPackage:
    zip_bytes: bytes
    zip_filename: str
    audit_df: pd.DataFrame
    logs: List[Dict]


# -----------------------------
# Utilities
# -----------------------------
def _log(logs, cb, msg, level="INFO"):
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "message": msg,
    }
    logs.append(entry)
    if cb:
        cb(entry)


def _validate_email(email: str, mode: str) -> Tuple[bool, str]:
    if not email:
        return False, "Email is empty"
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    if mode == "staff" and not email.endswith("@ntu.edu.sg"):
        return False, "Staff email must end with @ntu.edu.sg"
    if mode == "student" and not email.endswith("@e.ntu.edu.sg"):
        return False, "Student email must end with @e.ntu.edu.sg"
    return True, ""


def _parse_lines(raw: str) -> List[str]:
    return [x.strip() for x in raw.splitlines() if x.strip()]


def _make_users_df(emails: List[str], full_name: str) -> pd.DataFrame:
    rows = []
    for e in emails:
        rows.append({
            "login": e,
            "password": "Nanyang!23",
            "title": "",
            "first_name": full_name,
            "last_name": ".",
            "authentication_method_id": "",
            "email": e,
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


def _make_roles_df(rows: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=ROLES_COLUMNS)


def _zip_files(files: Dict[str, bytes]) -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


# -----------------------------
# STAFF
# -----------------------------
def generate_staff_package(
    department_name: str,
    full_name: str,
    raw_emails: str,
    raw_course_ids: str,
    selected_roles: List[str],
    generate_new_users: bool,
    generate_course_map: bool,
    generate_combined_course_map: bool,
    log_callback: LogCallback = None,
    progress_callback: ProgressCallback = None,
) -> GeneratedPackage:

    logs = []
    audit_rows = []

    emails = _parse_lines(raw_emails)
    course_ids = _parse_lines(raw_course_ids)

    valid_emails = []
    for e in emails:
        ok, reason = _validate_email(e, "staff")
        if ok:
            valid_emails.append(e)
        else:
            _log(logs, log_callback, f"Skipped {e}: {reason}", "WARN")

    files = {}
    ymd = datetime.now().strftime("%Y%m%d")

    # New users
    if generate_new_users:
        df_users = _make_users_df(valid_emails, full_name)
        bio = BytesIO()
        df_users.to_excel(bio, index=False)
        fname = f"1_NewCreationList/NewUsers_{department_name}_{ymd}.xlsx"
        files[fname] = bio.getvalue()
        audit_rows.append({"file": fname, "rows": len(df_users)})

    # Course map
    role_rows = []
    if generate_course_map:
        for e in valid_emails:
            for cid in course_ids:
                for r in selected_roles:
                    role_rows.append({
                        "login": e,
                        "organisation": cid,
                        "roles": r,
                        "add_to_lessons": "yes",
                    })

        df_roles = _make_roles_df(role_rows)
        bio = BytesIO()
        df_roles.to_excel(bio, index=False)
        fname = f"2_IndivUsers/CourseMap_{department_name}_{ymd}.xlsx"
        files[fname] = bio.getvalue()
        audit_rows.append({"file": fname, "rows": len(df_roles)})

    # Combined
    if generate_combined_course_map:
        df_roles = _make_roles_df(role_rows)
        bio = BytesIO()
        df_roles.to_excel(bio, index=False)
        fname = f"3_CombiUsers/CourseMap_Combined_{department_name}_{ymd}.xlsx"
        files[fname] = bio.getvalue()
        audit_rows.append({"file": fname, "rows": len(df_roles)})

    zip_name = f"StaffCEs_{department_name}_{ymd}.zip"
    zip_bytes = _zip_files(files)

    return GeneratedPackage(
        zip_bytes=zip_bytes,
        zip_filename=zip_name,
        audit_df=pd.DataFrame(audit_rows),
        logs=logs,
    )


# -----------------------------
# STUDENT
# -----------------------------
def generate_student_package(
    cohort_name: str,
    full_name: str,
    raw_emails: str,
    raw_course_ids: str,
    is_y1: bool,
    generate_y1_new_users: bool,
    generate_course_map: bool,
    log_callback: LogCallback = None,
    progress_callback: ProgressCallback = None,
) -> GeneratedPackage:

    logs = []
    audit_rows = []

    emails = _parse_lines(raw_emails)
    course_ids = _parse_lines(raw_course_ids)

    valid_emails = []
    for e in emails:
        ok, reason = _validate_email(e, "student")
        if ok:
            valid_emails.append(e)
        else:
            _log(logs, log_callback, f"Skipped {e}: {reason}", "WARN")

    files = {}
    ymd = datetime.now().strftime("%Y%m%d")

    if is_y1 and generate_y1_new_users:
        df_users = _make_users_df(valid_emails, full_name)
        bio = BytesIO()
        df_users.to_excel(bio, index=False)
        fname = f"1_NewCreationList/NewUsers_{cohort_name}_{ymd}.xlsx"
        files[fname] = bio.getvalue()
        audit_rows.append({"file": fname, "rows": len(df_users)})

    if generate_course_map:
        rows = []
        for cid in course_ids:
            for e in valid_emails:
                rows.append({
                    "login": e,
                    "organisation": cid,
                    "roles": "learner",
                    "add_to_lessons": "yes",
                })

        df_roles = _make_roles_df(rows)
        bio = BytesIO()
        df_roles.to_excel(bio, index=False)
        fname = f"2_IndivStudents/CourseMap_{cohort_name}_{ymd}.xlsx"
        files[fname] = bio.getvalue()
        audit_rows.append({"file": fname, "rows": len(df_roles)})

    zip_name = f"Student_{cohort_name}_{ymd}.zip"
    zip_bytes = _zip_files(files)

    return GeneratedPackage(
        zip_bytes=zip_bytes,
        zip_filename=zip_name,
        audit_df=pd.DataFrame(audit_rows),
        logs=logs,
    )
