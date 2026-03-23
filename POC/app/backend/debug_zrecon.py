import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.step2_service import get_file_by_heuristic

def analyze_zrecon():
    try:
        file_path = get_file_by_heuristic("Z Recon")
        df = pd.read_excel(file_path, engine='openpyxl')
        
        print("Total rows:", len(df))
        if "Revenue" in df.columns:
            rev_col = pd.to_numeric(df["Revenue"], errors='coerce').fillna(0)
            print("Revenue Sum:", rev_col.sum())
            print("Count of non-zero rows:", (rev_col != 0).sum())
            
            # Let's see if the very last row or second to last row contains the total
            print("\nLast 5 rows of Revenue:")
            last_rows = df.tail(5)
            for _, row in last_rows.iterrows():
                print(row.to_dict())
                
        if "Cost" in df.columns:
            cost_col = pd.to_numeric(df["Cost"], errors='coerce').fillna(0)
            print("Cost Sum:", cost_col.sum())
                
    except Exception as e:
        print(f"Error: {e}")

analyze_zrecon()
