import zipfile
from io import BytesIO
import pandas as pd
import pytest

from core.backend_3_Bulk_User_Excel_Gen import (
    generate_staff_package,
    generate_student_package,
    USERS_COLUMNS,
    ROLES_COLUMNS,
)

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def open_zip(zip_bytes: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(BytesIO(zip_bytes))


def read_xls(zf: zipfile.ZipFile, name_contains: str) -> pd.DataFrame:
    fname = next(n for n in zf.namelist() if name_contains in n)
    with zf.open(fname) as f:
        return pd.read_excel(f)


# -------------------------------------------------
# STAFF – EMAIL & USER GENERATION
# -------------------------------------------------

def test_staff_invalid_email_is_skipped_not_crash():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["Alice Tan"],
        raw_emails="alice@gmail.com\nalice@ntu.edu.sg",
        raw_course_ids="101",
        selected_roles=["monitor"],
        generate_new_users=True,
        generate_course_map=False,
    )

    zf = open_zip(pkg.zip_bytes)

    # Only valid NTU email should be present
    df = read_xls(zf, "NewUsers_")
    assert len(df) == 1
    assert df.loc[0, "* email"].endswith("@ntu.edu.sg")


def test_staff_users_xls_schema_and_values():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["Alice Tan"],
        raw_emails="alice@ntu.edu.sg",
        raw_course_ids="101",
        selected_roles=["monitor"],
        generate_new_users=True,
        generate_course_map=False,
    )

    zf = open_zip(pkg.zip_bytes)
    df = read_xls(zf, "NewUsers_")

    assert list(df.columns) == USERS_COLUMNS
    assert df.loc[0, "* login"] == "alice@ntu.edu.sg"
    assert df.loc[0, "* first_name"] == "Alice Tan"


# -------------------------------------------------
# STAFF – COURSE MAP
# -------------------------------------------------

def test_staff_course_map_roles_joined_correctly():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["Alice Tan"],
        raw_emails="alice@ntu.edu.sg",
        raw_course_ids="101\n102",
        selected_roles=["monitor", "course manager"],
        generate_new_users=False,
        generate_course_map=True,
    )

    zf = open_zip(pkg.zip_bytes)
    df = read_xls(zf, "CourseMap_")

    assert list(df.columns) == ROLES_COLUMNS
    assert set(df["* organisation"].astype(str)) == {"101", "102"}
    assert df.loc[0, "* roles"] == "monitor|course manager"

def test_staff_combined_course_map_exists():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["A", "B"],
        raw_emails="a@ntu.edu.sg\nb@ntu.edu.sg",
        raw_course_ids="101",
        selected_roles=["monitor"],
        generate_new_users=False,
        generate_course_map=True,
    )

    zf = open_zip(pkg.zip_bytes)
    assert any("CourseMap_Combi_" in f for f in zf.namelist())


# -------------------------------------------------
# STUDENT – VALIDATION
# -------------------------------------------------

def test_student_invalid_course_ids_raise():
    with pytest.raises(ValueError):
        generate_student_package(
            cohort_name="Cohort2026",
            full_names=["Student One"],
            raw_emails="s1@e.ntu.edu.sg",
            raw_course_ids="ABC\n123",
            generate_y1_new_users=False,
            generate_course_map=True,
        )


def test_student_invalid_email_skipped():
    pkg = generate_student_package(
        cohort_name="Cohort2026",
        full_names=["Student One"],
        raw_emails="bad@gmail.com\ns1@e.ntu.edu.sg",
        raw_course_ids="201",
        generate_y1_new_users=True,
        generate_course_map=False,
    )

    zf = open_zip(pkg.zip_bytes)
    df = read_xls(zf, "NewUsers_")

    assert len(df) == 1
    assert df.loc[0, "* email"].endswith("@e.ntu.edu.sg")


# -------------------------------------------------
# STUDENT – COURSE MAP
# -------------------------------------------------

def test_student_course_map_per_course():
    pkg = generate_student_package(
        cohort_name="Cohort2026",
        full_names=["Student One", "Student Two"],
        raw_emails="s1@e.ntu.edu.sg\ns2@e.ntu.edu.sg",
        raw_course_ids="201\n202",
        generate_y1_new_users=False,
        generate_course_map=True,
    )

    zf = open_zip(pkg.zip_bytes)

    files = zf.namelist()
    assert any("CID201" in f for f in files)
    assert any("CID202" in f for f in files)


def test_student_new_users_schema():
    pkg = generate_student_package(
        cohort_name="Cohort2026",
        full_names=["Student One"],
        raw_emails="s1@e.ntu.edu.sg",
        raw_course_ids="201",
        generate_y1_new_users=True,
        generate_course_map=False,
    )

    zf = open_zip(pkg.zip_bytes)
    df = read_xls(zf, "NewUsers_")

    assert list(df.columns) == USERS_COLUMNS
    assert len(df) == 1



# pytest --cov=core.backend_3_Bulk_User_Excel_Gen --cov-report=term-missing
