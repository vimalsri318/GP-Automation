import os
import pandas as pd

# The workspace root is the parent of app/ and Input Files/
CACHE_DIR = "app/backend/Input Files/.cache"
if not os.path.exists(CACHE_DIR):
    # Try alternate location if backend folder is flattened
    CACHE_DIR = "Input Files/.cache"

Z_RECON_PKL = os.path.join(CACHE_DIR, "Z_Recon_Step3.pkl")

# We'll use the hash-based SO Listing from the cache folder
so_listing_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl') and not f.startswith('Z_Recon')]

if not os.path.exists(Z_RECON_PKL):
    print(f"❌ Z_Recon_Step3.pkl not found in {Z_RECON_PKL}")
    exit()

z_df = pd.read_pickle(Z_RECON_PKL)
print(f"📊 Z-Recon Total Rows: {len(z_df)}")

# Filter targets like Step 4 does
z_so_col = [c for c in z_df.columns if 'so' in c.lower() or 'sales' in c.lower()][0]
z_df['__temp_so'] = z_df[z_so_col].fillna("").astype(str).str.strip().str.upper().str.replace(r'\.0+$', '', regex=True).str.lstrip('0')
z_df['__temp_so'] = z_df['__temp_so'].replace("NAN", "")

mask = (z_df['__temp_so'] != "")
targets_total = z_df[mask]['__temp_so']
print(f"🎯 Total SOs in Z-Recon Targets: {len(targets_total)}")

for s_pkl in so_listing_files:
    try:
        s_df = pd.read_pickle(os.path.join(CACHE_DIR, s_pkl))
        s_cols = [c for c in s_df.columns if 'so' in c.lower() or 'sales' in c.lower()]
        if not s_cols: continue
        
        s_col = s_cols[0]
        print(f"🔎 Checking Master Cache: {s_pkl} (Column: {s_col})")
        
        # Current Logic Count
        s_df_norm = s_df.copy()
        s_df_norm[s_col] = s_df_norm[s_col].fillna("").astype(str).str.strip().str.upper().str.replace(r'\.0+$', '', regex=True).str.lstrip('0')
        master_keys = set(s_df_norm[s_col].unique())
        master_keys.discard("")
        master_keys.discard("NAN")

        match_rows = targets_total[targets_total.isin(master_keys)].count()
        print(f"✅ Current Matches: {match_rows} / {len(targets_total)}")
        
        if match_rows < len(targets_total):
            missing = targets_total[~targets_total.isin(master_keys)].unique()
            print(f"❌ Sample Missing (First 5): {missing[:5]}")
            
            # --- HYPOTHESIS 1: The '.0' we are stripping was meaningful? ---
            # Test if those missing match if we ONLY lstrip '0' but don't replace '.0'
            s_df_alt1 = s_df.copy()
            s_df_alt1[s_col] = s_df_alt1[s_col].fillna("").astype(str).str.strip().str.upper().str.lstrip('0')
            alt1_keys = set(s_df_alt1[s_col].unique())
            alt_match1 = targets_total[targets_total.isin(alt1_keys)].count()
            print(f"🏁 Alt Matching (Keep Decimal): {alt_match1}")

            # --- HYPOTHESIS 2: Leading Zeros are meaningful? ---
            # Test if those missing match if we DON'T lstrip '0'
            s_df_alt2 = s_df.copy()
            s_df_alt2[s_col] = s_df_alt2[s_col].fillna("").astype(str).str.strip().str.upper().str.replace(r'\.0+$', '', regex=True)
            alt2_keys = set(s_df_alt2[s_col].unique())
            alt_match2 = targets_total[targets_total.isin(alt2_keys)].count()
            print(f"🏁 Alt Matching (Keep Leading Zero): {alt_match2}")
            
    except Exception as e:
        print(f"⚠️ Error reading {s_pkl}: {e}")
