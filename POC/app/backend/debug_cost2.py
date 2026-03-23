import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.step2_service import get_file_by_heuristic

def analyze_cost_dump():
    try:
        file_path = get_file_by_heuristic("Cost")
        df = pd.read_excel(file_path, sheet_name=1, header=0, engine='calamine')
        
        sum_col = next((c for c in df.columns if "general ledger amount" in str(c).strip().lower()), None)
        df[sum_col] = pd.to_numeric(df[sum_col], errors='coerce').fillna(0)
        
        print("All columns:", df.columns.tolist())
        
        for col in df.columns:
            if df[col].nunique() < 10:
                sums = df.groupby(col)[sum_col].sum()
                print(f"Grouping by '{col}':")
                print(sums)
                
    except Exception as e:
        print(f"Error: {e}")

analyze_cost_dump()
