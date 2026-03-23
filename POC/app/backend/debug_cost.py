import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.step2_service import get_file_by_heuristic

def analyze_cost_dump():
    try:
        file_path = get_file_by_heuristic("Cost")
        print(f"Reading: {file_path}")
        df = pd.read_excel(file_path, sheet_name=1, header=0, engine='calamine')
        
        sum_col = next((c for c in df.columns if "general ledger amount" in str(c).strip().lower()), None)
        df[sum_col] = pd.to_numeric(df[sum_col], errors='coerce').fillna(0)
        
        total_sum = df[sum_col].sum()
        print(f"Raw Column Sum: {total_sum}")
        
        # Are there any rows that say "Total" or something?
        print("Dataset Size:", df.shape)
        
        # Print a few random rows to see the structure
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check if there are any obvious duplicate groupings or subtotal rows
        # E.g., is there a column that identifies summary rows?
        print("\nColumns and unique values for potential summary columns:")
        for col in df.columns[:10]:  # Just check first 10 columns
            try:
                unique_vals = df[col].astype(str).unique()
                if any("total" in str(v).lower() or "sum" in str(v).lower() for v in unique_vals):
                    print(f"Column '{col}' contains 'total' or 'sum' strings.")
            except:
                pass
                
    except Exception as e:
        print(f"Error: {e}")

analyze_cost_dump()
