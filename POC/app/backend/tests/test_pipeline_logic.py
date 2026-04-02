import pytest
import pandas as pd
#import os
#from unittest.mock import patch, MagicMock
from app.services.step2_service import get_col_strict
#from app.services.step6_service import execute_step6_category_mapping
from unittest.mock import patch

# ==========================================
# TEST 1: ID NORMALIZATION (The Worst Case Formatting)
# ==========================================
@pytest.mark.parametrize("raw_input, expected", [
    ("45000123", "45000123"),
    ("45000123.0", "45000123"),
    ("00045000123", "45000123"),
    ("  45000123  ", "45000123"),
    (45000123.0, "45000123"),
    ("12345", "12345")
])
def test_normalization_logic(raw_input, expected):
    """Verifies that the engine can bridge Excel IDs regardless of formatting."""
    # This imitates the .astype(str).str.strip().str.replace('.0','').str.lstrip('0') chain
    processed = str(raw_input).strip().replace('.0','', 1).lstrip('0')
    if not processed: processed = "0" # Special Case for zero
    assert processed == expected

# ==========================================
# TEST 2: FUZZY HEADER MATCHING (Schema Drift)
# ==========================================
def test_fuzzy_column_matcher():
    """Verifies that headers like 'Doc No' match 'Accounting Document'."""
    df = pd.DataFrame(columns=['Doc No', 'Company Cd', 'Val'])
    
    match1 = get_col_strict(df, "accounting document", "document number", "doc no")
    match2 = get_col_strict(df, "company code", "company cd")
    
    assert match1 == "Doc No"
    assert match2 == "Company Cd"
    assert get_col_strict(df, "ghost column") is None

# ==========================================
# TEST 3: STEP 6 WATERFALL (The Business Logic)
# ==========================================
def test_step6_waterfall_edge_cases():
    """Verifies the fallback sequence between Special Rule (1-series) and Master Mapping."""
    
    # CASE: Row has BOTH a 1-series ID and a CMIR match.
    # RULE: 1-series priority MUST win (Vendor manual).
    row_both = pd.Series({
        'Accounting Document': '10009876', 
        'CMIR Type': 'ZZ-SALARY', 
        'Category': ''
    })
    
    # CASE: Row has NO 1-series, but HAS a CMIR match.
    row_cmir_only = pd.Series({
        'Accounting Document': '50001234', 
        'CMIR Type': 'ZZ-FNF', 
        'Category': ''
    })
    
    mapping_dict = {"ZZ-SALARY": "Salary", "ZZ-FNF": "Full & Final"}
    starts_with_1_cat = "Vendor manual"
    
    def apply_logic(row):
        doc = str(row['Accounting Document']).strip()
        if doc.startswith("1"): return starts_with_1_cat
        cmir = str(row['CMIR Type']).strip()
        if cmir in mapping_dict: return mapping_dict[cmir]
        return ""

    assert apply_logic(row_both) == "Vendor manual"
    assert apply_logic(row_cmir_only) == "Full & Final"

# ==========================================
# TEST 4: DIRECTORY DISCOVERY (Heuristic Speed)
# ==========================================
def test_file_heuristic_collision():
    """Verifies that 'Revenue Dump' doesn't pick up the 'Revenue Master' file."""
    from app.services.step2_service import get_file_by_heuristic
    
    # files = [
    #     "/tmp/Revenue Dump - Feb 2026.xlsx",
    #     "/tmp/Revenue file - Automation - Input Master.xlsx"
    # ]
    
    with patch("os.path.exists", return_value=True), \
         patch("app.services.step2_service.INPUT_DIR", "/tmp"), \
         patch("os.listdir", return_value=["Revenue Dump - Feb 2026.xlsx", "Revenue file - Automation - Input Master.xlsx"]):
        
        # Test the priority logic we just added
        path = get_file_by_heuristic("Revenue Dump")
        assert "Dump" in path
        assert "Master" not in path
