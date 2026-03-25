import os
import pandas as pd  # type: ignore
from typing import Dict, Any
from pathlib import Path
from config import BASE_DIR  # type: ignore
from app.services.automation_engine import (
    get_cached_dataframe, 
    normalize_sap_id, 
    get_col_from_df,
    INPUT_DIR,
    PROJECT_ROOT,
    CACHE_DIR
)

def get_system_files() -> list:
    """Returns the list of 5 required files tracked by the system."""
    if not os.path.exists(INPUT_DIR):
        return []
    
    files = []
    # Use os.listdir in the project root or Input Files
    search_dirs = [INPUT_DIR, str(PROJECT_ROOT)]
    seen_files = set()
    
    for d in search_dirs:
        if not os.path.exists(d): continue
        for f in os.listdir(d):
            if f in seen_files: continue
            if not f.startswith("~$") and (f.lower().endswith('.xlsx') or f.lower().endswith('.xls')):
                try:
                    size = os.path.getsize(os.path.join(d, f))
                    card_type = "Z Recon" if "Z Recon" in f else "Revenue Dump" if "Revenue" in f else "Cost Dump" if "Cost" in f else "Invoice Listing" if "Invoice" in f else "SO Listing" if "SO" in f else "Other"
                    files.append({
                        "name": f,
                        "size_kb": round(float(size / 1024.0), 1), # type: ignore
                        "type": card_type,
                        "status": "Ready",
                    })
                    seen_files.add(f)
                except Exception:
                    pass
    return files

def get_file_by_heuristic(prefix: str):
    """Discovers a file across both Root and Input Files with fallback matching."""
    search_dirs = [INPUT_DIR, str(PROJECT_ROOT)]
    files_in_dir = []
    for d in search_dirs:
        if os.path.exists(d):
            files_in_dir.extend([os.path.join(d, f) for f in os.listdir(d) if not f.startswith("~$") and "_Resolved" not in f])
    
    # Heuristic Discovery
    if prefix == "Revenue Dump":
        file_path = next((f for f in files_in_dir if "revenue" in os.path.basename(f).lower()), None)
    elif prefix == "Cost":
        file_path = next((f for f in files_in_dir if "cost" in os.path.basename(f).lower()), None)
    else:
        file_path = next((f for f in files_in_dir if prefix.lower() in os.path.basename(f).lower()), None)
        
    if not file_path:
        raise Exception(f"Missing {prefix} source file.")
    return file_path

def parse_zrecon() -> Dict[str, Any]:
    try:
        file_path = get_file_by_heuristic("Z Recon")
        z_df = get_cached_dataframe(file_path, engine='openpyxl')
        
        # Valid data rows usually have a Company Code
        co_col = get_col_from_df(z_df, "company code")
        if co_col:
            z_df = z_df[z_df[co_col].notna()]
            
        rev_col = get_col_from_df(z_df, "revenue")
        cost_col = get_col_from_df(z_df, "cost")
        
        z_rev = pd.to_numeric(z_df[rev_col], errors='coerce').fillna(0).sum() if rev_col else 0.0
        z_cost = pd.to_numeric(z_df[cost_col], errors='coerce').fillna(0).sum() if cost_col else 0.0
        
        return {
            "success": True, 
            "data": {
                "revenue": round(float(z_rev), 2),  # type: ignore
                "cost": round(float(z_cost), 2)  # type: ignore
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed parsing Z-Recon: {str(e)}"}

def extract_programmatic_pivots(df: pd.DataFrame, source_type: str) -> tuple[float, int, bool, list]:
    """
    Simulates the 3 required SAP pivots: Entity (Company Code), Deputee (Material), and Contract Code.
    Validates that the raw data mathematically aggregates to the exact same total across all 3 dimensions.
    """
    col_str = {c: str(c).strip().lower() for c in df.columns}
    
    # Identify required grouping columns
    company_col = next((c for c, l in col_str.items() if "company" in l), None)
    material_col = next((c for c, l in col_str.items() if "material" in l), None)
    
    if source_type == "Revenue Dump":
        contract_col = next((c for c, l in col_str.items() if "reference key 3" in l), None) 
    else:
        # Cost dump
        contract_col = next((c for c, l in col_str.items() if "cc" == l or "text" in l), None)
        
    # 3. Use Synonym Mapping to find the math total column
    sum_col = get_col_from_df(df, "general ledger amount", "revenue", "cost", "value")
    
    if not sum_col:
        raise Exception(f"Mathematical sum column not found for {source_type}.")
        
    df[sum_col] = pd.to_numeric(df[sum_col], errors='coerce').fillna(0)
    
    # Globally strip the SAP ALV phantom "Grand Total" row from the parsed matrix
    if company_col:
        df = df[df[company_col].notna()]
    
    totals = []
    pivot_breakdowns = []
    
    def add_pivot(dimension_name, col_name):
        if not col_name: return
        grouped = df.groupby(col_name, dropna=False)[sum_col].sum()
        total_sum = float(grouped.sum())
        
        # Serialize breakdown sorted by absolute magnitude natively
        breakdown = [{"key": str(k), "amount": round(float(v), 2)} for k, v in grouped.items() if float(v) != 0.0]  # type: ignore
        breakdown.sort(key=lambda x: abs(float(x["amount"])), reverse=True)
        
        pivot_breakdowns.append({
            "dimension": dimension_name,
            "total": round(float(total_sum), 2),  # type: ignore
            "values": breakdown[:100] # type: ignore
        })
        totals.append(total_sum)

    # 1. Entity Wise
    add_pivot("Entity (Company Code)", company_col)
    # 2. Deputee Wise
    add_pivot("Deputee (Material)", material_col)
    # 3. Contract Code Wise
    add_pivot("Contract Code (Ref Key 3 / Text)", contract_col)
        
    if totals:
        true_total = totals[0]
        is_consistent = all(abs(t - true_total) < 50 for t in totals)
        return true_total, len(totals), is_consistent, pivot_breakdowns
    else:
        baseline = float(df[sum_col].sum())
        return baseline, 0, True, []

def parse_revenue() -> Dict[str, Any]:
    try:
        file_path = get_file_by_heuristic("Revenue Dump")
        # Engine calamine reads huge files 100x faster!
        r_df = get_cached_dataframe(file_path, sheet_name=1, engine='calamine') 
        
        # Programmatically validate the 3 required Data Pivots: Entity, Deputee, Contract Code
        r_sum, pivot_count, is_consistent, pivots = extract_programmatic_pivots(r_df, "Revenue Dump")
        
        return {
            "success": True, 
            "data": {
                "revenue_sum": round(float(r_sum), 2),  # type: ignore
                "pivot_count": pivot_count,
                "pivots_consistent": is_consistent,
                "pivots": pivots
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed parsing Revenue Dump: {str(e)}"}

def parse_cost() -> Dict[str, Any]:
    try:
        file_path = get_file_by_heuristic("Cost")
        c_df = get_cached_dataframe(file_path, sheet_name=1, engine='calamine')
        
        # Programmatically validate the 3 required Data Pivots
        c_sum, pivot_count, is_consistent, pivots = extract_programmatic_pivots(c_df, "Cost Dump")
        
        return {
            "success": True, 
            "data": {
                "cost_sum": round(float(c_sum), 2),  # type: ignore
                "pivot_count": pivot_count,
                "pivots_consistent": is_consistent,
                "pivots": pivots
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed parsing Cost Dump: {str(e)}"}

def cross_invoice_integrity() -> Dict[str, Any]:
    """
    Step 2: Cross Invoice Integrity Workflow
    Scans and links physical invoice aggregates across files to resolve missing SO Numbers.
    """
    try:
        # Load Z Recon aggressively compressed base
        z_path = get_file_by_heuristic("Z Recon")
        z_df = get_cached_dataframe(z_path, engine='openpyxl')
        
        # Load Revenue Dump Cache
        r_path = get_file_by_heuristic("Revenue Dump")
        r_df = get_cached_dataframe(r_path, sheet_name=1, engine='calamine')
        
        # Load Invoice Listing Cache
        i_path = get_file_by_heuristic("Invoice")
        i_df = get_cached_dataframe(i_path, engine='openpyxl') 
        
        print(f"DEBUG: Revenue Cols = {list(r_df.columns)}")
        print(f"DEBUG: Invoice Cols = {list(i_df.columns)}")
        
        def get_col(df, *keywords):
            # First pass: Exact match (preventing Reference Key 1 vs Reference Key issue)
            for kw in keywords:
                for c in df.columns:
                    if kw.lower() == str(c).lower().strip():
                        return c
            # Second pass: Fuzzy match
            for kw in keywords:
                for c in df.columns:
                    if kw.lower() in str(c).lower():
                        return c
            return None
            
        z_acc_col = get_col(z_df, "accounting document")
        z_so_col = get_col(z_df, "so number", "sales order")
        
        if not z_acc_col:
            raise Exception("Cannot find Accounting Document column in Z Recon file.")
            
        r_doc_col = get_col(r_df, "document number", "doc. number")
        # Strict mapping to 'Reference Key' to avoid 'Reference Key 1'
        r_ref_col = get_col(r_df, "reference key", "invoice no / reference key")
        
        # Priority on "Invoice No" as explicitly requested by user
        i_inv_col = get_col(i_df, "invoice no", "invoice", "billing document")
        
        # Final SO resolution mapping
        i_so1_col = get_col(i_df, "sales order no", "sales order inv number", "sales order")
        i_so2_col = get_col(i_df, "so number2", "so number 2")
        
        # 1. Prepare Revenue Lookup (Document Number -> Reference Key) for instant index mapping
        rev_map = {}
        if r_doc_col and r_ref_col:
            rev_subset = r_df[[r_doc_col, r_ref_col]].dropna(subset=[r_doc_col])
            # Normalize key: stringify, strip decimals and LEADING ZEROS
            rev_subset[r_doc_col] = rev_subset[r_doc_col].astype(str).str.strip().str.replace('.0', '', regex=False).str.lstrip('0')
            rev_map = rev_subset.set_index(r_doc_col)[r_ref_col].to_dict()
            
        # 2. Prepare Invoice Lookup (Invoice -> SO Number dual fallback)
        inv_map = {}
        if i_inv_col:
            inv_subset = i_df.dropna(subset=[i_inv_col]).copy()
            inv_subset[i_inv_col] = inv_subset[i_inv_col].astype(str).str.strip().str.replace('.0', '', regex=False).str.lstrip('0')
            
            for _, row in inv_subset.iterrows():
                so_val = None
                # Primary SO
                if i_so1_col and pd.notna(row[i_so1_col]) and str(row[i_so1_col]).strip() not in ('', 'nan'):
                    so_val = row[i_so1_col]
                # Fallback SO
                elif i_so2_col and pd.notna(row[i_so2_col]) and str(row[i_so2_col]).strip() not in ('', 'nan'):
                    so_val = row[i_so2_col]
                
                inv_map[str(row[i_inv_col])] = so_val
            
            with open("sap_bridge.log", "w") as f:
                f.write(f"DEBUG: rev_map keys (first 5) = {list(rev_map.keys())[:5]}\n")  # type: ignore
                f.write(f"DEBUG: rev_map values (first 5) = {list(rev_map.values())[:5]}\n")  # type: ignore
                f.write(f"DEBUG: inv_map keys (first 5) = {list(inv_map.keys())[:5]}\n")  # type: ignore
                f.write(f"DEBUG: Current col mapping: R_REF={r_ref_col}, I_INV={i_inv_col}, I_SO1={i_so1_col}\n")
                
        # 3. Update Z-Recon Native DataFrame
        if not z_so_col:
            z_so_col = "SO Number"
            z_df[z_so_col] = None
            
        metrics = {
            "starts_with_one": 0,
            "candidates": 0,
            "already_has_so": 0,
            "missing_so_candidates": 0,
            "found_in_revenue": 0,
            "missing_in_revenue": 0,
            "found_in_invoice_listing": 0,
            "missing_in_invoice_listing": 0,
            "updates_applied": 0,
        }
        
        z_df[z_acc_col] = z_df[z_acc_col].astype(str)
        
        # Target only Accounting Documents that DO NOT start with '1'
        for idx, row in z_df.iterrows():
            acc_doc_raw = str(row[z_acc_col]).strip().replace('.0', '')
            acc_doc_norm = acc_doc_raw.lstrip('0')
            
            if acc_doc_raw and acc_doc_raw != 'nan':
                if acc_doc_norm.startswith('1'):
                    metrics["starts_with_one"] += 1
                else:
                    metrics["candidates"] += 1
                    
                    # We only populate if it's currently missing
                    if pd.isna(row.get(z_so_col)) or str(row.get(z_so_col)).strip() in ('', 'nan'):
                        metrics["missing_so_candidates"] += 1
                        
                        # Lookup 1: Get raw Invoice reference from Revenue memory matrix
                        invoice_str = str(rev_map.get(acc_doc_norm, '')).strip().replace('.0', '').lstrip('0')  # type: ignore
                        
                        if invoice_str and invoice_str != 'nan':
                            metrics["found_in_revenue"] += 1
                            # Lookup 2: Get SO resolution from Invoice map
                            so_resolved = inv_map.get(invoice_str)
                            if so_resolved and str(so_resolved).strip() != 'nan':
                                metrics["found_in_invoice_listing"] += 1
                                z_df.at[idx, z_so_col] = so_resolved
                                metrics["updates_applied"] += 1
                            else:
                                metrics["missing_in_invoice_listing"] += 1
                        else:
                            metrics["missing_in_revenue"] += 1
                    else:
                        metrics["already_has_so"] += 1
                        
        # Save enriched sequential dataframe via safe caching proxy for subsequent Pipeline workflows!
        target_path = os.path.join(CACHE_DIR, "Z_Recon_Step2.pkl")
        z_df.to_pickle(target_path)
        
        # Also create a physical Excel duplicate as requested for direct user audit
        try:
            excel_out = os.path.join(os.path.dirname(z_path), "Z_Recon_Step2_Resolved.xlsx")
            z_df.to_excel(excel_out, index=False)
            print(f"DEBUG: Exported resolved Excel to {excel_out}")
        except Exception as e:
            print(f"DEBUG: Failed Excel export: {e}")
        
        return {
            "success": True, 
            "data": {
                "total_rows": len(z_df),
                "process_steps": [
                    {"label": "Filter Z-Recon Baseline", "detail": f"Skipped {metrics['starts_with_one']} docs starting with '1'"},
                    {"label": "Identify Missing Data", "detail": f"Found {metrics['missing_so_candidates']} rows needing SO resolution"},
                    {"label": "Revenue Dump Bridge", "detail": f"Matched {metrics['found_in_revenue']} docs to Revenue references"},
                    {"label": "Invoice Listing Resolution", "detail": f"Resolved {metrics['found_in_invoice_listing']} unique SO numbers"},
                    {"label": "Final Integrity Injection", "detail": f"Populated {metrics['updates_applied']} new values into Z-Recon"}
                ],
                "starts_with_one": metrics["starts_with_one"],
                "candidates": metrics["candidates"],
                "already_has_so": metrics["already_has_so"],
                "missing_so_candidates": metrics["missing_so_candidates"],
                "found_in_revenue": metrics["found_in_revenue"],
                "missing_in_revenue": metrics["missing_in_revenue"],
                "found_in_invoice_listing": metrics["found_in_invoice_listing"],
                "missing_in_invoice_listing": metrics["missing_in_invoice_listing"],
                "updates_applied": metrics["updates_applied"],
                "unresolved_misses": metrics["missing_in_revenue"] + metrics["missing_in_invoice_listing"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
