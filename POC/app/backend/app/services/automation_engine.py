import os
import pandas as pd
import hashlib
import glob
from typing import Dict, Any, List, Optional
from pathlib import Path
from config import BASE_DIR

# --------------------------------------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------------------------------------
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
    cleaned_cols = {str(c).lower().strip(): c for c in df.columns}
    for key in target_keys:
        lk = key.lower().strip()
        if lk in cleaned_cols: return cleaned_cols[lk]
        for c_lower, original_name in cleaned_cols.items():
            if lk in c_lower: return original_name
    for key in target_keys:
        lk = key.lower().strip()
        if lk in COL_SYNONYMS:
            for synonym in COL_SYNONYMS[lk]:
                if synonym in cleaned_cols: return cleaned_cols[synonym]
    return None

# --------------------------------------------------------------------------------
# HIGH-PERFORMANCE SMART CACHING (AUTO-PURGE)
# --------------------------------------------------------------------------------
def get_cached_dataframe(file_path: str, sheet_name: Any = 0, engine: str = 'openpyxl') -> pd.DataFrame:
    """Retrieves high-speed binary with automatic old version cleanup."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
        
    mtime = os.path.getmtime(file_path)
    # 1. Create a Base ID for the file itself
    base_id = f"{file_path}_{sheet_name}".encode('utf-8')
    base_hash = hashlib.md5(base_id).hexdigest()
    
    # 2. Create the current version path
    current_cache_name = f"{base_hash}_{int(mtime)}.pkl"
    current_cache_path = os.path.join(CACHE_DIR, current_cache_name)
    
    # 3. SMART PURGE: Delete any old versions of THIS specific file/sheet
    for old_cache in glob.glob(os.path.join(CACHE_DIR, f"{base_hash}_*.pkl")):
        if os.path.basename(old_cache) != current_cache_name:
            try:
                os.remove(old_cache)
                print(f"🧹 [AutomationEngine] Purged old version: {os.path.basename(old_cache)}")
            except Exception: pass

    if os.path.exists(current_cache_path):
        try:
            print(f"✅ [AutomationEngine] Cache Hit: {os.path.basename(file_path)} (Instant)")
            return pd.read_pickle(current_cache_path)
        except Exception: pass
            
    print(f"🚀 [AutomationEngine] Eager Parsing: {os.path.basename(file_path)}...")
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
    
    try:
        df.to_pickle(current_cache_path)
        print(f"💾 [AutomationEngine] Saved binary: {current_cache_name}")
    except Exception: pass
        
    return df

def is_file_cached(file_path: str, sheet_name=0) -> bool:
    """Utility to check if a specific version is already warmed up."""
    if not os.path.exists(file_path): return False
    mtime = os.path.getmtime(file_path)
    base_id = f"{file_path}_{sheet_name}".encode('utf-8')
    base_hash = hashlib.md5(base_id).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{base_hash}_{int(mtime)}.pkl")
    return os.path.exists(cache_path)

def normalize_sap_id(val: Any) -> str:
    return str(val).strip().replace('.0', '').lstrip('0')
