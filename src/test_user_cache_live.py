# /src/test_user_cache_live.py
#
# FINAL ROBUST VERSION: This script now accepts the full user object from the API,
# filters it in memory, and then saves only the essential 'id' and 'fullName'
# columns to the cache.

import pandas as pd
import os
import time
import sys
from pathlib import Path

# --- 1. SETUP ---
try:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_root / 'src'))
    import api_client
except ImportError:
    print("--- FATAL ERROR: Could not import 'api_client'. ---")
    sys.exit(1)

# --- 2. DEFINE CACHE CONSTANTS ---
DATA_DIR = project_root / 'data'
CACHE_FILE_PATH = DATA_DIR / 'user_cache.csv'
CACHE_TTL_SECONDS = 10

# --- 3. THE FUNCTION TO BE TESTED ---
def get_user_map_with_cache() -> dict:
    """
    Gets the user ID-to-name map by fetching the full user object,
    filtering for valid records, and caching only the necessary fields.
    """
    if os.path.exists(CACHE_FILE_PATH):
        file_mod_time = os.path.getmtime(CACHE_FILE_PATH)
        if (time.time() - file_mod_time) < CACHE_TTL_SECONDS:
            print("--- Reading user map from FRESH cache file. ---")
            df = pd.read_csv(CACHE_FILE_PATH)
            return pd.Series(df['fullName'].values, index=df['id']).to_dict()

    print("--- User cache is STALE or MISSING. Fetching full objects from LIVE API... ---")
    
    try:
        # === THE NEW STRATEGY: Fetch the entire user object ===
        # We remove the 'select' parameter to make our intent clear.
        user_data = api_client.get_paged_align_data(
            endpoint="/rest/align/api/2/Users"
        )
        if not user_data:
            raise ValueError("No user data returned from the live API")

        print(f"\n--- API returned {len(user_data)} full user objects. ---")
            
        full_df = pd.DataFrame(user_data)
        
        # --- FILTERING STEP ---
        # First, filter out records with invalid 'fullName' fields.
        full_df.dropna(subset=['fullName'], inplace=True)
        valid_df = full_df[full_df['fullName'].str.strip() != ''].copy()
        
        print(f"--- Kept {len(valid_df)} records after filtering for valid fullNames. ---")

        # --- SELECTION STEP ---
        # Now, create a new, clean DataFrame with ONLY the columns we need to cache.
        clean_df = valid_df[['id', 'fullName']].copy()

        # --- CACHING STEP ---
        os.makedirs(DATA_DIR, exist_ok=True)
        # Save only the clean, small DataFrame to the cache file.
        clean_df.to_csv(CACHE_FILE_PATH, index=False)
        print(f"--- Successfully cached a CLEAN version with {len(clean_df)} users. ---")
        
        # Create the final map from the clean data.
        return pd.Series(clean_df['fullName'].values, index=clean_df['id']).to_dict()

    except Exception as e:
        print(f"--- ERROR: Could not refresh user cache from live API: {e} ---")
        if os.path.exists(CACHE_FILE_PATH):
            print("--- WARNING: Using STALE cache as a fallback. ---")
            df = pd.read_csv(CACHE_FILE_PATH)
            return pd.Series(df['fullName'].values, index=df['id']).to_dict()
        else:
            return {}

# --- 4. TEST RUNNER ---
if __name__ == "__main__":
    try:
        if os.path.exists(CACHE_FILE_PATH):
            os.remove(CACHE_FILE_PATH)
            print("--- Cleaned up old cache file. ---\n")
    except OSError as e:
        print(f"Error removing old cache file: {e}")

    print("====== SCENARIO 1: FETCH FULL OBJECT & FILTER ======")
    user_map = get_user_map_with_cache()
    print(f"Result: Got a map with {len(user_map)} valid users.")
    print("================================================\n")
