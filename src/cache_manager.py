# /src/cache_manager.py
#
# This utility module handles caching mechanisms, starting with the user map.

import pandas as pd
import os
import time
import sys
from pathlib import Path
import api_client # Assumes api_client.py is in the same /src directory

# --- DEFINE CACHE CONSTANTS ---
# The cache file will be stored in the /data directory, one level above /src
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
CACHE_FILE_PATH = DATA_DIR / 'user_cache.csv'
CACHE_TTL_SECONDS = 2592000 # Cache is valid for 1 hour

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
        user_data = api_client.get_paged_align_data(
            endpoint="/rest/align/api/2/Users"
        )
        if not user_data:
            raise ValueError("No user data returned from API")

        full_df = pd.DataFrame(user_data)
        
        # Filter out records where 'fullName' is missing or just empty spaces
        full_df.dropna(subset=['fullName'], inplace=True)
        valid_df = full_df[full_df['fullName'].str.strip() != ''].copy()
        
        # Select ONLY the 'id' and 'fullName' columns for the clean cache
        clean_df = valid_df[['id', 'fullName']].copy()
        
        # Cache the small, clean DataFrame
        os.makedirs(DATA_DIR, exist_ok=True)
        clean_df.to_csv(CACHE_FILE_PATH, index=False)
        print(f"--- Successfully refreshed cache with {len(clean_df)} valid users. ---")
        
        return pd.Series(clean_df['fullName'].values, index=clean_df['id']).to_dict()

    except Exception as e:
        print(f"--- ERROR: Could not refresh user cache: {e} ---")
        if os.path.exists(CACHE_FILE_PATH):
            print("--- WARNING: Using STALE cache as a fallback. ---")
            df = pd.read_csv(CACHE_FILE_PATH)
            return pd.Series(df['fullName'].values, index=df['id']).to_dict()
        else:
            return {}
