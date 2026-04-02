import os
import pandas as pd  # type: ignore
# from pathlib import Path

# Absolute paths
INPUT_DIR = "/Users/macbook/Downloads/Library/PROJECTS/Randstad/Untitled/POC/Input Files"

def verify_step2_bridge():
    z_path = os.path.join(INPUT_DIR, "Z Recon - 1st Feb to 26th Feb 2026 - Base File.XLSX")
    r_path = os.path.join(INPUT_DIR, "Revenue Dump - 1st to 26th Feb 2026.XLSX")
    i_path = os.path.join(INPUT_DIR, "Invoice Listing - 1st Jan to 28th Feb 2026.XLSX")
    
    # helper for column finding
    def get_col(df, *keywords):
        for kw in keywords:
            for c in df.columns:
                if kw.lower() in str(c).lower():
                    return c
        return None

    print("--- 1. Loading Z-Recon Sample ---")
    z_df = pd.read_excel(z_path, nrows=500) # Check 500 rows
    z_acc_col = get_col(z_df, "accounting document")
    z_so_col = get_col(z_df, "so number", "sales order")
    print(f"Z-Recon Columns: {list(z_df.columns)}")
    print(f"Z-Recon Found Cols: Acc={z_acc_col}, SO={z_so_col}")
    
    print("\n--- 2. Loading Revenue Dump Sample ---")
    # Revenue usually index 1
    r_df = pd.read_excel(r_path, sheet_name=1, nrows=500)
    r_doc_col = get_col(r_df, "document number", "doc. number")
    r_ref_col = get_col(r_df, "invoice no / reference key", "reference", "billing document", "invoice")
    print(f"Revenue Columns: {list(r_df.columns)}")
    print(f"Revenue Found Cols: Doc={r_doc_col}, Ref={r_ref_col}")
    
    print("\n--- 3. Loading Invoice Listing Sample ---")
    i_df = pd.read_excel(i_path, nrows=500)
    i_inv_col = get_col(i_df, "invoice no", "invoice", "billing document")
    i_so1_col = get_col(i_df, "sales order no", "so number 1", "sales order")
    print(f"Invoice Listing Columns: {list(i_df.columns)}")
    print(f"Invoice Found Cols: Inv={i_inv_col}, SO1={i_so1_col}")
    
    # Sample Bridge Attempt
    print("\n--- 4. Bridge Test ---")
    # Step A: Document Number -> Reference Map
    rev_map = {}
    if r_doc_col and r_ref_col:
        for _, row in r_df.dropna(subset=[r_doc_col]).iterrows():
            key = str(row[r_doc_col]).strip().replace('.0', '').lstrip('0')
            rev_map[key] = str(row[r_ref_col]).strip().replace('.0', '').lstrip('0')
    
    # Step B: Invoice Number -> SO Map
    inv_map = {}
    if i_inv_col and i_so1_col:
        for _, row in i_df.dropna(subset=[i_inv_col]).iterrows():
            key = str(row[i_inv_col]).strip().replace('.0', '').lstrip('0')
            inv_map[key] = str(row[i_so1_col]).strip().replace('.0', '')

    # Step C: Execution on Z-Recon sample
    matches: int = 0
    skips_starts_1: int = 0
    missing_so_count: int = 0
    
    for _, row in z_df.iterrows():
        acc_doc_raw = str(row[z_acc_col]).strip().replace('.0', '')
        acc_doc_norm = acc_doc_raw.lstrip('0')
        so_val = str(row.get(z_so_col, ''))
        
        if acc_doc_norm.startswith('1'):
            skips_starts_1 += 1
            continue
            
        if not so_val or so_val.lower() == 'nan':
            missing_so_count += 1
            
            # Bridge to Revenue
            invoice_ref = rev_map.get(acc_doc_norm)
            if invoice_ref:
                # Bridge to Invoice Listing
                final_so = inv_map.get(invoice_ref)
                if final_so:
                    matches += 1
                    if matches <= 5: # Debug first 5
                        print(f"  [SUCCESS] Z-Doc {acc_doc_norm} -> Rev-Ref {invoice_ref} -> SO {final_so}")
    
    print("\n--- Result on 500 rows ---")
    print(f"Skips (Starts 1): {skips_starts_1}")
    print(f"Missing SO Initially: {missing_so_count}")
    print(f"Resolved Successfully: {matches}")

if __name__ == "__main__":
    verify_step2_bridge()
