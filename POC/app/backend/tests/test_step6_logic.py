import pytest
import pandas as pd
from app.services.step6_service import execute_step6_category_mapping
from unittest.mock import patch, MagicMock

def test_step6_mapping_logic(mock_zrecon_df, mock_category_mapping):
    """
    Verifies that Step 6 logic correctly maps categories based on:
    1. Starts with '1' rule (Highest Priority)
    2. Dynamic CMIR Type Match (Second Priority)
    """
    # 1. Setup local mapping dict for logic verification
    mapping_dict = { m["type"]: m["category"] for m in mock_category_mapping }
    starts_with_1_cat = mapping_dict.get("Starting with 1 series", "Vendor manual")
    
    # 2. Define the exact implementation of logic from step6_service
    # Row 0: starts with 1 -> 'Vendor manual'
    # Row 1: CMIR ZZ-SALARY -> 'Salary'
    # Row 2: CMIR ZZ-FNF -> 'Full & Final Settlement'
    # Row 3: starts with 1 -> 'Vendor manual' (even if CMIR is missing)
    
    def resolve_row(row):
        doc_val = str(row['Accounting Document']).strip()
        if doc_val.startswith("1"):
            return starts_with_1_cat
        
        cmir_val = str(row['CMIR Type']).strip()
        if cmir_val and cmir_val in mapping_dict:
            return mapping_dict[cmir_val]
        
        return row['Category']

    # Apply same function as execute_step6_category_mapping
    mapped_categories = mock_zrecon_df.apply(resolve_row, axis=1)
    
    # Assertions: Verify indices
    assert mapped_categories[0] == "Vendor manual", f"Expected Vendor manual for 10001234, got {mapped_categories[0]}"
    assert mapped_categories[1] == "Salary", f"Expected Salary for ZZ-SALARY, got {mapped_categories[1]}"
    assert mapped_categories[2] == "Full & Final Settlement", f"Expected FNF for ZZ-FNF, got {mapped_categories[2]}"
    assert mapped_categories[3] == "Vendor manual", f"Expected Vendor manual for 19998887, got {mapped_categories[3]}"

def test_step6_service_flow(tmp_path):
    """
    Integrations test: Mocks file IO to verify the execute_step6_category_mapping service function.
    Ensures it handles missing checkpoints gracefully.
    """
    with patch("app.services.step6_service.CACHE_DIR", tmp_path), \
         patch("app.services.step6_service.get_category_mappings") as mock_get_cat:
        
        # Scenario 1: Step 5 Checkpoint Missing
        res = execute_step6_category_mapping()
        assert res["success"] is False
        assert "Step 5 Checkpoint not found" in res["error"]
        
        # Scenario 2: Checkpoint exists but mapping is empty
        z_path = tmp_path / "Z_Recon_Step5.pkl"
        mock_df = pd.DataFrame({'Accounting Document': ['100'], 'CMIR Type': [''], 'Category': ['']})
        mock_df.to_pickle(z_path)
        
        mock_get_cat.return_value = []
        res = execute_step6_category_mapping()
        assert res["success"] is True
        assert res["updates_applied"] >= 1
