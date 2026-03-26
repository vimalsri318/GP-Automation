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
    """Retrieves high-speed binary with high-resolution performance logging."""
    import time
    start_all = time.perf_counter()
    
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
        
    mtime = os.path.getmtime(file_path)
    base_id = f"{file_path}_{sheet_name}".encode('utf-8')
    base_hash = hashlib.md5(base_id).hexdigest()
    current_cache_name = f"{base_hash}_{int(mtime)}.pkl"
    current_cache_path = os.path.join(CACHE_DIR, current_cache_name)
    
    # Binary Cache Phase
    import glob
    if os.path.exists(current_cache_path):
        try:
            start_load = time.perf_counter()
            df = pd.read_pickle(current_cache_path)
            end_load = time.perf_counter()
            print(f"✅ [PERF] Binary Hit: {os.path.basename(file_path)} | Load Time: {int((end_load - start_load) * 1000)}ms")
            return df
        except Exception as e:
            print(f"⚠️ [PERF] Cache Malfunction ({e}), falling back to Excel.")

    # HOUSEKEEPING: Delete old versions of this specific data source before generating a new one
    old_versions = glob.glob(os.path.join(CACHE_DIR, f"{base_hash}_*.pkl"))
    for old_file in old_versions:
        try:
            os.remove(old_file)
            print(f"🧹 [AutoPurge] Cleaned old cache: {os.path.basename(old_file)}")
        except Exception: pass

    # Excel Parsing Phase (The Bottleneck)
    print(f"🚀 [PERF] First-Time Excel Read: {os.path.basename(file_path)} (Engine: {engine})...")
    start_parse = time.perf_counter()
    
    # FORCED STRINGS: Accounting IDs must never be floats
    # This prevents '123' from becoming '123.0'
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine, dtype=str)
    except Exception:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)

    end_parse = time.perf_counter()
    duration_ms = int((end_parse - start_parse) * 1000)
    print(f"⏱️ [PERF] Excel Parsed: {os.path.basename(file_path)} | Time: {duration_ms}ms")
    
    try:
        df.to_pickle(current_cache_path)
    except Exception: pass
        
    return df

def warmup_all_files(file_paths: List[str]):
    """Aggressively warms up all master files in parallel using multi-threading."""
    from concurrent.futures import ThreadPoolExecutor
    import time
    
    start = time.time()
    print(f"⚡ [AutomationEngine] Starting Multi-Threaded Warmup of {len(file_paths)} files...")
    
    with ThreadPoolExecutor(max_workers=min(len(file_paths), 8)) as executor:
        # We explicitly use 'calamine' here as it's the fastest for first-time reads
        executor.map(lambda p: get_cached_dataframe(p, engine='calamine'), file_paths)
        
    end = time.time()
    print(f"✨ [AutomationEngine] Parallel Warmup Complete in {end - start:.2f} seconds.")

def is_file_cached(file_path: str, sheet_name=0) -> bool:
    """Utility to check if a specific version is already warmed up."""
    if not os.path.exists(file_path): return False
    mtime = os.path.getmtime(file_path)
    base_id = f"{file_path}_{sheet_name}".encode('utf-8')
    base_hash = hashlib.md5(base_id).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{base_hash}_{int(mtime)}.pkl")
    return os.path.exists(cache_path)

import queue
import threading
import time

class GlobalAuditManager:
    """Manages sequential Excel audit writes to prevent race conditions."""
    _instance = None
    _queue = queue.Queue()
    _worker_thread = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if GlobalAuditManager._worker_thread is None:
            GlobalAuditManager._worker_thread = threading.Thread(target=self._worker, daemon=True)
            GlobalAuditManager._worker_thread.start()

    def _worker(self):
        while True:
            # Blocks until a task is available
            task_fn, args = self._queue.get()
            try:
                print(f"👷 [AuditManager] Starting background task: {task_fn.__name__}...")
                task_fn(*args)
            except Exception as e:
                print(f"❌ [AuditManager] Task Failed: {e}")
            finally:
                self._queue.task_done()

    def submit(self, fn, *args):
        self._queue.put((fn, args))
        print(f"📥 [AuditManager] Task queued: {fn.__name__} (Queue size: {self._queue.qsize()})")

def get_audit_manager():
    return GlobalAuditManager.get_instance()

def normalize_sap_id(val: Any) -> str:
    return str(val).strip().replace('.0', '').lstrip('0')
