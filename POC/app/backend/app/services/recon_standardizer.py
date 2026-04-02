import os
import pandas as pd
import time
import re
#from app.services.step2_service import get_file_by_heuristic, get_col_strict
from app.services.automation_engine import PROJECT_ROOT, INPUT_DIR, CACHE_DIR, get_cached_dataframe
# from app.services.automation_engine import PROJECT_ROOT, INPUT_DIR, CACHE_DIR, get_cached_dataframe, get_audit_manager

from app.services.automation_engine import (
    PROJECT_ROOT, INPUT_DIR, CACHE_DIR,
    get_cached_dataframe, get_file_by_heuristic, get_col_strict
)

def standardize_recon_format(month_name: str = None):
    """
    Step 0: Target Format Initialization.
    Standardizes raw Z-Recon into the 'Final-Zrecon.xlsx' format.
    
    1. Reads Raw Z-Recon (Base File).
    2. Reads Template (Final-Zrecon.xlsx Headers).
    3. Populates Column 0 with Month (User provided or extracted from filename).
    4. Populates Columns 1-20 with Z-Recon Data.
    5. Preserves Template Column names for future operations.
    """
    try:
        start_time = time.perf_counter()
        
        # 1. Discover Files
        raw_path = get_file_by_heuristic("Z Recon")
        # Template discovery explicitly looking for "Final-Zrecon"
        files_in_input = os.listdir(INPUT_DIR)
        template_name = next((f for f in files_in_input if "final-zrecon" in f.lower()), None)
        
        if not template_name:
            return {"success": False, "error": "Template file 'Final-Zrecon.xlsx' not found in Input Files."}
        
        template_path = os.path.join(INPUT_DIR, template_name)
        
        # 2. Extract Month from filename (e.g. "Feb 2026") if not provided
        if not month_name:
            filename = os.path.basename(raw_path)
            month_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*.*?\d{4}', filename, re.I)
            month_val = month_match.group(0) if month_match else "Unknown Month"
        else:
            month_val = month_name
            
        # 3. Read Data (Using Calamine for Speed)
        raw_df = get_cached_dataframe(raw_path, engine='calamine')
        # Only read headers for template if it is really just a template
        template_df = get_cached_dataframe(template_path, engine='openpyxl') # read headers primarily
        
        # 4. Standardized Initialization
        # Create new DF with template columns and raw data row count
        target_df = pd.DataFrame(columns=template_df.columns, index=range(len(raw_df)))
        
        # a) Populate Month
        target_df.iloc[:, 0] = month_val
        
        # b) Map existing data (Assuming columns 1 to 20 match raw_df columns)
        # We will do smarter mapping to be safe
        #raw_cols = list(raw_df.columns)
        target_cols = list(target_df.columns)
        
        # We know from analysis that target_cols[1:21] should match raw_cols
        # But we use get_col_strict to be safe for each target column
        matched_count = 0
        for i in range(1, len(target_cols)):
            t_col_name = target_cols[i]
            # Try to match t_col_name in raw_df
            raw_match = get_col_strict(raw_df, t_col_name)
            if raw_match:
                target_df[t_col_name] = raw_df[raw_match].values
                matched_count += 1
        
        # 5. Save Checkpoint as "Z_Recon_Step0.pkl" (Basis for all subsequent steps)
        # IMPORTANT: We make this the NEW base file for the engine
        checkpoint_path = os.path.join(CACHE_DIR, "Z_Recon_Step0.pkl")
        target_df.to_pickle(checkpoint_path)
        
        # Also save an XLSX for visual verification in Root
        visual_path = os.path.join(str(PROJECT_ROOT), "Z_Recon_Standardized_Format.xlsx")
        # In actual engine, we use audit manager for this but we can do it directly for Step 0
        target_df.to_excel(visual_path, index=False, engine='openpyxl')
        
        duration = int((time.perf_counter() - start_time) * 1000)
        return {
            "success": True,
            "message": "Z-Recon standardized successfully.",
            "month_detected": month_val,
            "columns_mapped": matched_count,
            "total_rows": len(target_df),
            "execution_time_ms": duration,
            "preview": target_df.head(5).fillna("").to_dict('records'),
            "process_steps": [
                {"label": "Template Initialization", "detail": f"Derived layout from {template_name}."},
                {"label": "Month Locking", "detail": f"Set period to '{month_val}'."},
                {"label": "Data Migration", "detail": f"Successfully mapped {matched_count} columns to standardized format."},
                {"label": "Basis Locked", "detail": "All subsequent check workflow steps will now use this target format."}
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
