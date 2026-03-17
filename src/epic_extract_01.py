# epic_extract_01.py

import api_client
import data_processor
from enrichment import get_release_titles_map, get_feature_titles_map 

def run_extraction_pipeline(program_ids: list, release_ids: list):
    """
    Extracts Epics(Initiatives) and enriches the data by adding Release and Feature Titles,
    while keeping the original ID columns.
    """
    print(f"--- Starting Epic extraction for Programs: {program_ids} and Releases: {release_ids} ---")

    # --- Step 1: Build filter and fetch main Epic data ---
    program_or_clauses = [f"primaryProgramId eq {pid}" for pid in program_ids]
    program_filter_part = f"({' or '.join(program_or_clauses)})"
    release_or_clauses = [f"(releaseIds/any(r: r eq {rid}))" for rid in release_ids]
    release_filter_part = f"({' or '.join(release_or_clauses)})"
    my_filters = f"{program_filter_part} and {release_filter_part}"
    my_fields = "id,title,primaryProgramId,releaseIds,featureIds,state,ownerId"
    
    epics = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Epics", filters=my_filters, select=my_fields
    )

    if not epics:
        print("\nNo Epics found. Please check the filter syntax and your permissions.")
        return data_processor.pd.DataFrame()

    epics_df = data_processor.pd.DataFrame(epics)
    print(f"\nSuccessfully extracted {len(epics_df)} Epics.")

    # --- Step 2: Enrich Release IDs ---
    all_release_ids = set(id for id_list in epics_df['releaseIds'].dropna() for id in id_list)
    if all_release_ids:
        release_titles_map = get_release_titles_map(list(all_release_ids))
        epics_df['releaseTitles'] = epics_df['releaseIds'].apply(
            lambda id_list: [release_titles_map.get(rid, f"ID {rid}") for rid in id_list] if id_list else []
        )
        
        # =================================================================
        # === CHANGE: The following .drop() line has been removed. ===
        # epics_df.drop(columns=['releaseIds'], inplace=True)
        # =================================================================

    # --- Step 3: Enrich Feature IDs ---
    all_feature_ids = set(id for id_list in epics_df['featureIds'].dropna() for id in id_list)
    if all_feature_ids:
        feature_titles_map = get_feature_titles_map(list(all_feature_ids))
        epics_df['featureTitles'] = epics_df['featureIds'].apply(
            lambda id_list: [feature_titles_map.get(fid, f"ID {fid}") for fid in id_list] if id_list else []
        )

        # =================================================================
        # === CHANGE: The following .drop() line has been removed. ===
        # epics_df.drop(columns=['featureIds'], inplace=True)
        # =================================================================

    # --- Step 4: Save the final, fully enriched data ---
    # Re-ordering columns for better readability in the CSV
    # This is optional but makes the output file much nicer.
    desired_order = [
        'id', 'title', 'state', 'ownerId', 'primaryProgramId', 
        'releaseIds', 'releaseTitles', 'featureIds', 'featureTitles'
    ]
    # Filter columns to only those that actually exist in the DataFrame to avoid errors
    final_columns = [col for col in desired_order if col in epics_df.columns]
    epics_df = epics_df[final_columns]
    
    data_processor.save_to_csv(epics_df, "fully_enriched_epics_with_ids.csv")
    return epics_df

# --- Main execution block (no changes needed here) ---
if __name__ == "__main__":
    # PrograsmId map: Sales = 70, Finance = 71, Supply Chain = 72, Workforce = 79
    programs_to_run = [72, 79]
    releases_to_run = [54, 55]
    results_df = run_extraction_pipeline(
        program_ids=programs_to_run,
        release_ids=releases_to_run
    )
    if not results_df.empty:
        print("\n--- Script finished successfully. First 5 rows of fully enriched output: ---")
        print(results_df.head())
