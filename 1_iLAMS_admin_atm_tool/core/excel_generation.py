# core/excel_generation.py

import re
from typing import List, Dict
import pandas as pd

from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
)


EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z0-9\-]+)")


def _parse_line_to_record(line: str) -> Dict:
    """
    Attempt to parse an input line into:
    - First Name
    - Last Name
    - Email
    - Username
    - Raw
    """
    raw = line.strip()

    # Extract email
    email_match = EMAIL_REGEX.search(raw)
    email = email_match.group(1) if email_match else ""

    # Extract name part = raw with email removed
    name_part = raw.replace(email, "").replace("<", "").replace(">", "").strip(" -\t")

    first_name = ""
    last_name = ""
    username = ""

    if email:
        username = email.split("@")[0]
        # Derive name from username if no explicit name
        if not name_part:
            # try split by ., _, or -
            parts = re.split(r"[._\-]+", username)
            if len(parts) >= 2:
                first_name = parts[0].title()
                last_name = " ".join(p.title() for p in parts[1:])
            else:
                first_name = username.title()
                last_name = ""
        else:
            # Name provided: split into first + last
            parts = name_part.split()
            if len(parts) == 1:
                first_name = parts[0].title()
                last_name = ""
            else:
                first_name = parts[0].title()
                last_name = " ".join(p.title() for p in parts[1:])
    else:
        # No email found, put everything into RawName
        name_part = raw
        parts = name_part.split()
        if parts:
            first_name = parts[0].title()
            if len(parts) > 1:
                last_name = " ".join(p.title() for p in parts[1:])

    return {
        "RawInput": raw,
        "FirstName": first_name,
        "LastName": last_name,
        "Email": email,
        "Username": username,
    }


def generate_user_excel(
    raw_text: str,
    mode: str,
    course_name: str,
    output_path: str,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    Parse raw text input into a table for user creation.
    mode: "student" or "staff"
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ExcelGeneration", msg, level)
        logs.append(entry)
        log_callback(entry)

    lines = [l for l in (raw_text or "").splitlines() if l.strip()]
    if not lines:
        log("No lines found in input text.", "warn")
        df = pd.DataFrame(columns=["RawInput", "FirstName", "LastName", "Email", "Username"])
        return {
            "rows": 0,
            "excel_path": output_path,
            "dataframe": df,
            "logs": logs,
        }

    total = len(lines)
    records: List[Dict] = []

    log(f"Starting Excel generation: mode={mode}, course='{course_name}', lines={total}.")

    for i, line in enumerate(lines, start=1):
        progress_callback(i, total)
        rec = _parse_line_to_record(line)
        records.append(rec)
        log(f"Parsed line {i}/{total}: {rec['Email'] or 'NO EMAIL'}")

    df = pd.DataFrame(records)

    # Extra columns useful for imports; adjust to your system needs
    df.insert(0, "Course", course_name)
    df.insert(1, "Role", mode.lower())

    try:
        df.to_excel(output_path, index=False)
        log(f"Excel saved to: {output_path}", "info")
    except Exception as e:
        log(f"Failed to save Excel to {output_path}: {e}", "error")

    return {
        "rows": len(df),
        "excel_path": output_path,
        "dataframe": df,
        "logs": logs,
    }
