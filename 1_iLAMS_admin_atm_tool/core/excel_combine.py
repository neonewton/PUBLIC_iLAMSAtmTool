# core/excel_combine.py

from typing import List, Dict, Union, IO
import pandas as pd

from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
)


def _read_excel_generic(source: Union[str, IO[bytes]]) -> pd.DataFrame:
    """
    Read an Excel file from a file path or a file-like object.
    """
    return pd.read_excel(source)


def combine_excels(
    sources: List[Union[str, IO[bytes]]],
    output_path: str,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    Combine multiple Excel sources (paths or file-like) into one DataFrame.
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ExcelCombine", msg, level)
        logs.append(entry)
        log_callback(entry)

    if not sources:
        log("No Excel sources provided to combine.", "warn")
        combined_df = pd.DataFrame()
        return {
            "rows": 0,
            "excel_path": output_path,
            "dataframe": combined_df,
            "logs": logs,
        }

    frames = []
    total = len(sources)

    for i, src in enumerate(sources, start=1):
        progress_callback(i, total)
        try:
            df = _read_excel_generic(src)
            df["__SourceIndex"] = i
            frames.append(df)
            log(f"Read Excel {i}/{total} – rows: {len(df)}", "info")
        except Exception as e:
            log(f"Failed to read Excel {i}/{total}: {e}", "error")

    if frames:
        combined_df = pd.concat(frames, ignore_index=True)
    else:
        combined_df = pd.DataFrame()

    try:
        combined_df.to_excel(output_path, index=False)
        log(f"Combined Excel saved to: {output_path}", "info")
    except Exception as e:
        log(f"Failed to save combined Excel to {output_path}: {e}", "error")

    return {
        "rows": len(combined_df),
        "excel_path": output_path,
        "dataframe": combined_df,
        "logs": logs,
    }
