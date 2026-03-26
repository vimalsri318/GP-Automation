import os
import pandas as pd

# Use relative paths for safety
CACHE_DIR = "Input Files/.cache"
Z_RECON_PKL = os.path.join(CACHE_DIR, "Z_Recon_Step3.pkl")

# We'll use the hash-based SO Listing from the cache folder
so_listing_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl') and not f.startswith('Z_Recon')]

if not os.path.exists(Z_RECON_PKL):
    print("❌ Z_Recon_Step3.pkl not found.")
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
unique_targets = set(targets_total.unique())
print(f"🎯 Unique SOs in Z-Recon Targets: {len(unique_targets)}")

for s_pkl in so_listing_files:
    s_df = pd.read_pickle(os.path.join(CACHE_DIR, s_pkl))
    s_cols = [c for c in s_df.columns if 'so' in c.lower() or 'sales' in c.lower()]
    if not s_cols: continue
    
    s_col = s_cols[0]
    print(f"🔎 Checking Master Cache: {s_pkl} (Column: {s_col})")
    
    s_df[s_col] = s_df[s_col].fillna("").astype(str).str.strip().str.upper().str.replace(r'\.0+$', '', regex=True).str.lstrip('0')
    master_keys = set(s_df[s_col].unique())
    master_keys.discard("")
    master_keys.discard("NAN")

    match_count = targets_total[targets_total.isin(master_keys)].count()
    print(f"✅ Synced Rows: {match_count} / {len(targets_total)}")
    
    if match_count < len(targets_total):
        missing = targets_total[~targets_total.isin(master_keys)].unique()
        print(f"❌ Sample Missing Keys (Raw): {missing[:5]}")
        
        # Test if they match if we don't lstrip '0'
        s_df_raw = pd.read_pickle(os.path.join(CACHE_DIR, s_pkl))
        s_raw_keys = set(s_df_raw[s_col].fillna("").astype(str).unique())
        no_strip_match = [k for k in missing if k in s_raw_keys]
        print(f"🤔 Matches without lstrip('0'): {len(no_strip_match)}")
