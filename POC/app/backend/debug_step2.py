import os
import pandas as pd
from pathlib import Path

INPUT_DIR = "/Users/macbook/Downloads/Library/PROJECTS/Randstad/Untitled/POC/Input Files"

def debug_step2_columns():
    files = {
        "Z-Recon": "Z Recon - 1st Feb to 26th Feb 2026 - Base File.XLSX",
        "Revenue Dump": "Revenue Dump - 1st to 26th Feb 2026.XLSX",
        "Invoice Listing": "Invoice Listing - 1st Jan to 28th Feb 2026.XLSX"
    }
    
    for label, filename in files.items():
        path = os.path.join(INPUT_DIR, filename)
        print(f"\n--- Analyzing {label} ({filename}) ---")
        try:
            # Using sheet index
            sheet = 1 if "Revenue" in label or "Cost" in label else 0
            df = pd.read_excel(path, sheet_name=sheet, nrows=5)
            print(f"Columns: {list(df.columns)}")
            print("Row 0 Snapshot:")
            for col in df.columns:
                print(f"  {col}: {df[col].iloc[0]} (Type: {type(df[col].iloc[0])})")
        except Exception as e:
            print(f"Error loading {label}: {e}")

if __name__ == "__main__":
    debug_step2_columns()
