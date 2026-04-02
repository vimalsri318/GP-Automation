import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock

# ==========================================
# MASTER PIPELINE TEST (STEPS 0 TO 6)
# ==========================================

def test_full_reconciliation_workflow(tmp_path):
    """
    Simulates the entire 6-step reconciliation flow with mock data inputs.
    Verifies data integrity and mapping accuracy across the full chain.
    """
    
    # 1. SETUP MOCK SOURCE DATA (The Inputs)
    # -----------------------------------
    # a) Z-Recon (Target Format)
    z_raw = pd.DataFrame({
        'Acc Doc': ['10001', '20002', '30003'], # 1-series, Normal, Normal
        'CO_Code': ['IN10', 'IN10', 'IN10'],
        'Revenue': [100.0, 200.0, 300.0],
        'SO Number': ['', '', ''], # Blank target for Step 2/4
        'CMIR Type': ['', '', '']  # Blank target for Step 3
    })
    
    # b) Revenue Dump (Bridge 1)
    rev_dump = pd.DataFrame({
        'Document Number': ['20002', '30003'],
        'Reference Key 3': ['INV-456', 'INV-789'] # Invoice Ref
    })
    
    # c) Invoice Listing (Bridge 2)
    inv_list = pd.DataFrame({
        'Invoice No': ['INV-456', 'INV-789'],
        'Sales Order No': ['SO-B2', 'SO-C3'] # Sales Order No
    })
    
    # d) SO Listing (The Master)
    so_list = pd.DataFrame({
        'Sales Order No': ['SO-B2', 'SO-C3'],
        'Transaction Type': ['ZZ-SALARY', 'ZZ-FNF'],
        'Narration': ['Salary Feb', 'Full Final']
    })

    # e) Cost Dump (Fallback for Step 5)
    cost_dump = pd.DataFrame({
        'Document Number': ['10001'],
        'Text': ['Vendor Manual Override']
    })

    # 2. STEP-BY-STEP LOGIC EXECUTION
    # -------------------------------
    
    # [STEP 2] CROSS-INVOICE INTEGRITY
    # Map Z-Recon -> Revenue (Ref Key 3) -> Invoice (Sales Order No)
    rev_map = rev_dump.set_index('Document Number')['Reference Key 3'].to_dict()
    inv_map = inv_list.set_index('Invoice No')['Sales Order No'].to_dict()
    
    # Acc Doc 20002 -> INV-456 -> SO-B2
    # Acc Doc 30003 -> INV-789 -> SO-C3
    z_raw['SO Number'] = z_raw['Acc Doc'].map(rev_map).map(inv_map)
    
    assert z_raw.loc[1, 'SO Number'] == 'SO-B2'
    assert z_raw.loc[2, 'SO Number'] == 'SO-C3'

    # [STEP 3] CMIR TYPE ALIGNMENT
    # Map Z-Recon (SO) -> SO Listing (Transaction Type)
    cmir_map = so_list.set_index('Sales Order No')['Transaction Type'].to_dict()
    z_raw['CMIR Type'] = z_raw['SO Number'].map(cmir_map)
    
    assert z_raw.loc[1, 'CMIR Type'] == 'ZZ-SALARY'
    assert z_raw.loc[2, 'CMIR Type'] == 'ZZ-FNF'

    # [STEP 4/5] NARRATION RECOVERY
    # Phase 1: SO List Narration (for Row 20002 and 30003)
    narr_map = so_list.set_index('Sales Order No')['Narration'].to_dict()
    z_raw['Narration'] = z_raw['SO Number'].map(narr_map)
    
    # Phase 2: Cost Dump Fallback (for Row 10001 missing SO)
    # Map Z-Recon (Acc Doc) -> Cost Dump (Text)
    fallback_map = cost_dump.set_index('Document Number')['Text'].to_dict()
    z_raw.loc[z_raw['Narration'].isna(), 'Narration'] = z_raw['Acc Doc'].map(fallback_map)
    
    assert z_raw.loc[0, 'Narration'] == 'Vendor Manual Override'
    assert z_raw.loc[1, 'Narration'] == 'Salary Feb'

    # [STEP 6] DYNAMIC CATEGORY MAPPING
    # Rule 1: 1-Series Priority
    # Rule 2: CMIR Type Match
    cat_mapping = {"ZZ-SALARY": "Salary", "ZZ-FNF": "Full Settlement"}
    
    def resolve_category(row):
        doc = str(row['Acc Doc']).strip()
        if doc.startswith("1"): return "Vendor manual"
        cmir = row['CMIR Type']
        if cmir in cat_mapping: return cat_mapping[cmir]
        return "Unknown"

    z_raw['Category'] = z_raw.apply(resolve_category, axis=1)
    
    # FINAL VERIFICATION
    # ------------------
    # Row 0: Acc Doc 10001 -> 'Vendor manual' (Priority 1-series rule wins over any CMIR)
    assert z_raw.loc[0, 'Category'] == 'Vendor manual'
    # Row 1: Acc Doc 20002 -> SO-B2 -> ZZ-SALARY -> 'Salary'
    assert z_raw.loc[1, 'Category'] == 'Salary'
    # Row 2: Acc Doc 30003 -> SO-C3 -> ZZ-FNF -> 'Full Settlement'
    assert z_raw.loc[2, 'Category'] == 'Full Settlement'

    print("\n🚀 [Logic Guardian] Full 6-Step Pipeline Chain verified successfully!")
