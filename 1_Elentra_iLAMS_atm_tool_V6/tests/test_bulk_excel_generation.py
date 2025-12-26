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

def open_zip(zip_bytes: bytes):
    return zipfile.ZipFile(BytesIO(zip_bytes))


def read_xls_from_zip(zf: zipfile.ZipFile, filename: str) -> pd.DataFrame:
    with zf.open(filename) as f:
        return pd.read_excel(f)


# -------------------------------------------------
# STAFF TESTS
# -------------------------------------------------

def test_invalid_staff_email_skipped():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["Alice"],
        raw_emails="alice@gmail.com",
        raw_course_ids="101",
        selected_roles=["monitor"],
        generate_new_users=True,
        generate_course_map=False,
    )

    assert pkg.audit_df.empty

    zf = open_zip(pkg.zip_bytes)

    files = zf.namelist()

    # two individual new-user files
    assert any("NewUsers_DL_alice_" in f for f in files)
    assert any("NewUsers_DL_bob_" in f for f in files)

    # combined new users
    assert any("NewUsers_Combi_DL" in f for f in files)


def test_staff_users_xls_headers():
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
    fname = next(f for f in zf.namelist() if "NewUsers_DL_alice" in f)

    df = read_xls_from_zip(zf, fname)

    assert list(df.columns) == USERS_COLUMNS
    assert df.loc[0, "* login"] == "alice@ntu.edu.sg"
    assert df.loc[0, "* first_name"] == "Alice Tan"


def test_staff_course_map_roles_pipe_join():
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
    fname = next(f for f in zf.namelist() if "CourseMap_DL_alice" in f)

    df = read_xls_from_zip(zf, fname)

    assert df.loc[0, "* roles"] == "monitor|course manager"
    assert len(df) == 2  # 2 course IDs


def test_staff_combined_course_map_exists():
    pkg = generate_staff_package(
        department_name="DL",
        full_names=["A", "B"],
        raw_emails="a@ntu.edu.sg\nb@ntu.edu.sg",
        raw_course_ids="101\n102",
        selected_roles=["monitor"],
        generate_new_users=False,
        generate_course_map=True,
    )

    zf = open_zip(pkg.zip_bytes)

    assert any("CourseMap_Combi_DL" in f for f in zf.namelist())


# -------------------------------------------------
# STUDENT TESTS
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


def test_student_y1_new_users_combined():
    pkg = generate_student_package(
        cohort_name="Cohort2026",
        full_names=["Student One", "Student Two"],
        raw_emails="s1@e.ntu.edu.sg\ns2@e.ntu.edu.sg",
        raw_course_ids="201",
        generate_y1_new_users=True,
        generate_course_map=False,
    )

    zf = open_zip(pkg.zip_bytes)

    fname = next(f for f in zf.namelist() if "NewUsers_Combined" in f)
    df = read_xls_from_zip(zf, fname)

    assert len(df) == 2
    assert list(df.columns) == USERS_COLUMNS


# -------------------------------------------------
# VALIDATION TESTS
# -------------------------------------------------

def test_invalid_staff_email_rejected():
    with pytest.raises(Exception):
        generate_staff_package(
            department_name="DL",
            full_names=["Alice"],
            raw_emails="alice@gmail.com",
            raw_course_ids="101",
            selected_roles=["monitor"],
            generate_new_users=True,
            generate_course_map=False,
        )


def test_student_course_id_must_be_integer():
    with pytest.raises(ValueError):
        generate_student_package(
            cohort_name="Cohort2026",
            full_names=["Student One"],
            raw_emails="s1@e.ntu.edu.sg",
            raw_course_ids="ABC",
            generate_y1_new_users=False,
            generate_course_map=True,
        )

