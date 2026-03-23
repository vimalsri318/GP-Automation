"""Step 1 Service - File Upload and Parsing"""
import pandas as pd
import os
import time
from pathlib import Path
from config import UPLOAD_DIR
from typing import Dict, Any


def validate_file(filename: str, file_size: int) -> tuple:
    """Validate file"""
    ext = Path(filename).suffix.lower().lstrip('.')
    if ext not in ['xlsx', 'xls', 'csv']:
        return False, f"Not supported: {ext}"
    if file_size > 100 * 1024 * 1024:
        return False, "File too large (>100MB)"
    return True, None


def save_file(filename: str, content: bytes) -> str:
    """Save file"""
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, 'wb') as f:
        f.write(content)
    return path


def parse_excel(file_path: str):
    """Parse Excel file"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error reading Excel: {str(e)}")


def process_files(files_dict: dict) -> Dict[str, Any]:
    """Process multiple files"""
    start = time.time()
    results: Dict[str, Any] = {"success": True, "files": {}, "errors": []}

    for filename, content in files_dict.items():
        try:
            # Validate
            valid, err = validate_file(filename, len(content))
            if not valid:
                results["errors"].append({"file": filename, "error": err})
                continue

            # Save
            path = save_file(filename, content)

            # Parse
            df = parse_excel(path)

            # Summary
            preview_df = df.head(5).fillna("")
            results["files"][filename] = {
                "rows": len(df),
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "preview": preview_df.to_dict('records')
            }

        except Exception as e:
            results["errors"].append({"file": filename, "error": str(e)})

    results["execution_time_ms"] = int((time.time() - start) * 1000)
    if results["errors"] and not results["files"]:
        results["success"] = False

    return results
