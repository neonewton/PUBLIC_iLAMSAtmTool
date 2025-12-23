from dataclasses import dataclass
from datetime import datetime
import xlwt
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
    "* login", "* password", "title", "* first_name", "* last_name",
    "authentication_method_id", "* email", "theme_id", "locale_id",
    "address_1", "address_2", "address_3", "city", "state",
    "postcode", "country", "day_phone", "evening_phone",
    "mobile_phone", "time_zone",
]

ROLES_COLUMNS = [
    "* login", "* organisation", "* roles", "* add_to_lessons",
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

def dataframe_to_xls(df) -> bytes:
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Sheet1")

    # headers
    for col_idx, col in enumerate(df.columns):
        ws.write(0, col_idx, col)

    # rows
    for row_idx, row in enumerate(df.itertuples(index=False), start=1):
        for col_idx, value in enumerate(row):
            ws.write(row_idx, col_idx, value)

    bio = BytesIO() 
    wb.save(bio)
    return bio.getvalue()

def _username_from_email(email: str) -> str:
    # strip domain; works for @ntu.edu.sg and @e.ntu.edu.sg
    return email.split("@")[0].strip()

def _safe_name(s: str) -> str:
    # optional: prevent weird folder/file chars
    return "".join(c for c in s.strip() if c not in r'\/:*?"<>|')


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
    if mode == "Staff" and not email.endswith("@ntu.edu.sg"):
        return False, "Staff email must end with @ntu.edu.sg"
    if mode == "Student" and not email.endswith("@e.ntu.edu.sg"):
        return False, "Student email must end with @e.ntu.edu.sg"
    return True, ""


def _parse_lines(raw: str) -> List[str]:
    return [x.strip() for x in raw.splitlines() if x.strip()]


def _make_users_df(emails: List[str], full_names: List[str]) -> pd.DataFrame:
    if len(emails) != len(full_names):
        raise ValueError("Number of names must match number of emails.")

    rows = []
    for email, name in zip(emails, full_names):
        rows.append({
            "login": email,
            "password": "Nanyang!23",
            "title": "",
            "first_name": name,
            "last_name": ".",
            "authentication_method_id": "",
            "email": email,
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

    df = pd.DataFrame(rows)

    df = df.rename(columns={
        "login": "* login",
        "password": "* password",
        "first_name": "* first_name",
        "last_name": "* last_name",
        "email": "* email",
    })

    return df[USERS_COLUMNS]



def _make_roles_df(rows: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)

    df = df.rename(columns={
        "login": "* login",
        "organisation": "* organisation",
        "roles": "* roles",
        "add_to_lessons": "* add_to_lessons",
    })

    return df[ROLES_COLUMNS]


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
    full_names: List[str],
    raw_emails: str,
    raw_course_ids: str,
    selected_roles: List[str],
    generate_new_users: bool,
    generate_course_map: bool,
    log_callback: LogCallback = None,
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

    dept = _safe_name(department_name)
    n_users = len(valid_emails)
    parent = f"StaffCEs_{dept}_{ymd}_{n_users:03d}users"

    if generate_new_users:

        if len(full_names) != len(valid_emails):
            raise ValueError("Number of names must match number of emails.")

        combined_rows = []

        for email, name in zip(valid_emails, full_names):
            # ----- Individual -----
            df_one = _make_users_df([email], [name])
            xls_bytes = dataframe_to_xls(df_one)

            username = _username_from_email(email)
            fname = f"{parent}/2_NewUsersList/NewUsers_{dept}_{username}_{ymd}.xls"
            files[fname] = xls_bytes
            audit_rows.append({"file": fname, "rows": len(df_one)})

            # collect for combined
            combined_rows.append({
                "login": email,
                "password": "Nanyang!23",
                "title": "",
                "first_name": name,
                "last_name": ".",
                "authentication_method_id": "",
                "email": email,
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

        # ----- Combined New Users -----
        df_combined = _make_users_df(
            [r["email"] for r in combined_rows],
            [r["first_name"] for r in combined_rows],
        )

        xls_bytes = dataframe_to_xls(df_combined)
        fname = f"{parent}/1_Combined/NewUsers_Combi_{dept}_{ymd}_{n_users:03d}users.xls"
        files[fname] = xls_bytes
        audit_rows.append({"file": fname, "rows": len(df_one)})



    # Course map 
    if generate_course_map:

        roles_str = "|".join(selected_roles)
        all_role_rows = []

        for email in valid_emails:
            username = _username_from_email(email)
            user_rows = []

            for cid in course_ids:
                row = {
                    "login": email,
                    "organisation": cid,
                    "roles": roles_str,
                    "add_to_lessons": "yes",
                }
                user_rows.append(row)
                all_role_rows.append(row)

            # ----- Individual per-user Excel -----
            df_user = _make_roles_df(user_rows)
            xls_bytes = dataframe_to_xls(df_user)

            fname = f"{parent}/3_CourseMapStaff/CourseMap_{dept}_{username}_{ymd}.xls"
            files[fname] = xls_bytes
            audit_rows.append({"file": fname, "rows": len(df_user)})
        
            # ----- Combined Excel (after loop) -----
        df_roles = _make_roles_df(all_role_rows)
        xls_bytes = dataframe_to_xls(df_roles)

        fname = f"{parent}/1_Combined/CourseMap_Combi_{dept}_{ymd}_{n_users:03d}users.xls"
        files[fname] = xls_bytes
        audit_rows.append({"file": fname, "rows": len(df_roles)})


    zip_name = f"{parent}.zip"
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
    full_names: List[str],
    raw_emails: str,
    raw_course_ids: str,
    generate_y1_new_users: bool,
    generate_course_map: bool,
    log_callback: LogCallback = None,
) -> GeneratedPackage:

    logs = []
    audit_rows = []

    emails = _parse_lines(raw_emails)
    course_ids = []
    invalid_ids = []

    for v in _parse_lines(raw_course_ids):
        if v.isdigit():
            course_ids.append(int(v))
        else:
            invalid_ids.append(v)

    if invalid_ids:
        raise ValueError(
            "Invalid Course IDs (must be integers only): "
            + ", ".join(invalid_ids)
        )

    valid_emails = []
    for e in emails:
        ok, reason = _validate_email(e, "student")
        if ok:
            valid_emails.append(e)
        else:
            _log(logs, log_callback, f"Skipped {e}: {reason}", "WARN")

    files = {}
    ymd = datetime.now().strftime("%Y%m%d")

    cohort = _safe_name(cohort_name)
    n_courses = len(course_ids)
    n_students = len(valid_emails)
    parent = f"Student_{cohort}_{ymd}_{n_courses:03d}courses"

    if generate_y1_new_users:
        n_students = len(valid_emails)
        students_tag = f"{n_students:03d}students"

        df_users = _make_users_df(valid_emails, full_names)
        xls_bytes = dataframe_to_xls(df_users)

        fname = f"{parent}/2_NewUsersList/NewUsers_Combined_{cohort}_{ymd}_{n_students:03d}students.xls"
        files[fname] = xls_bytes
        audit_rows.append({"file": fname, "rows": len(df_users)})


    if generate_course_map:
        for cid in course_ids:
            rows = []
            for email in valid_emails:
                rows.append({
                    "login": email,
                    "organisation": cid,
                    "roles": "learner",
                    "add_to_lessons": "yes",
                })

            df_roles = _make_roles_df(rows)
            xls_bytes = dataframe_to_xls(df_roles)

            fname = f"{parent}/3_CourseMapStudents/CourseMap_Combi_{cohort}_CID{cid}_{ymd}_{n_students}students.xls"
            files[fname] = xls_bytes
            audit_rows.append({"file": fname, "rows": len(df_roles)})


    zip_name = f"{parent}.zip"
    zip_bytes = _zip_files(files)

    return GeneratedPackage(
        zip_bytes=zip_bytes,
        zip_filename=zip_name,
        audit_df=pd.DataFrame(audit_rows),
        logs=logs,
    )
