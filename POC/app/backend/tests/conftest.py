import pytest
import os
import sys

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_zrecon_df():
    """Returns a basic Z-Recon DataFrame for mapping tests."""
    import pandas as pd
    data = {
        'Month': ['Feb 2026', 'Feb 2026', 'Feb 2026', 'Feb 2026'],
        'Accounting Document': ['10001234', '50009876', '20005555', '19998887'],
        'CMIR Type': ['', 'ZZ-SALARY', 'ZZ-FNF', ''],
        'Category': ['', '', '', ''],
        'SO No.': ['SO123', 'SO456', 'SO789', 'SO000']
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_category_mapping():
    """Returns a mock mapping list similar to what get_category_mappings returns."""
    return [
        {"type": "Starting with 1 series", "category": "Vendor manual"},
        {"type": "ZZ-SALARY", "category": "Salary"},
        {"type": "ZZ-FNF", "category": "Full & Final Settlement"}
    ]
