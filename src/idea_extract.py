# /src/idea_extract.py
#
# This script is now correctly configured to read the header row
# in 'idea_status_mapping.csv'.

import pandas as pd
from pathlib import Path
import sys

# --- SETUP: Ensure all our utility modules can be imported ---
try:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_root / 'src'))
    import api_client
    import data_processor
    import cache_manager
except ImportError as e:
    print(f"--- FATAL ERROR: Could not import a required module: {e} ---")
    sys.exit(1)

def load_status_mapping(filename: str) -> dict:
    """
    Loads a mapping from status ID to status name from a CSV file
    that has 'id' and 'status' columns in its header.
    """
    try:
        filepath = project_root / 'data' / filename
        print(f"--- Attempting to load status mapping from: {filepath} ---")
        
        # === THE FIX: Read the CSV using its existing header row ===
        # By default, read_csv uses the first row as the header.
        mapping_df = pd.read_csv(filepath)

        # Verify the required columns exist before proceeding
        if 'id' not in mapping_df.columns or 'status' not in mapping_df.columns:
            print(f"--- FATAL ERROR: Status mapping file must contain 'id' and 'status' columns. Found: {mapping_df.columns.tolist()} ---")
            sys.exit(1)
            
        # Create the dictionary using the actual column names from the file.
        status_map = pd.Series(mapping_df['status'].values, index=mapping_df['id']).to_dict()
        
        print(f"--- Successfully loaded {len(status_map)} status mappings. ---")
        return status_map
    except FileNotFoundError:
        print(f"--- FATAL ERROR: Status mapping file not found at '{filepath}'. ---")
        sys.exit(1)
    except Exception as e:
        print(f"--- FATAL ERROR while loading status mapping: {e} ---")
        sys.exit(1)

def load_group_mapping(filename: str) -> dict:
    """
    Loads the group ID to group name mapping, guaranteeing integer keys.
    """
    try:
        filepath = project_root / 'data' / filename
        # Read the CSV with simple column names
        mapping_df = pd.read_csv(filepath, header=None, names=['id', 'name'])

        # === THE DEFINITIVE FIX: A multi-step, robust conversion to integer keys ===
        # 1. Convert the 'id' column to a numeric type. If any ID isn't a number, it becomes NaN.
        mapping_df['id'] = pd.to_numeric(mapping_df['id'], errors='coerce')
        
        # 2. Drop any rows where the ID could not be converted to a number.
        mapping_df.dropna(subset=['id'], inplace=True)
        
        # 3. Now that we have only valid numbers, safely cast the 'id' column to integers.
        mapping_df['id'] = mapping_df['id'].astype(int)
        # ============================================================================

        # Create the dictionary from the clean DataFrame.
        group_map = pd.Series(mapping_df['name'].values, index=mapping_df['id']).to_dict()
        
        if group_map:
             print(f"--- Successfully loaded group map. Key data type is now: {type(next(iter(group_map.keys())))} ---")
        
        return group_map
    except Exception as e:
        print(f"--- FATAL ERROR while loading group mapping: {e} ---")
        sys.exit(1)

def extract_and_save_ideas():
    """
    Fetches ideas, enriches group, owner, and status, and saves to a CSV file.
    """
    print("\n--- Starting the idea extraction and enrichment process... ---")

    # === 1. LOAD ALL MAPPINGS ===
    group_map = load_group_mapping('group_mapping.csv')
    user_map = cache_manager.get_user_map_with_cache()
    status_map = load_status_mapping('idea_status_mapping.csv')

    # === 2. FETCH IDEA DATA FROM API ===
    select_fields = "id,title,status,ownerId,groupId"
    print(f"\n--- Requesting idea data from the API: {select_fields} ---")
    idea_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Ideas",
        select=select_fields
    )

    if not idea_data:
        print("--- No ideas found from API. Exiting. ---")
        return

    print(f"--- Successfully fetched {len(idea_data)} total ideas. ---")
    df = pd.DataFrame(idea_data)

    # === 3. ENFORCE DATA TYPES & ENRICH DATA ===
    print("\n--- Standardizing data types for all mapped columns... ---")
    # === THE FIX: Apply the data type conversion to ALL columns before mapping ===
    df['status'] = pd.to_numeric(df['status'], errors='coerce').astype('Int64')
    df['groupId'] = pd.to_numeric(df['groupId'], errors='coerce').astype('Int64')
    df['ownerId'] = pd.to_numeric(df['ownerId'], errors='coerce').astype('Int64')
    # ============================================================================
    
    if status_map:
        # The 'status' column from the API will be mapped using the dictionary
        # created from the 'id' and 'status' columns in your CSV.
        df['status'] = df['status'].map(status_map).fillna(df['status'])
        print("--- Successfully mapped Status IDs to Status Names. ---")

    if group_map:
        # df['groupId'] = df['groupId'].map(group_map).fillna(df['groupId'])
        # print("--- Successfully mapped Group IDs to Group Names. ---")
        mapped_groups = df['groupId'].map(group_map)
        df['groupId'] = mapped_groups.where(mapped_groups.notna(), df['groupId'])
        print("--- Successfully mapped Group IDs to Group Names. ---")
        
    if user_map:
        df['ownerId'] = df['ownerId'].map(user_map).fillna(df['ownerId'])
        print("--- Successfully mapped Owner IDs to Full Names. ---")

    # === 4. RENAME COLUMNS FOR FINAL OUTPUT ===
    column_map = {
        'id': 'idea_id',
        'title': 'idea_title',
        'status': 'idea_status',
        'ownerId': 'owner_name',
        'groupId': 'requester_organization'
    }
    df.rename(columns=column_map, inplace=True)

    # === 5. SAVE THE FINAL, FULLY ENRICHED DATA ===
    output_filename = project_root / 'data' / "all_ideas.csv"
    data_processor.save_to_csv(df, output_filename)

    print(f"\n--- Process complete. Fully enriched data saved to '{output_filename}'. ---")

if __name__ == "__main__":
    extract_and_save_ideas()
