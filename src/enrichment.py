# enrichment.py
#
# This module's purpose is to "enrich" data by fetching related details.

import api_client
import pandas as pd
from typing import Tuple
import os
import time
import sys

# Define the path to the cache file relative to the project root
# This assumes your project structure is /data, /src, etc.
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CACHE_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'users_cache.csv')
CACHE_TTL_SECONDS = 2592000 # 24 hours * 30 days


def get_release_titles_map(release_ids: list) -> dict:
    """
    ################DEPRECATION NOTICE################
    Fetches Release data from the API and returns a mapping of ID to Title.
    ReleaseID maps to ReleaseTitle.
    - Id = 54, Title = 2026Q1
    - Id = 55, Title = 2026Q2
    - Id = 56, Title = 2026Q3
    - Id = 57, Title = 2026Q4

    Args:
        release_ids: A list of unique integer IDs for the Releases (PIs).

    Returns:
        A dictionary mapping each Release ID to its title. e.g., {54: "2026Q1"}
    """
    if not release_ids:
        return {}

    print(f"--- Enriching data: Fetching titles for {len(release_ids)} Release IDs... ---")

    # Build the filter string: (id eq 54 or id eq 55 or ...)
    or_clauses = [f"id eq {rid}" for rid in release_ids]
    filters = f"({' or '.join(or_clauses)})"
    
    # We only need the id and title fields
    select_fields = "id,title"

    # Call the API to get the release details
    # NOTE: The endpoint is /Releases, which is the API name for Program Increments.
    release_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Releases",
        filters=filters,
        select=select_fields
    )

    # Create the mapping dictionary
    release_map = {item['id']: item['title'] for item in release_data}
    
    print("--- Enrichment complete. ---")
    return release_map

# =========================================================================
# === NEW FUNCTION TO GET FEATURE TITLES ===
# =========================================================================
def get_feature_titles_map(feature_ids: list) -> dict:
    """
    Fetches Feature data from the API and returns a mapping of ID to Title.

    Args:
        feature_ids: A list of unique integer IDs for the Features.

    Returns:
        A dictionary mapping each Feature ID to its title. e.g., {10806: "User Login V2"}
    """
    if not feature_ids:
        return {}

    print(f"--- Enriching data: Fetching titles for {len(feature_ids)} Feature IDs... ---")

    # Build the filter string: (id eq 10806 or id eq 10886 or ...)
    or_clauses = [f"id eq {fid}" for fid in feature_ids]
    filters = f"({' or '.join(or_clauses)})"
    
    select_fields = "id,title"

    # Call the API to get the feature details
    feature_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Features", # <-- Using the /Features endpoint
        filters=filters,
        select=select_fields
    )

    # Create the mapping dictionary
    feature_map = {item['id']: item.get('title', 'Title Not Found') for item in feature_data}
    
    print("--- Feature enrichment complete. ---")
    return feature_map

# =========================================================================
# === NEW FUNCTION TO GET EPIC DETAILS ===
# This encapsulates all the logic for fetching and defining Epics.
# =========================================================================
def get_epic_details(program_ids: list, release_ids: list) -> Tuple[pd.DataFrame, dict]:
    """
    Fetches Epic (Initiatives) details from program_id and release_id filters
    and returns a DataFrame and a column map.
    
    """
    print(f"--- Fetching Epic details for Programs: {program_ids} and Releases: {release_ids} ---")

    # --- Cohesion: All Epic-specific logic is now in one place ---
    select_fields = "id,title,state,ownerId,releaseIds,featureIds"
    column_map = {
        'id': 'initiative_id',
        'title': 'initiative_title',
       'state': 'initiative_state',
        'ownerId': 'owner_id',
       'releaseIds': 'release_ids',
        'featureIds': 'epic_id'
    }
    
    program_or_clauses = [f"primaryProgramId eq {pid}" for pid in program_ids]
    release_or_clauses = [f"(releaseIds/any(r: r eq {rid}))" for rid in release_ids]
    filters = f"({' or '.join(program_or_clauses)}) and ({' or '.join(release_or_clauses)})"
    
    epic_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Epics", filters=filters, select=select_fields
    )

    df = pd.DataFrame(epic_data) if epic_data else pd.DataFrame()
    return df, column_map




# =========================================================================
# === NEW FUNCTION TO GET FULL FEATURE DETAILS ===
# =========================================================================

def get_feature_details(feature_ids: list) -> Tuple[pd.DataFrame, dict]: # We now return a tuple
    """
    Fetches the full objects for a given list of Feature IDs and returns
    the data as a DataFrame along with a suggested column map.
    """
    # ... (code to get the list of feature_ids) ...
    if not feature_ids:
        return pd.DataFrame(), {}

    print(f"--- Fetching details for {len(feature_ids)} Feature IDs... ---")


    # --- Cohesion: select_fields and column_map are defined together ---
    select_fields = "id,title,state,parentId,releaseId"
    column_map = {
        'id': 'epic_id',
        'title': 'epic_title',
        'state': 'epic_state',
        'parentId': 'initiative_id',
        'releaseId': 'release_id'
    }
    # ----------------------------------------------------------------

    or_clauses = [f"id eq {fid}" for fid in feature_ids]
    filters = f"({' or '.join(or_clauses)})"
    
    feature_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Features", 
        filters=filters, 
        select=select_fields
    )

    df = pd.DataFrame(feature_data) if feature_data else pd.DataFrame()
    return df, column_map


# =========================================================================
# === REVISED FUNCTION TO GET DEPENDENCIES ===
# This function is the same as before, but we are re-confirming its purpose.
# =========================================================================
def get_dependencies_for_features(feature_ids: list) -> Tuple[pd.DataFrame, dict]:
    """
    Fetches all Dependency objects that are linked to a given list of Feature IDs.
    The fundation of this function is the GET anaplan.jiraalign.com/rest/align/api/2/Dependencies?filter=(featureId eq 10732 or featureId eq 10736)
    
    """
    if not feature_ids:
        return pd.DataFrame(), {}
    print(f"--- Enriching data: Fetching dependencies for {len(feature_ids)} Feature IDs... ---")


    select_fields = "id,title,releaseId,requestingTeamId,requestingProgramId,featureId,self"
    column_map = {
        'id': 'dependency_id',
        'title': 'dependency_title',
        'releaseId': 'release_id',
        'requestingTeamId': 'team_id',
        'requestingProgramId': 'workstream_id',
        'featureId': 'epic_id',
        'self':'request_url'
    }

    or_clauses = [f"featureId eq {fid}" for fid in feature_ids]
    filters = f"({' or '.join(or_clauses)})"

    # select_fields = "id,title,description,state,neededByDate,featureId"
    dependencies = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Dependencies",
        filters=filters,
        select=select_fields
    )
    print(f"--- Found {len(dependencies)} total dependencies. ---")
    df = pd.DataFrame(dependencies) if dependencies else pd.DataFrame()
    return df, column_map


def get_ideas(program_ids: list) -> Tuple[pd.DataFrame, dict]:
    """
    Fetches Idea details from the API, filtered by a list of program IDs,
    and returns a DataFrame and a column map.

    Args:
        program_ids: A list of unique integer IDs for the Programs.

    Returns:
        A tuple containing a DataFrame of the ideas and a dictionary 
        for column name mapping.
    """
    if not program_ids:
        return pd.DataFrame(), {}

    print(f"--- Fetching Idea details for Programs: {program_ids} ---")

    # Define the fields to select based on the provided JSON payload
    select_fields = "id,title,description,ownerId,createdBy,status,createDate,featureName,self"
    column_map = {
        'id': 'idea_id',
        'title': 'idea_title',
        'description': 'idea_description',
        'ownerId': 'owner_id',
        'createdBy': 'submitter_id',
        'status': 'idea_status',
        'createDate': 'create_date',
        'featureName': 'feature_name',
        'self': 'idea_url'
    }

    # Build the filter string for programs
    # Creates a filter like: (programId eq 123 or programId eq 456)
    program_or_clauses = [f"programId eq {pid}" for pid in program_ids]
    filters = f"({' or '.join(program_or_clauses)})"

    # Call the API to get the idea details
    idea_data = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Ideas",
        filters=filters,
        select=select_fields
    )

    # Convert to DataFrame
    df = pd.DataFrame(idea_data) if idea_data else pd.DataFrame()
    
    print(f"--- Found {len(df)} total ideas. ---")
    return df, column_map



def get_user_map_with_cache() -> dict:
    """
    Gets the user ID-to-name map by fetching the full user object,
    filtering for valid records, and caching only the necessary fields.
    """
    if os.path.exists(CACHE_FILE_PATH):
        file_mod_time = os.path.getmtime(CACHE_FILE_PATH)
        if (time.time() - file_mod_time) < CACHE_TTL_SECONDS:
            print("--- Reading user map from fresh cache. ---")
            df = pd.read_csv(CACHE_FILE_PATH)
            # The cache file is clean, so we can use it directly
            return pd.Series(df['fullName'].values, index=df['id']).to_dict()

    print("--- User cache is stale or missing. Fetching full objects from API... ---")
    
    try:
        # STEP 1: Fetch the entire user object, removing the 'select' param.
        user_data = api_client.get_paged_align_data(
            endpoint="/rest/align/api/2/Users"
        )
        if not user_data:
            raise ValueError("No user data returned from API")

        # Create a DataFrame from the full, raw data
        full_df = pd.DataFrame(user_data)

        # STEP 2: Filter the DataFrame to keep only valid records.
        # First, ensure the 'fullName' column exists.
        if 'fullName' not in full_df.columns:
            raise KeyError("The key 'fullName' was not found in the API response.")

        # Drop rows where 'fullName' is null/NaN or just empty spaces.
        full_df.dropna(subset=['fullName'], inplace=True)
        valid_df = full_df[full_df['fullName'].str.strip() != ''].copy()
        
        print(f"--- API returned {len(user_data)} records, kept {len(valid_df)} valid records after filtering. ---")

        # STEP 3: Select ONLY the 'id' and 'fullName' columns for caching.
        clean_df = valid_df[['id', 'fullName']].copy()
        
        # STEP 4: Cache the small, clean DataFrame.
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        clean_df.to_csv(CACHE_FILE_PATH, index=False)
        print(f"--- Successfully refreshed cache at '{CACHE_FILE_PATH}' with clean data. ---")

        # Create and return the final map from the clean data.
        return pd.Series(clean_df['fullName'].values, index=clean_df['id']).to_dict()

    except KeyError as e:
        # This will catch if the 'fullName' column doesn't exist at all.
        print(f"\n--- FATAL ERROR: The API response is missing a required column: {e}. ---")
        sys.exit(1)
    except Exception as e:
        print(f"--- ERROR: Could not refresh user cache: {e} ---")
        # Fallback to using the old (stale) cache if it exists
        if os.path.exists(CACHE_FILE_PATH):
            print("--- WARNING: Using stale cache as a fallback. ---")
            df = pd.read_csv(CACHE_FILE_PATH)
            return pd.Series(df['fullName'].values, index=df['id']).to_dict()
        else:
            # If there's no cache and the API fails, return empty.
            return {}