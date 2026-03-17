# epic_extract.py
# this file acts as the main entry point and Orchestracotr, deciding the overall sequence of etsps.
# it calls enrichment to get data and then call data_processor to save data into csv files.

import api_client
import data_processor
# NEW: Import the revised enrichment functions
from enrichment import get_release_titles_map, get_feature_details, get_dependencies_for_features,get_epic_details

def run_extraction_pipeline(program_ids: list, release_ids: list):
    """
    Extracts a relational dataset for Epics, Features, and Dependencies,
    saving them into three separate, linkable CSV files.
    """
    print(f"--- Starting Relational Extraction for Programs: {program_ids} and Releases: {release_ids} ---")

    # === STEP 1: FETCH AND SAVE EPICS ===
    epics_df, epic_column_map = get_epic_details(program_ids, release_ids)
    if epics_df.empty:
        print("\nNo Epics found. Halting process.")
        return
    data_processor.save_to_csv(epics_df, "initiatives_report.csv", column_mapping=epic_column_map)
    print(f"\nSaved {len(epics_df)} Epics to 'initiatives_report.csv'.")

    # === STEP 2: FETCH AND SAVE FEATURES ===
    all_feature_ids = set(id for id_list in epics_df['featureIds'].dropna() for id in id_list)
    if all_feature_ids:
        features_df, feature_column_map = get_feature_details(list(all_feature_ids))
        if not features_df.empty:
            data_processor.save_to_csv(features_df, "epic_features_report.csv", column_mapping=feature_column_map)
            print(f"Saved {len(features_df)} Features to 'features_report.csv'.")
    else:
        print("No child Features found for the extracted Epics.")
        all_feature_ids = set()

    # === STEP 3: FETCH AND SAVE DEPENDENCIES ===
    if all_feature_ids:
        dependencies_df, dependency_column_map = get_dependencies_for_features(list(all_feature_ids))
        if not dependencies_df.empty:
            data_processor.save_to_csv(dependencies_df, "dependencies_report.csv", column_mapping=dependency_column_map)
            print(f"Saved {len(dependencies_df)} Dependencies to 'dependencies_report.csv'.")
    else:
        print("Skipping dependency extraction as no features were found.")
        
    print("\n--- Relational extraction complete. ---")

# --- Main execution block (no changes needed) ---
if __name__ == "__main__":
    # programs_to_run = [72, 79]
    programs_to_run = [72]
    releases_to_run = [54, 55]
    run_extraction_pipeline(
        program_ids=programs_to_run,
        release_ids=releases_to_run
    )
