import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.step2_service import get_file_by_heuristic

rev_file = get_file_by_heuristic("Revenue Dump")
print(f"Reading {rev_file} sheet 1 (raw data) with calamine...")
import time
t0 = time.time()
df = pd.read_excel(rev_file, sheet_name=1, header=0, engine='calamine')
# or openpyxl
print(f"Time taken: {time.time()-t0:.2f}s")
print(f"Shape: {df.shape}")
print("Columns:", [str(c).lower() for c in df.columns])
