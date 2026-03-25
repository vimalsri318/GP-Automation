import os
import pandas as pd
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from config import BASE_DIR

# --------------------------------------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------------------------------------
# Ensure we find the 'Input Files' directory reliably from the backend root
PROJECT_ROOT = Path(str(BASE_DIR.parent.parent))
INPUT_DIR = os.path.join(str(PROJECT_ROOT), "Input Files")
CACHE_DIR = os.path.join(INPUT_DIR, ".cache")

# --------------------------------------------------------------------------------
# SMART COLUMN MAPPING (SYNONYOMS)
# --------------------------------------------------------------------------------
COL_SYNONYMS = {
    "revenue": ["revenue", "amount", "value", "net value", "amount in doc. curr.", "general ledger amount"],
    "cost": ["cost", "actual cost", "total cost", "expense"],
    "so_number": ["so number", "sales order", "so no", "so number 1", "so number 2"],
    "acc_doc": ["accounting document", "document number", "doc. number"],
    "invoice": ["invoice no", "invoice", "billing document", "reference key 3", "reference key"]
}

def get_col_from_df(df: pd.DataFrame, *target_keys: str) -> Optional[str]:
    """
    Finds a column in a dataframe using a fuzzy 'Synonym Map'.
    Matches case-insensitive, stripped, and fuzzy substrings.
    """
    cleaned_cols = {str(c).lower().strip(): c for c in df.columns}
    
    # Pass 1: Check prioritized target keys
    for key in target_keys:
        lk = key.lower().strip()
        # Direct Match
        if lk in cleaned_cols:
            return cleaned_cols[lk]
        # Partial Match
        for c_lower, original_name in cleaned_cols.items():
            if lk in c_lower:
                return original_name
                
    # Pass 2: Check global synonyms if target keys were generic
    for key in target_keys:
        lk = key.lower().strip()
        if lk in COL_SYNONYMS:
            for synonym in COL_SYNONYMS[lk]:
                if synonym in cleaned_cols:
                    return cleaned_cols[synonym]
                
    return None

# --------------------------------------------------------------------------------
# HIGH-PERFORMANCE CACHING ENGINE
# --------------------------------------------------------------------------------
def get_cached_dataframe(file_path: str, sheet_name: Any = 0, engine: str = 'openpyxl') -> pd.DataFrame:
    """
    Retrieves data from a high-speed binary pickle if available, 
    otherwise parses Excel and saves it to binary for future 'Instant Loads'.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
        
    mtime = os.path.getmtime(file_path)
    # Unique ID tied to mtime to detect file changes instantly
    file_id = f"{file_path}_{mtime}_{sheet_name}".encode('utf-8')
    hash_str = hashlib.md5(file_id).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{hash_str}.pkl")
    
    if os.path.exists(cache_path):
        try:
            # 🚀 Instant binary load (~50-100x faster than Excel)
            print(f"✅ [AutomationEngine] Cache Hit: {os.path.basename(file_path)}")
            return pd.read_pickle(cache_path)
        except Exception:
            pass
            
    # 🐌 Slow Excel parse (Happens only once per file change)
    print(f"🚀 [AutomationEngine] Eager Parsing: {os.path.basename(file_path)}...")
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
    
    # Save for next time
    try:
        df.to_pickle(cache_path)
    except Exception:
        pass
        
    return df

def normalize_sap_id(val: Any) -> str:
    """Cleans SAP reference IDs (strip leading zeros, decimals, and spaces)."""
    return str(val).strip().replace('.0', '').lstrip('0')
